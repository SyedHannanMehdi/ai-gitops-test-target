# task-cli

A simple command-line task manager.

## Installation

```bash
pip install pyyaml
```

## Usage

```bash
python task.py add "Buy groceries"
python task.py list
python task.py done 1
```

## Configuration

task-cli reads its configuration from:

```
~/.config/task-cli/config.yaml
```

If the file does not exist, it is **auto-created** the first time you run any command.

### Default configuration

```yaml
tasks_file: ~/.config/task-cli/tasks.json
```

> **Note:** The `tasks_file` value is stored as written above (using `~` for the home directory). It is expanded to an absolute path at runtime, so you can use either `~`-prefixed or absolute paths in your own config.

### Configuration keys

| Key | Default | Description |
|-----|---------|-------------|
| `tasks_file` | `~/.config/task-cli/tasks.json` | Path to the JSON file where tasks are stored. Supports `~` expansion. |

### Error-handling matrix

| Situation | Behaviour |
|-----------|-----------|
| Config file missing | Auto-created with defaults; a notice is printed to stderr. |
| Config file is empty | Defaults are used silently. |
| Config file has invalid YAML | Error message printed to stderr; exit code 1. |
| Config root is not a YAML mapping | Error message printed to stderr; exit code 1. |
| Config file unreadable (permissions) | OS error message printed to stderr; exit code 1. |

## Commands

| Command | Description |
|---------|-------------|
| `task add <description>` | Add a new task. |
| `task list` | List all tasks. |
| `task done <id>` | Mark a task as done. |
