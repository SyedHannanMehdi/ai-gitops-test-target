# AI GitOps Test Target — Task Manager CLI

A simple command-line task manager with `--json` output support for scripting and automation.

---

## Installation

```bash
npm install
npm run build
```

---

## Running the CLI

You can run the CLI in three ways:

### 1. Directly with `ts-node` (development)

```bash
npx ts-node src/index.ts <command> [options]
```

### 2. From the compiled build

```bash
node dist/index.js <command> [options]
```

### 3. As a global `tasks` binary

To use the short `tasks` command shown in the examples below, link the package globally:

```bash
npm link
```

After linking, the `tasks` binary will be available on your PATH. You can also install globally from a published package with `npm install -g <package-name>`.

> **Note:** All examples below use the `tasks` shorthand. If you haven't run `npm link`, substitute `npx ts-node src/index.ts` or `node dist/index.js` in place of `tasks`.

---

## Commands

### `add <title>`

Add a new task.

```bash
tasks add "Buy groceries"
# Added: [ ] #1 Buy groceries

tasks add "Buy groceries" --json
```

**JSON output:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "done": false,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

---

### `list`

List all tasks.

```bash
tasks list
# [ ] #1 Buy groceries
# [x] #2 Walk the dog

tasks list --json
```

**JSON output:**
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "done": false,
    "createdAt": "2024-01-01T00:00:00.000Z"
  },
  {
    "id": 2,
    "title": "Walk the dog",
    "done": true,
    "createdAt": "2024-01-01T01:00:00.000Z"
  }
]
```

---

### `done <id>`

Mark a task as done.

```bash
tasks done 1
# Marked done: [x] #1 Buy groceries

tasks done 1 --json
```

**JSON output:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "done": true,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

**Error output (task not found or invalid ID):**
```json
{
  "error": "Task #99 not found"
}
```

---

## JSON Schemas

### Task object

| Field       | Type    | Description                         |
|-------------|---------|-------------------------------------|
| `id`        | number  | Unique integer task ID              |
| `title`     | string  | Task description                    |
| `done`      | boolean | Whether the task is completed       |
| `createdAt` | string  | ISO 8601 creation timestamp         |

### Error object

| Field   | Type   | Description          |
|---------|--------|----------------------|
| `error` | string | Human-readable error |

---

## Scripting Examples

All examples below assume `tasks` is on your PATH (via `npm link` or global install).  
Replace `tasks` with `node dist/index.js` if running from the build directly.

### Add a task and capture its ID

```bash
ID=$(tasks add "Deploy to production" --json | node -e "process.stdin.resume();let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>console.log(JSON.parse(d).id))")
echo "Created task $ID"
```

### List only incomplete tasks

```bash
tasks list --json | node -e "
  process.stdin.resume();
  let d = '';
  process.stdin.on('data', c => d += c);
  process.stdin.on('end', () => {
    const tasks = JSON.parse(d).filter(t => !t.done);
    console.log(JSON.stringify(tasks, null, 2));
  });
"
```

### Mark a task done and check success

```bash
result=$(tasks done 1 --json)
if echo "$result" | grep -q '"error"'; then
  echo "Failed: $result"
else
  echo "Success"
fi
```

---

## Development

```bash
# Run tests
npm test

# Run tests with coverage
npm run coverage

# Build
npm run build
```

---

## Data Storage

Tasks are stored in `~/.tasks.json`. The file is created automatically on first use.
