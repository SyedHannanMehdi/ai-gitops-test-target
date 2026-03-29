#!/usr/bin/env node

import { program } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface Task {
  id: number;
  title: string;
  done: boolean;
  createdAt: string;
}

export interface TaskStore {
  tasks: Task[];
  nextId: number;
}

const DATA_FILE = path.join(os.homedir(), '.tasks.json');

export function loadTasks(): TaskStore {
  if (!fs.existsSync(DATA_FILE)) {
    return { tasks: [], nextId: 1 };
  }
  const raw = fs.readFileSync(DATA_FILE, 'utf-8');
  return JSON.parse(raw) as TaskStore;
}

export function saveTasks(store: TaskStore): void {
  fs.writeFileSync(DATA_FILE, JSON.stringify(store, null, 2), 'utf-8');
}

export function outputResult(data: unknown, jsonFlag: boolean): void {
  if (jsonFlag) {
    console.log(JSON.stringify(data, null, 2));
  } else {
    if (Array.isArray(data)) {
      const tasks = data as Task[];
      if (tasks.length === 0) {
        console.log('No tasks found.');
      } else {
        tasks.forEach((t) => {
          const status = t.done ? '[x]' : '[ ]';
          console.log(`${status} #${t.id}: ${t.title}`);
        });
      }
    } else {
      const task = data as Task;
      const status = task.done ? '[x]' : '[ ]';
      console.log(`${status} #${task.id}: ${task.title}`);
    }
  }
}

program
  .name('tasks')
  .description('Simple task manager CLI')
  .version('1.0.0');

// add command
program
  .command('add <title>')
  .description('Add a new task')
  .option('--json', 'Output result as JSON')
  .action((title: string, options: { json?: boolean }) => {
    const store = loadTasks();
    const task: Task = {
      id: store.nextId,
      title,
      done: false,
      createdAt: new Date().toISOString(),
    };
    store.tasks.push(task);
    store.nextId += 1;
    saveTasks(store);

    if (options.json) {
      outputResult(task, true);
    } else {
      console.log(`Added task #${task.id}: ${task.title}`);
    }
  });

// list command
program
  .command('list')
  .description('List all tasks')
  .option('--json', 'Output result as JSON')
  .action((options: { json?: boolean }) => {
    const store = loadTasks();

    if (options.json) {
      outputResult(store.tasks, true);
    } else {
      outputResult(store.tasks, false);
    }
  });

// done command
program
  .command('done <id>')
  .description('Mark a task as done')
  .option('--json', 'Output result as JSON')
  .action((id: string, options: { json?: boolean }) => {
    const store = loadTasks();
    const taskId = parseInt(id, 10);
    const task = store.tasks.find((t) => t.id === taskId);

    if (!task) {
      if (options.json) {
        console.log(JSON.stringify({ error: `Task #${taskId} not found` }, null, 2));
      } else {
        console.error(`Task #${taskId} not found`);
      }
      process.exit(1);
    }

    task.done = true;
    saveTasks(store);

    if (options.json) {
      outputResult(task, true);
    } else {
      console.log(`Marked task #${task.id} as done: ${task.title}`);
    }
  });

program.parse(process.argv);
