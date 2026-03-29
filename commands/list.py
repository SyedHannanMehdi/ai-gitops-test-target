import json

from utils.paths import get_tasks_file


def list_tasks() -> None:
    """Print all tasks to stdout.

    Prints a friendly message and returns (without raising) when the tasks
    file does not exist, preserving the previous user-visible behaviour.
    """
    filepath = get_tasks_file()

    # Preserve previous behaviour: missing file → friendly message, no exception.
    try:
        with open(filepath, "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print("No tasks found.")
        return

    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        status = "x" if task.get("done") else " "
        print(f"[{status}] {task['id']}: {task['description']}")
