# ai-gitops-test-target

A simple CLI todo manager built with TypeScript and Commander.js.

## Installation

```bash
npm install
npm run build
```

## Usage

### Add a todo

```bash
todo add "Buy groceries"
# Added: "Buy groceries" (id: 1)
```

### List todos

```bash
todo list
# [ ] 1. Buy groceries
# [x] 2. Write tests
```

### Mark a todo as done

```bash
todo done 1
# Marked as done: "Buy groceries" (id: 1)
```

---

## JSON Output (`--json` flag)

All commands support the `--json` flag for machine-readable output, ideal for scripting and automation.

### `add --json`

```bash
todo add "Buy groceries" --json
```

```json
{
  "success": true,
  "todo": {
    "id": 1,
    "text": "Buy groceries",
    "done": false,
    "createdAt": "2024-01-15T10:30:00.000Z"
  }
}
```

### `list --json`

```bash
todo list --json
```

```json
{
  "todos": [
    {
      "id": 1,
      "text": "Buy groceries",
      "done": false,
      "createdAt": "2024-01-15T10:30:00.000Z"
    },
    {
      "id": 2,
      "text": "Write tests",
      "done": true,
      "createdAt": "2024-01-15T10:31:00.000Z"
    }
  ]
}
```

### `done --json`

```bash
todo done 1 --json
```

```json
{
  "success": true,
  "todo": {
    "id": 1,
    "text": "Buy groceries",
    "done": true,
    "createdAt": "2024-01-15T10:30:00.000Z"
  }
}
```

### Error responses (with `--json`)

When an error occurs with `--json` enabled, the output will be:

```json
{
  "success": false,
  "error": "Todo with id 99 not found"
}
```

---

## Scripting Examples

### Get the ID of a newly added todo

```bash
ID=$(todo add "Deploy to production" --json | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8'); console.log(JSON.parse(d).todo.id)")
echo "Created todo with id: $ID"
```

### Count pending todos

```bash
todo list --json | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8'); const t=JSON.parse(d).todos; console.log(t.filter(x=>!x.done).length + ' pending')"
```

### Mark all todos as done in a script

```bash
for id in $(todo list --json | node -e "const d=require('fs').readFileSync('/dev/stdin','utf8'); JSON.parse(d).todos.forEach(t=>console.log(t.id))"); do
  todo done $id --json
done
```

---

## Development

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build
npm run build

# Run in dev mode (no build needed)
npm run dev -- add "Hello world"
```

## Todo Schema

| Field       | Type      | Description                        |
|-------------|-----------|-----------------------------------|
| `id`        | `number`  | Unique auto-incrementing ID        |
| `text`      | `string`  | The todo description               |
| `done`      | `boolean` | Whether the todo is completed      |
| `createdAt` | `string`  | ISO 8601 creation timestamp        |
