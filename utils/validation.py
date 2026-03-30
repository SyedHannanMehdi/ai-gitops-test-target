"""Shared validation helpers for the task manager application."""

import os


def validate_description(description: str) -> None:
    """Validate that a task description is non-empty.

    Args:
        description: The task description string to validate.

    Raises:
        ValueError: If the description is empty or contains only whitespace.
    """
    if not description or not description.strip():
        raise ValueError("Task description cannot be empty.")


def validate_task_file(tasks_file: str) -> None:
    """Validate that the tasks file exists.

    Args:
        tasks_file: Path to the tasks file.

    Raises:
        FileNotFoundError: If the tasks file does not exist.
    """
    if not os.path.exists(tasks_file):
        raise FileNotFoundError(f"Tasks file not found: {tasks_file}")


def validate_task_id(task_id: str) -> int:
    """Validate that a task ID is a positive integer.

    Args:
        task_id: The task ID string to validate.

    Returns:
        The task ID as a positive integer.

    Raises:
        ValueError: If the task ID is not a valid positive integer.
    """
    try:
        tid = int(task_id)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid task ID '{task_id}': must be a positive integer.")

    if tid <= 0:
        raise ValueError(f"Invalid task ID '{task_id}': must be a positive integer.")

    return tid
