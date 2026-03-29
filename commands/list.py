"""Command: list all tasks."""

import json

from utils.paths import get_tasks_file
from utils.validation import validate_task_file


def list_tasks() -> None:
    """Print all tasks from the tasks file."""
    filepath = get_tasks_file()
    validate_task_file(filepath)

    with open(filepath, "r") as f:
        tasks = json.load(f)

    if not tasks:
        print("No tasks found.")
        return

    for i, task in enumerate(tasks, start=1):
        status = "✓" if task.get("done") else "✗"
        print(f"{i}. [{status}] {task['description']}")
