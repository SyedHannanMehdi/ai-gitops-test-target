# task-cli

A simple command-line task manager.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python task.py add "Buy groceries"
python task.py list
python task.py done 1
```

## Configuration

task-cli stores its configuration at:

```
~/.config/task-cli/config.yaml
```

If the file does not exist, it is **automatically created** with sensible defaults on first run.

### Default configuration

```yaml
tasks_file: /home/<your-username>/.config/task-cli/tasks.json
default_priority: medium
```

> **Note:** `tasks_file` is written as an absolute path (e.g. `/home/alice/.config/task-cli/tasks.json`).
> The `~` shorthand is **not** used in the generated file so that the path is unambiguous across tools.

### Configuration keys

| Key | Default (expanded) | Description |
|-----|--------------------|-------------|
| `tasks_file` | `$HOME/.config/task-cli/tasks.json` | Where tasks are stored |
| `default_priority` | `medium` | Priority assigned to new tasks when none is specified |

### Error handling

| Situation | Behaviour |
|-----------|-----------|
| Config file missing | Auto-created with defaults; execution continues normally |
| Config file is empty | Defaults are used; execution continues normally |
| Config file contains invalid YAML | Friendly error message printed to stderr; exit code 1 |
| Config file root is not a YAML mapping | Friendly error message printed to stderr; exit code 1 |
| Unknown CLI command | Friendly error message printed to stderr; exit code 1 |
