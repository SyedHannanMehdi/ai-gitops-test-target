import json

from utils.paths import get_tasks_file


def mark_done(task_id: int) -> None:
    """Mark the task with the given stored ID as done.

    Preserves previous behaviour:
    - Prints a friendly message and returns (without raising) when the tasks
      file does not exist.
    - Looks up tasks by their stored ``id`` field, not by list index.
    """
    filepath = get_tasks_file()

    # Preserve previous behaviour: missing file → friendly message, no exception.
    try:
        with open(filepath, "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print("No tasks found.")
        return

    # ID-based lookup — matches the original persistence semantics.
    for task in tasks:
        if task.get("id") == task_id:
            task["done"] = True
            with open(filepath, "w") as f:
                json.dump(tasks, f, indent=2)
            print(f"Task {task_id} marked as done.")
            return

    print(f"Task {task_id} not found.")
