import { loadTasks, saveTasks, outputResult, Task, TaskStore } from '../index';
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import { execSync } from 'child_process';

const DATA_FILE = path.join(os.homedir(), '.tasks.json');

/** Helper: reset the task store before each test */
function resetStore(): void {
  const empty: TaskStore = { tasks: [], nextId: 1 };
  fs.writeFileSync(DATA_FILE, JSON.stringify(empty, null, 2), 'utf-8');
}

/** Helper: run CLI command and return stdout */
function cli(args: string): string {
  return execSync(`ts-node src/index.ts ${args}`, { encoding: 'utf-8' });
}

describe('Task store helpers', () => {
  beforeEach(() => resetStore());
  afterAll(() => {
    if (fs.existsSync(DATA_FILE)) fs.unlinkSync(DATA_FILE);
  });

  it('loadTasks returns empty store when no file exists', () => {
    if (fs.existsSync(DATA_FILE)) fs.unlinkSync(DATA_FILE);
    const store = loadTasks();
    expect(store.tasks).toEqual([]);
    expect(store.nextId).toBe(1);
  });

  it('saveTasks and loadTasks round-trip correctly', () => {
    const store: TaskStore = {
      tasks: [{ id: 1, title: 'Test task', done: false, createdAt: '2024-01-01T00:00:00.000Z' }],
      nextId: 2,
    };
    saveTasks(store);
    const loaded = loadTasks();
    expect(loaded).toEqual(store);
  });
});

describe('outputResult', () => {
  let consoleSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  it('outputs valid JSON for a single task when jsonFlag is true', () => {
    const task: Task = { id: 1, title: 'Hello', done: false, createdAt: '2024-01-01T00:00:00.000Z' };
    outputResult(task, true);
    expect(consoleSpy).toHaveBeenCalledTimes(1);
    const output = consoleSpy.mock.calls[0][0] as string;
    const parsed = JSON.parse(output);
    expect(parsed).toEqual(task);
  });

  it('outputs valid JSON for a task list when jsonFlag is true', () => {
    const tasks: Task[] = [
      { id: 1, title: 'A', done: false, createdAt: '2024-01-01T00:00:00.000Z' },
      { id: 2, title: 'B', done: true, createdAt: '2024-01-02T00:00:00.000Z' },
    ];
    outputResult(tasks, true);
    const output = consoleSpy.mock.calls[0][0] as string;
    const parsed = JSON.parse(output);
    expect(parsed).toEqual(tasks);
  });

  it('outputs empty array as valid JSON when jsonFlag is true', () => {
    outputResult([], true);
    const output = consoleSpy.mock.calls[0][0] as string;
    const parsed = JSON.parse(output);
    expect(parsed).toEqual([]);
  });

  it('outputs human-readable text for a single task when jsonFlag is false', () => {
    const task: Task = { id: 1, title: 'Hello', done: false, createdAt: '2024-01-01T00:00:00.000Z' };
    outputResult(task, false);
    expect(consoleSpy.mock.calls[0][0]).toBe('[ ] #1: Hello');
  });

  it('outputs human-readable text for a done task when jsonFlag is false', () => {
    const task: Task = { id: 2, title: 'Done task', done: true, createdAt: '2024-01-01T00:00:00.000Z' };
    outputResult(task, false);
    expect(consoleSpy.mock.calls[0][0]).toBe('[x] #2: Done task');
  });

  it('outputs "No tasks found." when list is empty and jsonFlag is false', () => {
    outputResult([], false);
    expect(consoleSpy.mock.calls[0][0]).toBe('No tasks found.');
  });

  it('outputs each task on its own line when jsonFlag is false', () => {
    const tasks: Task[] = [
      { id: 1, title: 'A', done: false, createdAt: '2024-01-01T00:00:00.000Z' },
      { id: 2, title: 'B', done: true, createdAt: '2024-01-02T00:00:00.000Z' },
    ];
    outputResult(tasks, false);
    expect(consoleSpy.mock.calls[0][0]).toBe('[ ] #1: A');
    expect(consoleSpy.mock.calls[1][0]).toBe('[x] #2: B');
  });
});

describe('CLI --json flag integration', () => {
  beforeEach(() => resetStore());
  afterAll(() => {
    if (fs.existsSync(DATA_FILE)) fs.unlinkSync(DATA_FILE);
  });

  describe('add --json', () => {
    it('returns valid JSON with the new task', () => {
      const output = cli('add "Buy milk" --json');
      const parsed = JSON.parse(output);
      expect(parsed).toMatchObject({ id: 1, title: 'Buy milk', done: false });
      expect(typeof parsed.createdAt).toBe('string');
    });

    it('assigns incrementing IDs', () => {
      const out1 = cli('add "Task one" --json');
      const out2 = cli('add "Task two" --json');
      expect(JSON.parse(out1).id).toBe(1);
      expect(JSON.parse(out2).id).toBe(2);
    });

    it('returns human-readable output without --json', () => {
      const output = cli('add "Buy milk"');
      expect(output.trim()).toBe('Added task #1: Buy milk');
    });
  });

  describe('list --json', () => {
    it('returns empty array JSON when no tasks exist', () => {
      const output = cli('list --json');
      const parsed = JSON.parse(output);
      expect(parsed).toEqual([]);
    });

    it('returns all tasks as JSON array', () => {
      cli('add "Task one"');
      cli('add "Task two"');
      const output = cli('list --json');
      const parsed = JSON.parse(output) as Task[];
      expect(parsed).toHaveLength(2);
      expect(parsed[0].title).toBe('Task one');
      expect(parsed[1].title).toBe('Task two');
    });

    it('JSON output contains required fields', () => {
      cli('add "Test task"');
      const output = cli('list --json');
      const parsed = JSON.parse(output) as Task[];
      const task = parsed[0];
      expect(task).toHaveProperty('id');
      expect(task).toHaveProperty('title');
      expect(task).toHaveProperty('done');
      expect(task).toHaveProperty('createdAt');
    });

    it('returns human-readable output without --json', () => {
      cli('add "My task"');
      const output = cli('list');
      expect(output.trim()).toBe('[ ] #1: My task');
    });
  });

  describe('done --json', () => {
    it('returns updated task as JSON', () => {
      cli('add "Finish report"');
      const output = cli('done 1 --json');
      const parsed = JSON.parse(output);
      expect(parsed).toMatchObject({ id: 1, title: 'Finish report', done: true });
    });

    it('reflects done=true in list after marking done', () => {
      cli('add "Some task"');
      cli('done 1 --json');
      const listOutput = cli('list --json');
      const tasks = JSON.parse(listOutput) as Task[];
      expect(tasks[0].done).toBe(true);
    });

    it('returns JSON error for non-existent task', () => {
      let output = '';
      try {
        cli('done 999 --json');
      } catch (e: unknown) {
        const err = e as { stdout: string };
        output = err.stdout;
      }
      const parsed = JSON.parse(output);
      expect(parsed).toHaveProperty('error');
      expect(parsed.error).toContain('999');
    });

    it('returns human-readable output without --json', () => {
      cli('add "Write tests"');
      const output = cli('done 1');
      expect(output.trim()).toBe('Marked task #1 as done: Write tests');
    });
  });
});
