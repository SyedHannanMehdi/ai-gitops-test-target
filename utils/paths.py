"""Shared path helpers for the task manager application."""

import os


def get_tasks_file() -> str:
    """Return the path to the tasks file, defaulting to 'tasks.txt'."""
    return os.environ.get("TASKS_FILE", "tasks.txt")
