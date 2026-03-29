#!/usr/bin/env node

import { Command } from "commander";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

const program = new Command();

const TODO_FILE = path.join(os.homedir(), ".todos.json");

interface Todo {
  id: number;
  text: string;
  done: boolean;
  createdAt: string;
}

function loadTodos(): Todo[] {
  if (!fs.existsSync(TODO_FILE)) {
    return [];
  }
  try {
    const data = fs.readFileSync(TODO_FILE, "utf-8");
    return JSON.parse(data) as Todo[];
  } catch {
    return [];
  }
}

function saveTodos(todos: Todo[]): void {
  fs.writeFileSync(TODO_FILE, JSON.stringify(todos, null, 2), "utf-8");
}

function outputResult(data: unknown, jsonMode: boolean): void {
  if (jsonMode) {
    console.log(JSON.stringify(data, null, 2));
  }
}

program
  .name("todo")
  .description("A simple CLI todo manager")
  .version("1.0.0");

// ADD command
program
  .command("add <text>")
  .description("Add a new todo item")
  .option("--json", "Output result as JSON")
  .action((text: string, options: { json?: boolean }) => {
    const todos = loadTodos();
    const newTodo: Todo = {
      id: todos.length > 0 ? Math.max(...todos.map((t) => t.id)) + 1 : 1,
      text,
      done: false,
      createdAt: new Date().toISOString(),
    };
    todos.push(newTodo);
    saveTodos(todos);

    if (options.json) {
      outputResult({ success: true, todo: newTodo }, true);
    } else {
      console.log(`Added: "${text}" (id: ${newTodo.id})`);
    }
  });

// LIST command
program
  .command("list")
  .description("List all todo items")
  .option("--json", "Output result as JSON")
  .action((options: { json?: boolean }) => {
    const todos = loadTodos();

    if (options.json) {
      outputResult({ todos }, true);
    } else {
      if (todos.length === 0) {
        console.log("No todos found.");
        return;
      }
      todos.forEach((todo) => {
        const status = todo.done ? "[x]" : "[ ]";
        console.log(`${status} ${todo.id}. ${todo.text}`);
      });
    }
  });

// DONE command
program
  .command("done <id>")
  .description("Mark a todo item as done")
  .option("--json", "Output result as JSON")
  .action((idStr: string, options: { json?: boolean }) => {
    const id = parseInt(idStr, 10);
    if (isNaN(id)) {
      if (options.json) {
        outputResult({ success: false, error: "Invalid id provided" }, true);
      } else {
        console.error("Error: Invalid id provided.");
      }
      process.exit(1);
    }

    const todos = loadTodos();
    const todo = todos.find((t) => t.id === id);

    if (!todo) {
      if (options.json) {
        outputResult({ success: false, error: `Todo with id ${id} not found` }, true);
      } else {
        console.error(`Error: Todo with id ${id} not found.`);
      }
      process.exit(1);
    }

    todo.done = true;
    saveTodos(todos);

    if (options.json) {
      outputResult({ success: true, todo }, true);
    } else {
      console.log(`Marked as done: "${todo.text}" (id: ${todo.id})`);
    }
  });

program.parse(process.argv);
