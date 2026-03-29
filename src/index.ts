#!/usr/bin/env node

import { Command } from "commander";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";

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

export const DATA_FILE = path.join(os.homedir(), ".tasks.json");

export function loadTasks(): TaskStore {
  if (!fs.existsSync(DATA_FILE)) {
    return { tasks: [], nextId: 1 };
  }

  const raw = fs.readFileSync(DATA_FILE, "utf-8");

  // Handle empty or whitespace-only files gracefully
  if (!raw.trim()) {
    return { tasks: [], nextId: 1 };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    console.error(
      `Warning: Failed to parse tasks file at "${DATA_FILE}". Using an empty task store instead.`
    );
    return { tasks: [], nextId: 1 };
  }

  if (!parsed || typeof parsed !== "object") {
    console.error(
      `Warning: Tasks file at "${DATA_FILE}" has an invalid format. Using an empty task store instead.`
    );
    return { tasks: [], nextId: 1 };
  }

  const store = parsed as Partial<TaskStore>;

  if (!Array.isArray(store.tasks) || typeof store.nextId !== "number") {
    console.error(
      `Warning: Tasks file at "${DATA_FILE}" is missing required fields. Using an empty task store instead.`
    );
    return { tasks: [], nextId: 1 };
  }

  return { tasks: store.tasks, nextId: store.nextId };
}

export function saveTasks(store: TaskStore): void {
  fs.writeFileSync(DATA_FILE, JSON.stringify(store, null, 2), "utf-8");
}

export function formatTask(task: Task): string {
  const status = task.done ? "[x]" : "[ ]";
  return `${status} #${task.id} ${task.title} (created: ${task.createdAt})`;
}

const program = new Command();

program
  .name("tasks")
  .description("A simple CLI task manager with optional JSON output")
  .version("1.0.0");

// add command
program
  .command("add <title>")
  .description("Add a new task")
  .option("--json", "Output result as JSON")
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
      console.log(JSON.stringify(task, null, 2));
    } else {
      console.log(`Added: ${formatTask(task)}`);
    }
  });

// list command
program
  .command("list")
  .description("List all tasks")
  .option("--json", "Output result as JSON")
  .action((options: { json?: boolean }) => {
    const store = loadTasks();

    if (options.json) {
      console.log(JSON.stringify(store.tasks, null, 2));
    } else {
      if (store.tasks.length === 0) {
        console.log("No tasks found.");
      } else {
        store.tasks.forEach((task) => console.log(formatTask(task)));
      }
    }
  });

// done command
program
  .command("done <id>")
  .description("Mark a task as done by ID")
  .option("--json", "Output result as JSON")
  .action((id: string, options: { json?: boolean }) => {
    const taskId = parseInt(id, 10);

    if (!Number.isInteger(taskId) || isNaN(taskId)) {
      const errorMessage = `Invalid task id "${id}", must be an integer`;
      if (options.json) {
        console.log(JSON.stringify({ error: errorMessage }, null, 2));
      } else {
        console.error(errorMessage);
      }
      process.exit(1);
    }

    const store = loadTasks();
    const task = store.tasks.find((t) => t.id === taskId);

    if (!task) {
      const errorMessage = `Task #${taskId} not found`;
      if (options.json) {
        console.log(JSON.stringify({ error: errorMessage }, null, 2));
      } else {
        console.error(errorMessage);
      }
      process.exit(1);
    }

    task.done = true;
    saveTasks(store);

    if (options.json) {
      console.log(JSON.stringify(task, null, 2));
    } else {
      console.log(`Marked done: ${formatTask(task)}`);
    }
  });

program.parse(process.argv);
