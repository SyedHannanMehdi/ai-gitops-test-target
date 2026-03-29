import json
import os

from utils.paths import get_tasks_file
from utils.validation import validate_task_file


def list_tasks() -> None:
    """Print all tasks to stdout.

    If the tasks file does not exist a friendly message is printed and the
    command returns without error — preserving the original UX.
    """
    filepath = get_tasks_file()

    # Non-exceptional handling for a missing file (original behaviour).
    if not os.path.exists(filepath):
        print("No tasks found.")
        return

    with open(filepath, "r") as f:
        tasks = json.load(f)

    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        status = "x" if task.get("done") else " "
        print(f"[{status}] {task['id']}: {task['description']}")
