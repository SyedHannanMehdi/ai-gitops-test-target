# ai-gitops-test-target

A simple CLI task manager written in TypeScript with `--json` output support for scripting and automation.

---

## Installation

```bash
npm install
npm run build
```

---

## Usage

You can run the CLI in three ways:

### 1. During development (via ts-node)
```bash
npx ts-node src/index.ts <command> [options]
```

### 2. After building (via Node.js)
```bash
node dist/index.js <command> [options]
```

### 3. As a global `tasks` command

To use the short `tasks` command directly in your terminal, install the package globally or link it locally:

```bash
# Option A: link locally (recommended for development)
npm link

# Option B: install globally from a published package
npm install -g ai-gitops-test-target
```

After linking/installing, the `tasks` binary will be available on your PATH.

---

## Commands

### `add <title>`

Add a new task.

```bash
tasks add "Buy groceries"
# or without global install:
node dist/index.js add "Buy groceries"
```

### `list`

List all tasks.

```bash
tasks list
# or:
node dist/index.js list
```

### `done <id>`

Mark a task as done by its integer ID.

```bash
tasks done 1
# or:
node dist/index.js done 1
```

---

## JSON Output (`--json`)

Every command supports a `--json` flag that prints structured JSON to stdout, making it easy to use in scripts and pipelines.

### `add --json`

```bash
tasks add "Deploy to production" --json
```

Output schema:

```json
{
  "id": 1,
  "title": "Deploy to production",
  "done": false,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

### `list --json`

```bash
tasks list --json
```

Output schema:

```json
[
  {
    "id": 1,
    "title": "Deploy to production",
    "done": false,
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
]
```

### `done --json`

```bash
tasks done 1 --json
```

Output schema (updated task):

```json
{
  "id": 1,
  "title": "Deploy to production",
  "done": true,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

Error schema (task not found or invalid ID):

```json
{
  "error": "Task #99 not found"
}
```

---

## Scripting Examples

All examples below assume `tasks` is on your PATH (via `npm link` or global install). Replace `tasks` with `node dist/index.js` if running locally without linking.

### Add a task and capture its ID

```bash
TASK_ID=$(tasks add "Run tests" --json | jq -r '.id')
echo "Created task $TASK_ID"
```

### List only incomplete tasks

```bash
tasks list --json | jq '[.[] | select(.done == false)]'
```

### Mark a task done in a script

```bash
tasks done "$TASK_ID" --json | jq '.done'
```

### Check for errors

```bash
result=$(tasks done 999 --json)
if echo "$result" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $(echo "$result" | jq -r '.error')"
fi
```

---

## Data Storage

Tasks are stored in `~/.tasks.json`. The file is created automatically on first use.

If the file is missing, empty, or corrupted, the CLI will emit a warning and fall back to an empty task store rather than crashing.

---

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run tests with coverage
npm run coverage

# Build TypeScript
npm run build
```

---

## License

MIT
