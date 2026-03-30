"""Command to list all tasks."""

from utils.paths import get_tasks_file
from utils.validation import validate_task_file


def list_tasks() -> None:
    """List all tasks from the tasks file.

    Raises:
        FileNotFoundError: If the tasks file does not exist.
    """
    tasks_file = get_tasks_file()
    validate_task_file(tasks_file)

    with open(tasks_file, "r") as f:
        lines = f.readlines()

    if not lines:
        print("No tasks found.")
        return

    for index, line in enumerate(lines, start=1):
        task = line.strip()
        if task:
            print(f"{index}. {task}")
