#!/usr/bin/env python3
"""task-cli: A simple task management CLI."""

import sys
import os
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".config" / "task-cli"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "tasks_file": str(Path.home() / ".config" / "task-cli" / "tasks.json"),
    "default_priority": "medium",
}


def _exit_with_error(message: str) -> None:
    """Print a friendly error message and exit with code 1."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def load_config() -> dict:
    """Load config from CONFIG_PATH, creating it with defaults if missing."""
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        _exit_with_error(
            f"Config file contains invalid YAML: {CONFIG_PATH}\n"
            f"Details: {e}\n"
            f"Fix or delete the file to regenerate defaults."
        )

    if data is None:
        return DEFAULT_CONFIG.copy()

    if not isinstance(data, dict):
        _exit_with_error(
            f"Config file must contain a mapping (YAML object) at the top level: {CONFIG_PATH}\n"
            f"Found {type(data).__name__} instead.\n"
            f"Fix or delete the file to regenerate defaults."
        )

    return {**DEFAULT_CONFIG, **data}


# Load config at startup
config = load_config()

# ---------------------------------------------------------------------------
# Delegate to existing command modules
# ---------------------------------------------------------------------------
try:
    import commands.add as _cmd_add
    import commands.list as _cmd_list
    import commands.done as _cmd_done
    _COMMANDS_AVAILABLE = True
except ImportError:
    _COMMANDS_AVAILABLE = False


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print("Usage: task <command> [options]")
        print("Commands: add, list, done")
        sys.exit(0)

    command = args[0]

    if _COMMANDS_AVAILABLE:
        if command == "add":
            _cmd_add.run(args[1:], config)
        elif command == "list":
            _cmd_list.run(args[1:], config)
        elif command == "done":
            _cmd_done.run(args[1:], config)
        else:
            _exit_with_error(f"Unknown command: {command!r}. Available: add, list, done")
    else:
        _exit_with_error(
            "Command modules not found. Ensure the 'commands/' directory is present."
        )


if __name__ == "__main__":
    main()
