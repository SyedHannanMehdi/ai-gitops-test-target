"""Shared validation helpers used across command modules."""

import os
from typing import List


def validate_description(description: str) -> None:
    """Validate that a task description is non-empty.

    Raises:
        ValueError: If *description* is empty or contains only whitespace.
    """
    if not description or not description.strip():
        raise ValueError("Task description cannot be empty.")


def validate_task_file(filepath: str) -> None:
    """Validate that the tasks file exists at *filepath*.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Tasks file not found: {filepath}")


def validate_task_id(task_id: int, tasks: List[dict]) -> None:
    """Validate that *task_id* refers to an existing task in *tasks*.

    Raises:
        ValueError: If *task_id* is not a valid index into *tasks*.
    """
    if task_id < 1 or task_id > len(tasks):
        raise ValueError(
            f"Invalid task ID: {task_id}. Must be between 1 and {len(tasks)}."
        )
