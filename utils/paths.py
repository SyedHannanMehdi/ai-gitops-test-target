import os
from pathlib import Path


def get_tasks_file() -> str:
    """Return the path to the tasks JSON file.

    Defaults to ``tasks.json`` in the user's home directory, matching the
    original behaviour of the individual command modules.  The path can be
    overridden by setting the ``TASKS_FILE`` environment variable.
    """
    return os.environ.get("TASKS_FILE", str(Path.home() / "tasks.json"))
