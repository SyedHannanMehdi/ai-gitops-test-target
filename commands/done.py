"""Command: mark a task as done."""

import json

from utils.paths import get_tasks_file
from utils.validation import validate_task_file, validate_task_id


def mark_done(task_id: str) -> None:
    """Mark the task with the given ID as done.

    Args:
        task_id: The string representation of the task's integer ID.
    """
    tid = validate_task_id(task_id)

    tasks_file = get_tasks_file()
    validate_task_file(tasks_file)

    with open(tasks_file, "r") as f:
        tasks = json.load(f)

    for task in tasks:
        if task["id"] == tid:
            task["done"] = True
            with open(tasks_file, "w") as f:
                json.dump(tasks, f, indent=2)
            print(f"Task #{tid} marked as done.")
            return

    print(f"Task #{tid} not found.")
