"""Command: add a new task."""

import json

from utils.paths import get_tasks_file
from utils.validation import validate_description


def add_task(description: str) -> None:
    """Add a new task with the given *description* to the tasks file."""
    validate_description(description)

    filepath = get_tasks_file()

    try:
        with open(filepath, "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []

    tasks.append({"description": description.strip(), "done": False})

    with open(filepath, "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Task added: {description.strip()}")
