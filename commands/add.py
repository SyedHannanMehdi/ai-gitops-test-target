"""Command to add a new task."""

from utils.paths import get_tasks_file
from utils.validation import validate_description


def add_task(description: str) -> None:
    """Add a new task with the given description.

    Args:
        description: The description for the new task.

    Raises:
        ValueError: If the description is empty.
    """
    validate_description(description)

    tasks_file = get_tasks_file()

    with open(tasks_file, "a") as f:
        f.write(f"{description.strip()}\n")

    print(f"Task added: {description.strip()}")
