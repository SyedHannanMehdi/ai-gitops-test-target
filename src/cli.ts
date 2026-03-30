#!/usr/bin/env node

import { Command } from "commander";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

const DATA_FILE = path.join(os.homedir(), ".todo-items.json");

interface TodoItem {
  id: number;
  text: string;
  done: boolean;
  createdAt: string;
}

interface JsonOutput<T = unknown> {
  success: boolean;
  data: T;
  error?: string;
}

function loadItems(): TodoItem[] {
  if (!fs.existsSync(DATA_FILE)) {
    return [];
  }
  try {
    const raw = fs.readFileSync(DATA_FILE, "utf-8");
    return JSON.parse(raw) as TodoItem[];
  } catch {
    return [];
  }
}

function saveItems(items: TodoItem[]): void {
  fs.writeFileSync(DATA_FILE, JSON.stringify(items, null, 2), "utf-8");
}

function outputJson<T>(payload: JsonOutput<T>): void {
  process.stdout.write(JSON.stringify(payload, null, 2) + "\n");
}

const program = new Command();

program
  .name("todo")
  .description("A simple CLI todo manager")
  .version("1.0.0");

// ── add ──────────────────────────────────────────────────────────────────────
program
  .command("add <text>")
  .description("Add a new todo item")
  .option("--json", "Output result as JSON")
  .action((text: string, options: { json?: boolean }) => {
    const items = loadItems();
    const newItem: TodoItem = {
      id: items.length > 0 ? Math.max(...items.map((i) => i.id)) + 1 : 1,
      text,
      done: false,
      createdAt: new Date().toISOString(),
    };
    items.push(newItem);
    saveItems(items);

    if (options.json) {
      outputJson<TodoItem>({ success: true, data: newItem });
    } else {
      console.log(`Added: [${newItem.id}] ${newItem.text}`);
    }
  });

// ── list ─────────────────────────────────────────────────────────────────────
program
  .command("list")
  .description("List all todo items")
  .option("--json", "Output result as JSON")
  .action((options: { json?: boolean }) => {
    const items = loadItems();

    if (options.json) {
      outputJson<TodoItem[]>({ success: true, data: items });
    } else {
      if (items.length === 0) {
        console.log("No todo items found.");
        return;
      }
      items.forEach((item) => {
        const status = item.done ? "[x]" : "[ ]";
        console.log(`${status} [${item.id}] ${item.text}`);
      });
    }
  });

// ── done ─────────────────────────────────────────────────────────────────────
program
  .command("done <id>")
  .description("Mark a todo item as done")
  .option("--json", "Output result as JSON")
  .action((idStr: string, options: { json?: boolean }) => {
    const id = parseInt(idStr, 10);

    if (isNaN(id)) {
      if (options.json) {
        outputJson({ success: false, data: null, error: "Invalid ID provided" });
      } else {
        console.error("Error: Invalid ID provided");
      }
      process.exit(1);
    }

    const items = loadItems();
    const item = items.find((i) => i.id === id);

    if (!item) {
      if (options.json) {
        outputJson({
          success: false,
          data: null,
          error: `Todo item with ID ${id} not found`,
        });
      } else {
        console.error(`Error: Todo item with ID ${id} not found`);
      }
      process.exit(1);
    }

    item.done = true;
    saveItems(items);

    if (options.json) {
      outputJson<TodoItem>({ success: true, data: item });
    } else {
      console.log(`Done: [${item.id}] ${item.text}`);
    }
  });

program.parse(process.argv);
