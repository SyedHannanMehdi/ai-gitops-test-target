#!/usr/bin/env python3
"""task-cli: A simple task management CLI."""

import sys
import os
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Config constants
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".config" / "task-cli"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "tasks_file": "~/.config/task-cli/tasks.json",
}


def _exit_with_error(message: str) -> None:
    """Print a friendly error message and exit with code 1."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def load_config() -> dict:
    """Load config from CONFIG_PATH, auto-creating defaults if missing."""
    if not CONFIG_PATH.exists():
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with CONFIG_PATH.open("w") as f:
                yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
            print(
                f"Created default config at {CONFIG_PATH}",
                file=sys.stderr,
            )
        except OSError as exc:
            _exit_with_error(
                f"Could not create config directory/file at {CONFIG_PATH}: {exc}"
            )
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_PATH.open("r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        _exit_with_error(
            f"Config file contains invalid YAML: {CONFIG_PATH}\n"
            f"Details: {exc}\n"
            f"Fix or delete the file to regenerate defaults."
        )

    # An empty file returns None from safe_load
    if data is None:
        return DEFAULT_CONFIG.copy()

    # Validate that the root value is a YAML mapping (dict)
    if not isinstance(data, dict):
        _exit_with_error(
            f"Config file must contain a mapping (YAML object) at the top level: {CONFIG_PATH}\n"
            f"Found {type(data).__name__} instead.\n"
            f"Fix or delete the file to regenerate defaults."
        )

    return {**DEFAULT_CONFIG, **data}


# ---------------------------------------------------------------------------
# Entry-point: delegate to existing command modules
# ---------------------------------------------------------------------------

def main() -> None:
    config = load_config()

    # Resolve tasks_file — support both '~' paths and absolute paths
    tasks_file = Path(config.get("tasks_file", DEFAULT_CONFIG["tasks_file"])).expanduser()

    # Lazy import keeps startup fast and lets tests patch before import
    from commands import add, list_tasks, done  # noqa: F401

    args = sys.argv[1:]

    if not args:
        print("Usage: task <command> [args]")
        print("Commands: add, list, done")
        sys.exit(0)

    command = args[0]

    if command == "add":
        if len(args) < 2:
            _exit_with_error("Usage: task add <description>")
        add.run(tasks_file, args[1:])
    elif command == "list":
        list_tasks.run(tasks_file)
    elif command == "done":
        if len(args) < 2:
            _exit_with_error("Usage: task done <task_id>")
        done.run(tasks_file, args[1])
    else:
        _exit_with_error(f"Unknown command: {command!r}. Valid commands: add, list, done")


if __name__ == "__main__":
    main()
