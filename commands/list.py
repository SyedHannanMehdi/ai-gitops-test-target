"""Command: list all tasks."""

import json

from utils.paths import get_tasks_file
from utils.validation import validate_task_file


def list_tasks() -> None:
    """List all tasks, showing their ID, status, and description."""
    tasks_file = get_tasks_file()

    validate_task_file(tasks_file)

    with open(tasks_file, "r") as f:
        tasks = json.load(f)

    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        status = "✓" if task.get("done") else "✗"
        print(f"[{status}] #{task['id']}: {task['description']}")
