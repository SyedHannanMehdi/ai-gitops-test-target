import json
import os


def validate_description(description: str) -> str:
    """Validate and normalize a task description.

    The description must be non-empty (after stripping whitespace) and no longer
    than 200 characters.

    Returns the stripped description string.

    Raises:
        ValueError: if the description is empty or exceeds 200 characters.
    """
    stripped = description.strip()
    if not stripped:
        raise ValueError("Description cannot be empty.")
    if len(stripped) > 200:
        raise ValueError("Description cannot exceed 200 characters.")
    return stripped


def validate_task_file(filepath: str) -> None:
    """Check that the tasks file exists.

    Raises:
        FileNotFoundError: if *filepath* does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Tasks file not found: {filepath}")


def validate_task_id(task_id: int) -> None:
    """Validate that a task ID is a positive integer.

    Raises:
        ValueError: if *task_id* is not a positive integer.
    """
    if not isinstance(task_id, int) or task_id <= 0:
        raise ValueError(f"Task ID must be a positive integer, got: {task_id!r}")
