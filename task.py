#!/usr/bin/env python3
"""task-cli: A simple task management CLI."""

import os
import sys
import yaml
import argparse
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "task-cli"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "tasks_file": str(Path.home() / ".config" / "task-cli" / "tasks.json"),
    "default_priority": "medium",
    "date_format": "%Y-%m-%d",
    "editor": os.environ.get("EDITOR", "nano"),
}


def load_config() -> dict:
    """Load configuration from file, creating defaults if missing.

    Returns:
        dict: The loaded (or default) configuration.
    """
    if not CONFIG_PATH.exists():
        _create_default_config()

    try:
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f)
            # yaml.safe_load returns None for an empty file
            if data is None:
                return DEFAULT_CONFIG.copy()
            return {**DEFAULT_CONFIG, **data}
    except yaml.YAMLError as exc:
        _exit_with_error(
            f"Config file is not valid YAML: {CONFIG_PATH}\n"
            f"Details: {exc}\n"
            f"Fix or delete the file to regenerate defaults."
        )
    except OSError as exc:
        _exit_with_error(
            f"Could not read config file: {CONFIG_PATH}\n"
            f"Details: {exc}"
        )


def _create_default_config() -> None:
    """Create the config directory and write a default config file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=True)
        print(
            f"[task-cli] Config file not found — created default config at:\n"
            f"  {CONFIG_PATH}\n"
            f"Edit it to customise your settings.\n"
        )
    except OSError as exc:
        _exit_with_error(
            f"Could not create default config at: {CONFIG_PATH}\n"
            f"Details: {exc}\n"
            f"Check that you have write permission to: {CONFIG_DIR}"
        )


def _exit_with_error(message: str) -> None:
    """Print a friendly error message and exit with code 1."""
    print(f"[task-cli] Error: {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Task operations (stubs kept minimal — extend as needed)
# ---------------------------------------------------------------------------

def cmd_list(config: dict, args: argparse.Namespace) -> None:
    tasks_file = Path(config["tasks_file"])
    if not tasks_file.exists():
        print("No tasks found. Add one with: task.py add <description>")
        return
    import json
    tasks = json.loads(tasks_file.read_text())
    if not tasks:
        print("No tasks found.")
        return
    for idx, task in enumerate(tasks, 1):
        priority = task.get("priority", config["default_priority"])
        print(f"{idx}. [{priority.upper()}] {task['description']}")


def cmd_add(config: dict, args: argparse.Namespace) -> None:
    import json
    tasks_file = Path(config["tasks_file"])
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    tasks = json.loads(tasks_file.read_text()) if tasks_file.exists() else []
    task = {
        "description": " ".join(args.description),
        "priority": args.priority or config["default_priority"],
    }
    tasks.append(task)
    tasks_file.write_text(json.dumps(tasks, indent=2))
    print(f"Added task: {task['description']}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task",
        description="Simple task management CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List all tasks")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", nargs="+", help="Task description")
    add_parser.add_argument(
        "--priority", "-p",
        choices=["low", "medium", "high"],
        default=None,
        help="Task priority (default: from config)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    config = load_config()

    dispatch = {
        "list": cmd_list,
        "add": cmd_add,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        _exit_with_error(f"Unknown command: {args.command}")

    handler(config, args)


if __name__ == "__main__":
    main()
