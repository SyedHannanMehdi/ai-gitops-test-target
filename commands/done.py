"""Command to mark a task as done."""

from utils.paths import get_tasks_file
from utils.validation import validate_task_file, validate_task_id


def mark_done(task_id: str) -> None:
    """Mark the task with the given ID as done (removes it from the list).

    Args:
        task_id: The 1-based index of the task to mark as done.

    Raises:
        ValueError: If the task ID is not a valid positive integer or out of range.
        FileNotFoundError: If the tasks file does not exist.
    """
    tid = validate_task_id(task_id)

    tasks_file = get_tasks_file()
    validate_task_file(tasks_file)

    with open(tasks_file, "r") as f:
        lines = f.readlines()

    tasks = [line for line in lines if line.strip()]

    if tid > len(tasks):
        raise ValueError(
            f"Task ID {tid} is out of range. There are only {len(tasks)} task(s)."
        )

    completed_task = tasks.pop(tid - 1).strip()

    with open(tasks_file, "w") as f:
        f.writelines(tasks)

    print(f"Task {tid} marked as done: {completed_task}")
