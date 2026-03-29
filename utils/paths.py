"""Shared path helpers used across command modules."""

import os


def get_tasks_file() -> str:
    """Return the path to the tasks file, preferring the environment variable
    TASKS_FILE when set, otherwise defaulting to 'tasks.json' in the current
    working directory."""
    return os.environ.get("TASKS_FILE", "tasks.json")
