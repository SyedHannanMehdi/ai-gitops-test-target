# ai-gitops-test-target

A simple file-backed CLI task manager with `--json` output for scripting and automation.

---

## Installation

```bash
npm install
npm run build        # compiles TypeScript → dist/
```

---

## Running the CLI

There are three ways to invoke the task manager:

### 1. After building (recommended for production use)

```bash
node dist/index.js <command> [options]
```

### 2. Directly with ts-node (no build step required)

```bash
npx ts-node src/index.ts <command> [options]
```

### 3. As a global `tasks` binary

If you want to use the short `tasks` alias, link the package globally first:

```bash
npm link          # or: npm install -g .
```

Then you can call:

```bash
tasks <command> [options]
```

> **Note:** Without `npm link` / `npm install -g`, the `tasks` binary is not on your PATH.
> Use `node dist/index.js …` or `npx ts-node src/index.ts …` instead.

---

## Commands

| Command | Description |
|---------|-------------|
| `add <title>` | Add a new task |
| `list` | List all tasks |
| `done <id>` | Mark task `<id>` as done |

Every command accepts a `--json` flag for machine-readable output.

---

## Usage examples

### Plain text output

```bash
# After npm link / npm install -g
tasks add "Write unit tests"
tasks list
tasks done 1

# Without global install
node dist/index.js add "Write unit tests"
node dist/index.js list
node dist/index.js done 1
```

### JSON output (`--json`)

```bash
node dist/index.js add "Deploy to staging" --json
# {
#   "id": 1,
#   "title": "Deploy to staging",
#   "done": false,
#   "createdAt": "2024-01-15T10:30:00.000Z"
# }

node dist/index.js list --json
# [
#   { "id": 1, "title": "Deploy to staging", "done": false, "createdAt": "..." }
# ]

node dist/index.js done 1 --json
# {
#   "id": 1,
#   "title": "Deploy to staging",
#   "done": true,
#   "createdAt": "..."
# }
```

### Scripting example (bash)

```bash
# Add a task and capture its id
TASK=$(node dist/index.js add "Run smoke tests" --json)
ID=$(echo "$TASK" | node -e "process.stdin.resume();let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>console.log(JSON.parse(d).id))")

# Mark it done
node dist/index.js done "$ID" --json
```

---

## JSON schemas

### Task object

```jsonc
{
  "id":        1,           // integer — unique task identifier
  "title":     "string",    // task description
  "done":      false,       // boolean — completion status
  "createdAt": "ISO 8601"   // creation timestamp
}
```

### Error object (non-zero exit)

```jsonc
{
  "error": "Human-readable error message"
}
```

---

## Development

```bash
npm test            # run Jest test suite
npm run coverage    # run tests with coverage report
npm run build       # compile TypeScript
```

Data is stored in `~/.tasks.json`.
