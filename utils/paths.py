import os

def get_tasks_file() -> str:
    """Return the path to the tasks JSON file.

    Respects the ``TASKS_FILE`` environment variable when set; otherwise
    defaults to ``tasks.json`` inside the user's home directory — preserving
    the original behaviour of the individual command modules.
    """
    default = os.path.join(os.path.expanduser("~"), "tasks.json")
    return os.environ.get("TASKS_FILE", default)
