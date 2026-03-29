"""Command: mark a task as done."""

import json

from utils.paths import get_tasks_file
from utils.validation import validate_task_file, validate_task_id


def mark_done(task_id: int) -> None:
    """Mark the task identified by *task_id* as done."""
    filepath = get_tasks_file()
    validate_task_file(filepath)

    with open(filepath, "r") as f:
        tasks = json.load(f)

    validate_task_id(task_id, tasks)

    task = tasks[task_id - 1]
    task["done"] = True

    with open(filepath, "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Task {task_id} marked as done: {task['description']}")
