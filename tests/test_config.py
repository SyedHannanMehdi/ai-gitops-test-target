"""
Tests for config loading — especially the missing-config scenario (issue #2).
"""

import json
import sys
import os
import tempfile
import textwrap
from pathlib import Path
from unittest import mock

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_config_path(tmp_path: Path):
    """Return a context manager that redirects CONFIG_PATH/CONFIG_DIR to tmp_path."""
    config_dir = tmp_path / "task-cli"
    config_path = config_dir / "config.yaml"
    return mock.patch.multiple(
        "task",
        CONFIG_DIR=config_dir,
        CONFIG_PATH=config_path,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLoadConfigMissingFile:
    """load_config() must not crash when the config file does not exist."""

    def test_returns_default_config_when_file_missing(self, tmp_path):
        """A missing config file returns the built-in defaults without raising."""
        import task as task_module  # local import so patches apply cleanly

        with _patch_config_path(tmp_path):
            config = task_module.load_config()

        assert isinstance(config, dict), "Expected a dict back from load_config()"
        assert "storage" in config
        assert "display" in config
        assert "defaults" in config

    def test_creates_config_file_when_missing(self, tmp_path):
        """A missing config file should be created on disk with defaults."""
        import task as task_module

        config_path = tmp_path / "task-cli" / "config.yaml"
        assert not config_path.exists(), "Pre-condition: file must not exist"

        with _patch_config_path(tmp_path):
            task_module.load_config()

        assert config_path.exists(), "Config file should have been created"

    def test_created_config_is_valid_yaml(self, tmp_path):
        """The auto-created config file must be parseable YAML."""
        import task as task_module

        config_path = tmp_path / "task-cli" / "config.yaml"

        with _patch_config_path(tmp_path):
            task_module.load_config()

        with open(config_path) as f:
            data = yaml.safe_load(f)

        assert isinstance(data, dict)

    def test_no_crash_without_stderr_output(self, tmp_path, capsys):
        """
        load_config() must not raise and should print a friendly message to stderr
        instead of letting an exception propagate.
        """
        import task as task_module

        with _patch_config_path(tmp_path):
            # Should NOT raise FileNotFoundError (the original bug)
            try:
                task_module.load_config()
            except FileNotFoundError as exc:
                pytest.fail(f"load_config() raised FileNotFoundError: {exc}")

        captured = capsys.readouterr()
        # A helpful message should appear on stderr
        assert "config" in captured.err.lower(), (
            "Expected a user-friendly config message on stderr"
        )

    def test_no_system_exit_when_file_missing(self, tmp_path):
        """A missing config file must NOT cause sys.exit()."""
        import task as task_module

        with _patch_config_path(tmp_path):
            try:
                task_module.load_config()
            except SystemExit as exc:
                pytest.fail(f"load_config() called sys.exit({exc.code}) unexpectedly")


class TestLoadConfigExistingFile:
    """load_config() correctly reads and merges an existing config file."""

    def test_reads_custom_values(self, tmp_path):
        """Values present in the file override the defaults."""
        import task as task_module

        config_dir = tmp_path / "task-cli"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text(
            textwrap.dedent(
                """\
                display:
                  show_completed: true
                  date_format: "%d/%m/%Y"
                """
            )
        )

        with _patch_config_path(tmp_path):
            config = task_module.load_config()

        assert config["display"]["show_completed"] is True
        assert config["display"]["date_format"] == "%d/%m/%Y"

    def test_missing_keys_filled_from_defaults(self, tmp_path):
        """Keys absent from the file are still present via defaults."""
        import task as task_module

        config_dir = tmp_path / "task-cli"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("display:\n  show_completed: true\n")

        with _patch_config_path(tmp_path):
            config = task_module.load_config()

        # "storage" and "defaults" sections should still be present from defaults
        assert "storage" in config
        assert "defaults" in config

    def test_invalid_yaml_exits_with_message(self, tmp_path, capsys):
        """Malformed YAML exits cleanly with an error message."""
        import task as task_module

        config_dir = tmp_path / "task-cli"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("key: [\nbad yaml here")

        with _patch_config_path(tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                task_module.load_config()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "invalid yaml" in captured.err.lower() or "yaml" in captured.err.lower()


class TestDeepMerge:
    """Unit tests for the _deep_merge helper."""

    def test_override_wins_for_scalar(self):
        from task import _deep_merge

        result = _deep_merge({"a": 1, "b": 2}, {"b": 99})
        assert result == {"a": 1, "b": 99}

    def test_nested_dicts_are_merged(self):
        from task import _deep_merge

        base = {"display": {"date_format": "%Y-%m-%d", "show_completed": False}}
        override = {"display": {"show_completed": True}}
        result = _deep_merge(base, override)
        assert result["display"]["date_format"] == "%Y-%m-%d"
        assert result["display"]["show_completed"] is True

    def test_base_not_mutated(self):
        from task import _deep_merge

        base = {"a": {"x": 1}}
        _deep_merge(base, {"a": {"x": 2}})
        assert base["a"]["x"] == 1  # original unchanged

    def test_new_keys_from_override_added(self):
        from task import _deep_merge

        result = _deep_merge({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}


class TestCreateDefaultConfig:
    """Unit tests for create_default_config()."""

    def test_creates_directory_and_file(self, tmp_path):
        from task import _deep_merge
        import task as task_module

        config_dir = tmp_path / "new-dir" / "task-cli"
        config_path = config_dir / "config.yaml"
        assert not config_dir.exists()

        with mock.patch.multiple("task", CONFIG_DIR=config_dir, CONFIG_PATH=config_path):
            task_module.create_default_config()

        assert config_dir.exists()
        assert config_path.exists()

    def test_written_content_matches_default(self, tmp_path):
        import task as task_module

        config_dir = tmp_path / "task-cli"
        config_path = config_dir / "config.yaml"

        with mock.patch.multiple("task", CONFIG_DIR=config_dir, CONFIG_PATH=config_path):
            task_module.create_default_config()

        with open(config_path) as f:
            written = yaml.safe_load(f)

        assert written == task_module.DEFAULT_CONFIG
