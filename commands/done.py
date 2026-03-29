import json
import os

from utils.paths import get_tasks_file
from utils.validation import validate_task_id


def mark_done(task_id: int) -> None:
    """Mark the task identified by *task_id* (its stored ``id`` field) as done.

    Prints a friendly message when the tasks file is missing rather than
    raising an exception — preserving the original UX.  Task lookup uses the
    stored ``id`` field, not the list index, to preserve persistence semantics.
    """
    filepath = get_tasks_file()

    # Non-exceptional handling for a missing file (original behaviour).
    if not os.path.exists(filepath):
        print("No tasks found.")
        return

    with open(filepath, "r") as f:
        tasks = json.load(f)

    # Validate that the requested id actually exists.
    validate_task_id(task_id, tasks)

    # Update the matching task by its stored id (not by list index).
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            break

    with open(filepath, "w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Task {task_id} marked as done.")
