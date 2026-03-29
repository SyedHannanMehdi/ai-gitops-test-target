#!/usr/bin/env python3
"""task-cli: A simple task management CLI."""

import os
import sys
import yaml
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".config" / "task-cli"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "storage": str(Path.home() / ".local" / "share" / "task-cli" / "tasks.json"),
    "default_priority": "medium",
    "date_format": "%Y-%m-%d",
}


def load_config() -> dict:
    """Load configuration from disk, creating defaults if the file is missing.

    Returns:
        A dict containing the merged configuration (defaults + user overrides).

    Raises:
        SystemExit: If the config directory cannot be created or the file
                    cannot be written.
    """
    if not CONFIG_PATH.exists():
        _create_default_config()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        _exit_with_error(
            f"Config file '{CONFIG_PATH}' contains invalid YAML: {exc}\n"
            f"Please fix or delete it and re-run to generate fresh defaults."
        )
    except OSError as exc:
        _exit_with_error(f"Cannot read config file '{CONFIG_PATH}': {exc}")

    # Merge: defaults first, then user values override
    config = {**DEFAULT_CONFIG, **user_config}
    return config


def _create_default_config() -> None:
    """Create the config directory and write default config.yaml."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=True)
        print(
            f"[task-cli] Config file not found — created default config at:\n"
            f"  {CONFIG_PATH}\n"
            f"Edit it to customise your setup.\n",
            file=sys.stderr,
        )
    except OSError as exc:
        _exit_with_error(
            f"Could not create default config at '{CONFIG_PATH}': {exc}\n"
            f"Check that you have write permission to '{CONFIG_DIR}'."
        )


def _exit_with_error(message: str) -> None:
    """Print a friendly error message and exit with code 1."""
    print(f"[task-cli] ERROR: {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Task operations (stubs — extend as needed)
# ---------------------------------------------------------------------------

def cmd_list(config: dict, args: argparse.Namespace) -> None:
    storage = config.get("storage", DEFAULT_CONFIG["storage"])
    if not Path(storage).exists():
        print("No tasks found. Use 'task.py add <title>' to create one.")
        return
    with open(storage, "r", encoding="utf-8") as f:
        import json
        tasks = json.load(f)
    if not tasks:
        print("No tasks found.")
    else:
        for i, task in enumerate(tasks, 1):
            priority = task.get("priority", config.get("default_priority", "medium"))
            print(f"  {i}. [{priority}] {task.get('title', '<untitled>')}")


def cmd_add(config: dict, args: argparse.Namespace) -> None:
    import json
    storage = Path(config.get("storage", DEFAULT_CONFIG["storage"]))
    storage.parent.mkdir(parents=True, exist_ok=True)
    tasks = []
    if storage.exists():
        with open(storage, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    tasks.append({
        "title": " ".join(args.title),
        "priority": config.get("default_priority", "medium"),
    })
    with open(storage, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
    print(f"Added task: {' '.join(args.title)}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task.py",
        description="A simple task management CLI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all tasks")

    add_parser = sub.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", nargs="+", help="Task title")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config()

    if args.command == "list":
        cmd_list(config, args)
    elif args.command == "add":
        cmd_add(config, args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
