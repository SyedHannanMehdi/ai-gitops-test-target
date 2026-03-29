# task-cli

A simple command-line task manager written in Python.

## Installation

```bash
pip install pyyaml
```

## Usage

```bash
# List all tasks
python task.py list

# Add a task
python task.py add Buy groceries
python task.py add --priority high Fix production bug
```

## Configuration

task-cli stores its configuration at:

```
~/.config/task-cli/config.yaml
```

**If the file does not exist, task-cli will create it automatically** with sensible
defaults the first time you run any command. You will see a one-time informational
message telling you where the file was created.

### Default configuration

```yaml
date_format: '%Y-%m-%d'
default_priority: medium
editor: nano          # or the value of $EDITOR
tasks_file: ~/.config/task-cli/tasks.json
```

### Configuration options

| Key | Default | Description |
|-----|---------|-------------|
| `tasks_file` | `~/.config/task-cli/tasks.json` | Path where tasks are stored |
| `default_priority` | `medium` | Priority used when `--priority` is omitted (`low`, `medium`, `high`) |
| `date_format` | `%Y-%m-%d` | `strftime` format for displaying dates |
| `editor` | `$EDITOR` or `nano` | Editor launched for long-form task descriptions |

## Error handling

| Situation | Behaviour |
|-----------|-----------|
| Config file missing | Created automatically with defaults; one-time message printed |
| Config file is empty | Defaults used silently |
| Config file contains invalid YAML | Friendly error printed; exit code 1 |
| Config directory not writable | Friendly error printed; exit code 1 |

## Running tests

```bash
pip install pytest pyyaml
pytest tests/
```
