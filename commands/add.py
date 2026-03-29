"""Command: add a new task."""

import json
import os

from utils.paths import get_tasks_file
from utils.validation import validate_description


def add_task(description: str) -> None:
    """Add a new task with the given description.

    Args:
        description: The task description to add.
    """
    validate_description(description)

    tasks_file = get_tasks_file()

    if os.path.exists(tasks_file):
        with open(tasks_file, "r") as f:
            tasks = json.load(f)
    else:
        tasks = []

    task = {
        "id": len(tasks) + 1,
        "description": description.strip(),
        "done": False,
    }
    tasks.append(task)

    with open(tasks_file, "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Added task #{task['id']}: {task['description']}")
