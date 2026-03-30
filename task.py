#!/usr/bin/env python3
"""
task-cli: A simple task management CLI tool.
"""

import sys
import os
import argparse
import yaml
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "task-cli"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "storage": {
        "path": str(Path.home() / ".local" / "share" / "task-cli" / "tasks.json"),
    },
    "display": {
        "date_format": "%Y-%m-%d",
        "show_completed": False,
    },
    "defaults": {
        "priority": "medium",
    },
}


def load_config() -> dict:
    """Load configuration from file, creating defaults if missing."""
    if not CONFIG_PATH.exists():
        print(
            f"[task-cli] Config file not found at {CONFIG_PATH}. "
            "Creating default configuration...",
            file=sys.stderr,
        )
        create_default_config()

    try:
        with open(CONFIG_PATH) as f:
            loaded = yaml.safe_load(f) or {}
        # Merge loaded config on top of defaults so missing keys are filled in
        config = _deep_merge(DEFAULT_CONFIG, loaded)
        return config
    except yaml.YAMLError as exc:
        print(
            f"[task-cli] Error: Config file {CONFIG_PATH} contains invalid YAML.\n"
            f"  Details: {exc}\n"
            "  Fix the file manually or delete it to regenerate defaults.",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as exc:
        print(
            f"[task-cli] Error: Could not read config file {CONFIG_PATH}.\n"
            f"  Details: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)


def create_default_config() -> None:
    """Create the config directory and write the default config file."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        print(
            f"[task-cli] Default config written to {CONFIG_PATH}.",
            file=sys.stderr,
        )
    except OSError as exc:
        print(
            f"[task-cli] Error: Could not create default config at {CONFIG_PATH}.\n"
            f"  Details: {exc}\n"
            "  Continuing with in-memory defaults.",
            file=sys.stderr,
        )


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_list(config: dict, args: argparse.Namespace) -> None:
    """List tasks."""
    storage_path = Path(config["storage"]["path"])
    if not storage_path.exists():
        print("No tasks found.")
        return

    import json
    try:
        with open(storage_path) as f:
            tasks = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[task-cli] Error reading tasks: {exc}", file=sys.stderr)
        sys.exit(1)

    show_completed = config["display"].get("show_completed", False)
    date_fmt = config["display"].get("date_format", "%Y-%m-%d")

    filtered = [t for t in tasks if show_completed or not t.get("completed", False)]
    if not filtered:
        print("No tasks to display.")
        return

    for task in filtered:
        status = "✓" if task.get("completed") else "○"
        due = task.get("due", "")
        print(f"  [{status}] {task.get('id', '?')}. {task.get('title', '')}  {due}")


def cmd_add(config: dict, args: argparse.Namespace) -> None:
    """Add a new task."""
    import json
    import datetime

    storage_path = Path(config["storage"]["path"])
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    tasks = []
    if storage_path.exists():
        try:
            with open(storage_path) as f:
                tasks = json.load(f)
        except (json.JSONDecodeError, OSError):
            tasks = []

    new_task = {
        "id": len(tasks) + 1,
        "title": args.title,
        "priority": getattr(args, "priority", None) or config["defaults"]["priority"],
        "completed": False,
        "created": datetime.date.today().strftime(config["display"]["date_format"]),
    }
    tasks.append(new_task)

    with open(storage_path, "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Added task #{new_task['id']}: {new_task['title']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task",
        description="A simple task management CLI.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List tasks")

    add_p = sub.add_parser("add", help="Add a task")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        help="Task priority (default: from config)",
    )

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


if __name__ == "__main__":
    main()
