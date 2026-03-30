# task-cli

A simple command-line task manager written in Python.

## Installation

```bash
pip install pyyaml
```

## Usage

```bash
# List tasks
python task.py list

# Add a task
python task.py add "Buy groceries"
python task.py add "Deploy hotfix" --priority high
```

## Configuration

The configuration file lives at:

```
~/.config/task-cli/config.yaml
```

**If the file does not exist**, `task-cli` will automatically create it with
sensible defaults the first time you run any command. You will see a short
notice on stderr:

```
[task-cli] Config file not found at /home/you/.config/task-cli/config.yaml. Creating default configuration...
[task-cli] Default config written to /home/you/.config/task-cli/config.yaml.
```

### Default configuration

```yaml
storage:
  path: ~/.local/share/task-cli/tasks.json

display:
  date_format: "%Y-%m-%d"
  show_completed: false

defaults:
  priority: medium
```

### Options

| Key | Description | Default |
|-----|-------------|---------|
| `storage.path` | Where tasks are stored (JSON) | `~/.local/share/task-cli/tasks.json` |
| `display.date_format` | Python `strftime` format for dates | `%Y-%m-%d` |
| `display.show_completed` | Whether completed tasks are shown in `list` | `false` |
| `defaults.priority` | Priority assigned when `--priority` is omitted | `medium` |

## Running tests

```bash
pip install pytest pyyaml
pytest tests/
```
