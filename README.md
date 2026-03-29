# task-cli

A simple task management CLI written in Python.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# List all tasks
python task.py list

# Add a task
python task.py add Buy milk
```

## Configuration

Configuration is stored at `~/.config/task-cli/config.yaml`.

If the file does **not** exist, `task-cli` will automatically create it with
sensible defaults the first time you run any command — no manual setup needed.

### Default config

```yaml
date_format: '%Y-%m-%d'
default_priority: medium
storage: ~/.local/share/task-cli/tasks.json
```

| Key | Description | Default |
|---|---|---|
| `storage` | Path to the JSON file that stores tasks | `~/.local/share/task-cli/tasks.json` |
| `default_priority` | Priority assigned to new tasks (`low` / `medium` / `high`) | `medium` |
| `date_format` | strftime format used when displaying dates | `%Y-%m-%d` |

## Running Tests

```bash
pytest tests/
```
