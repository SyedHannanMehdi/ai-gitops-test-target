# ai-gitops-test-target — Todo CLI

A simple command-line todo manager written in TypeScript.

## Installation

```bash
npm install
npm run build
npm link   # makes `todo` available globally
```

## Usage

### Add a todo item

```bash
todo add "Buy milk"
# Added: [1] Buy milk
```

### List all todo items

```bash
todo list
# [ ] [1] Buy milk
# [ ] [2] Write tests
```

### Mark a todo item as done

```bash
todo done 1
# Done: [1] Buy milk
```

---

## JSON Output (`--json` flag)

All commands support the `--json` flag for machine-readable output. This is useful for scripting and automation pipelines.

The JSON envelope always has the shape:

```json
{
  "success": true | false,
  "data": <command-specific payload>,
  "error": "<message>"   // only present when success is false
}
```

### `add --json`

```bash
todo add "Buy milk" --json
```

```json
{
  "success": true,
  "data": {
    "id": 1,
    "text": "Buy milk",
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
  "success": true,
  "data": [
    {
      "id": 1,
      "text": "Buy milk",
      "done": true,
      "createdAt": "2024-01-15T10:30:00.000Z"
    },
    {
      "id": 2,
      "text": "Write tests",
      "done": false,
      "createdAt": "2024-01-15T11:00:00.000Z"
    }
  ]
}
```

Empty list:

```json
{
  "success": true,
  "data": []
}
```

### `done --json`

```bash
todo done 1 --json
```

```json
{
  "success": true,
  "data": {
    "id": 1,
    "text": "Buy milk",
    "done": true,
    "createdAt": "2024-01-15T10:30:00.000Z"
  }
}
```

#### Error responses

When something goes wrong (e.g. item not found), the process exits with a non-zero code and outputs:

```json
{
  "success": false,
  "data": null,
  "error": "Todo item with ID 99 not found"
}
```

---

## Scripting examples

```bash
# Get the ID of the newly added item
ID=$(todo add "Deploy to prod" --json | node -e "process.stdin.resume();let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>console.log(JSON.parse(d).data.id))")

# Count pending items
todo list --json | node -e "process.stdin.resume();let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>console.log(JSON.parse(d).data.filter(i=>!i.done).length))"

# Use with jq
todo list --json | jq '.data[] | select(.done == false) | .text'
todo add "New task" --json | jq '.data.id'
```

## Development

```bash
npm run build   # compile TypeScript → dist/
npm test        # run Jest test suite
```

## Data storage

Todo items are persisted to `~/.todo-items.json`.
