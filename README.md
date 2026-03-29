# ai-gitops-test-target

A simple task manager CLI with human-readable and JSON output support.

## Installation

```bash
npm install
npm run build
```

## Usage

```bash
# Using ts-node directly
npx ts-node src/index.ts <command> [options]

# Or after building
node dist/index.js <command> [options]
```

## Commands

### `add <title>`

Add a new task.

```bash
# Human-readable output
$ tasks add "Buy groceries"
Added task #1: Buy groceries

# JSON output
$ tasks add "Buy groceries" --json
{
  "id": 1,
  "title": "Buy groceries",
  "done": false,
  "createdAt": "2024-01-15T10:30:00.000Z"
}
```

### `list`

List all tasks.

```bash
# Human-readable output
$ tasks list
[ ] #1: Buy groceries
[x] #2: Write tests
[ ] #3: Deploy to production

# JSON output
$ tasks list --json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "done": false,
    "createdAt": "2024-01-15T10:30:00.000Z"
  },
  {
    "id": 2,
    "title": "Write tests",
    "done": true,
    "createdAt": "2024-01-15T10:31:00.000Z"
  },
  {
    "id": 3,
    "title": "Deploy to production",
    "done": false,
    "createdAt": "2024-01-15T10:32:00.000Z"
  }
]

# Empty list
$ tasks list --json
[]
```

### `done <id>`

Mark a task as done.

```bash
# Human-readable output
$ tasks done 1
Marked task #1 as done: Buy groceries

# JSON output
$ tasks done 1 --json
{
  "id": 1,
  "title": "Buy groceries",
  "done": true,
  "createdAt": "2024-01-15T10:30:00.000Z"
}

# Error (task not found) — JSON output
$ tasks done 999 --json
{
  "error": "Task #999 not found"
}
```

## Options

| Flag     | Description                          | Commands          |
|----------|--------------------------------------|-------------------|
| `--json` | Output result as JSON                | add, list, done   |
| `--help` | Display help for a command           | all               |

## JSON Schema

### Task object

```json
{
  "id": 1,
  "title": "string",
  "done": false,
  "createdAt": "ISO 8601 date string"
}
```

### Error object

```json
{
  "error": "Human-readable error message"
}
```

## Scripting Examples

### Add a task and capture its ID

```bash
ID=$(tasks add "Deploy hotfix" --json | jq -r '.id')
echo "Created task $ID"
```

### List only incomplete tasks

```bash
tasks list --json | jq '[.[] | select(.done == false)]'
```

### Mark all tasks as done

```bash
tasks list --json | jq -r '.[].id' | xargs -I{} tasks done {}
```

### Check if a task exists

```bash
TASK=$(tasks list --json | jq '.[] | select(.id == 1)')
if [ -z "$TASK" ]; then
  echo "Task not found"
fi
```

## Development

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build
npm run build
```

## Data Storage

Tasks are stored in `~/.tasks.json` as a JSON file. The format is:

```json
{
  "tasks": [...],
  "nextId": 4
}
```
