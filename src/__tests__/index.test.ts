import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

const CLI_PATH = path.resolve(__dirname, "../../dist/index.js");
const TODO_FILE = path.join(os.homedir(), ".todos.json");

function runCLI(args: string): { stdout: string; stderr: string; status: number } {
  try {
    const stdout = execSync(`node ${CLI_PATH} ${args}`, {
      encoding: "utf-8",
    });
    return { stdout, stderr: "", status: 0 };
  } catch (err: unknown) {
    const error = err as { stdout?: string; stderr?: string; status?: number };
    return {
      stdout: error.stdout ?? "",
      stderr: error.stderr ?? "",
      status: error.status ?? 1,
    };
  }
}

function clearTodos(): void {
  if (fs.existsSync(TODO_FILE)) {
    fs.writeFileSync(TODO_FILE, JSON.stringify([]), "utf-8");
  }
}

beforeEach(() => {
  clearTodos();
});

afterAll(() => {
  clearTodos();
});

describe("add command", () => {
  it("adds a todo and prints human-readable output", () => {
    const { stdout, status } = runCLI('add "Buy groceries"');
    expect(status).toBe(0);
    expect(stdout).toMatch(/Added: "Buy groceries"/);
  });

  it("adds a todo and outputs valid JSON with --json flag", () => {
    const { stdout, status } = runCLI('add "Buy groceries" --json');
    expect(status).toBe(0);
    const parsed = JSON.parse(stdout);
    expect(parsed.success).toBe(true);
    expect(parsed.todo).toBeDefined();
    expect(parsed.todo.text).toBe("Buy groceries");
    expect(parsed.todo.done).toBe(false);
    expect(parsed.todo.id).toBeDefined();
    expect(parsed.todo.createdAt).toBeDefined();
  });

  it("JSON output contains parseable ISO date", () => {
    const { stdout, status } = runCLI('add "Test date" --json');
    expect(status).toBe(0);
    const parsed = JSON.parse(stdout);
    expect(new Date(parsed.todo.createdAt).toISOString()).toBe(parsed.todo.createdAt);
  });
});

describe("list command", () => {
  it("lists todos in human-readable format", () => {
    runCLI('add "Task one"');
    const { stdout, status } = runCLI("list");
    expect(status).toBe(0);
    expect(stdout).toMatch(/Task one/);
  });

  it("lists todos as valid JSON with --json flag", () => {
    runCLI('add "Task one" --json');
    runCLI('add "Task two" --json');
    const { stdout, status } = runCLI("list --json");
    expect(status).toBe(0);
    const parsed = JSON.parse(stdout);
    expect(Array.isArray(parsed.todos)).toBe(true);
    expect(parsed.todos.length).toBe(2);
    expect(parsed.todos[0].text).toBe("Task one");
    expect(parsed.todos[1].text).toBe("Task two");
  });

  it("returns empty todos array when no todos exist", () => {
    const { stdout, status } = runCLI("list --json");
    expect(status).toBe(0);
    const parsed = JSON.parse(stdout);
    expect(parsed.todos).toEqual([]);
  });
});

describe("done command", () => {
  it("marks a todo as done in human-readable format", () => {
    const addResult = runCLI('add "Finish report" --json');
    const { todo } = JSON.parse(addResult.stdout);
    const { stdout, status } = runCLI(`done ${todo.id}`);
    expect(status).toBe(0);
    expect(stdout).toMatch(/Marked as done: "Finish report"/);
  });

  it("marks a todo as done and outputs valid JSON with --json flag", () => {
    const addResult = runCLI('add "Write tests" --json');
    const { todo } = JSON.parse(addResult.stdout);
    const { stdout, status } = runCLI(`done ${todo.id} --json`);
    expect(status).toBe(0);
    const parsed = JSON.parse(stdout);
    expect(parsed.success).toBe(true);
    expect(parsed.todo.done).toBe(true);
    expect(parsed.todo.id).toBe(todo.id);
    expect(parsed.todo.text).toBe("Write tests");
  });

  it("returns error JSON for non-existent id", () => {
    const { stdout, status } = runCLI("done 9999 --json");
    expect(status).toBe(1);
    const parsed = JSON.parse(stdout);
    expect(parsed.success).toBe(false);
    expect(parsed.error).toMatch(/not found/i);
  });

  it("returns error JSON for invalid id", () => {
    const { stdout, status } = runCLI("done abc --json");
    expect(status).toBe(1);
    const parsed = JSON.parse(stdout);
    expect(parsed.success).toBe(false);
    expect(parsed.error).toMatch(/invalid id/i);
  });
});

describe("JSON output is always valid JSON", () => {
  it("add --json output is parseable", () => {
    const { stdout } = runCLI('add "Parseable test" --json');
    expect(() => JSON.parse(stdout)).not.toThrow();
  });

  it("list --json output is parseable", () => {
    const { stdout } = runCLI("list --json");
    expect(() => JSON.parse(stdout)).not.toThrow();
  });

  it("done --json output is parseable even on error", () => {
    const { stdout } = runCLI("done 99999 --json");
    expect(() => JSON.parse(stdout)).not.toThrow();
  });
});
