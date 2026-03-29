import json
import os

MAX_DESCRIPTION_LENGTH = 200


def validate_description(description: str) -> str:
    """Validate and normalize a task description.

    The description must be non-empty (after stripping whitespace) and no longer
    than 200 characters.

    Returns the stripped description string on success.
    Raises ValueError for empty or too-long descriptions.
    """
    stripped = description.strip()
    if not stripped:
        raise ValueError("Description cannot be empty.")
    if len(stripped) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            f"Description is too long ({len(stripped)} chars); "
            f"maximum allowed is {MAX_DESCRIPTION_LENGTH}."
        )
    return stripped


def validate_task_file(filepath: str) -> None:
    """Raise FileNotFoundError if *filepath* does not exist."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Tasks file not found: {filepath}")


def validate_task_id(task_id: int, tasks: list) -> None:
    """Raise ValueError if *task_id* is not a valid stored task id."""
    ids = [t["id"] for t in tasks]
    if task_id not in ids:
        raise ValueError(f"No task found with id {task_id}.")
