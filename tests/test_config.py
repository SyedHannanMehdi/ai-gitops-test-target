"""Tests for config loading behaviour (issue #2)."""

import json
import sys
import textwrap
from pathlib import Path
from unittest import mock

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_task(monkeypatch, tmp_path):
    """Re-import task module with CONFIG_PATH pointing to tmp_path."""
    config_path = tmp_path / "config.yaml"
    config_dir = tmp_path

    # Patch constants before the module is used
    import importlib
    import task as task_module

    monkeypatch.setattr(task_module, "CONFIG_PATH", config_path)
    monkeypatch.setattr(task_module, "CONFIG_DIR", config_dir)

    return task_module, config_path, config_dir


# ---------------------------------------------------------------------------
# load_config — missing file
# ---------------------------------------------------------------------------

class TestMissingConfig:
    def test_creates_config_file_when_missing(self, monkeypatch, tmp_path, capsys):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)

        assert not config_path.exists(), "Pre-condition: file should not exist"

        result = task.load_config()

        assert config_path.exists(), "load_config() must create the config file"

    def test_returns_default_values_when_missing(self, monkeypatch, tmp_path, capsys):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)

        result = task.load_config()

        assert "default_priority" in result
        assert result["default_priority"] == "medium"
        assert "tasks_file" in result
        assert "date_format" in result

    def test_prints_friendly_message_when_creating_default(
        self, monkeypatch, tmp_path, capsys
    ):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)

        task.load_config()

        captured = capsys.readouterr()
        assert "task-cli" in captured.out
        assert str(config_path) in captured.out

    def test_no_crash_when_config_missing(self, monkeypatch, tmp_path):
        """Regression: must not raise FileNotFoundError."""
        task, config_path, _ = _import_task(monkeypatch, tmp_path)

        try:
            task.load_config()
        except FileNotFoundError:
            pytest.fail(
                "load_config() raised FileNotFoundError when config file was missing"
            )


# ---------------------------------------------------------------------------
# load_config — file exists
# ---------------------------------------------------------------------------

class TestExistingConfig:
    def test_loads_existing_config(self, monkeypatch, tmp_path):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)
        config_path.write_text(
            yaml.dump({"default_priority": "high", "date_format": "%d/%m/%Y"})
        )

        result = task.load_config()

        assert result["default_priority"] == "high"
        assert result["date_format"] == "%d/%m/%Y"

    def test_merges_missing_keys_with_defaults(self, monkeypatch, tmp_path):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)
        # Write a partial config (only one key)
        config_path.write_text(yaml.dump({"default_priority": "low"}))

        result = task.load_config()

        # Partial override preserved
        assert result["default_priority"] == "low"
        # Default keys still present
        assert "tasks_file" in result
        assert "date_format" in result

    def test_empty_config_file_returns_defaults(self, monkeypatch, tmp_path):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)
        config_path.write_text("")  # empty YAML → yaml.safe_load returns None

        result = task.load_config()

        assert result["default_priority"] == "medium"

    def test_invalid_yaml_exits_with_error(self, monkeypatch, tmp_path):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)
        config_path.write_text("key: [\nbad yaml")

        with pytest.raises(SystemExit) as exc_info:
            task.load_config()

        assert exc_info.value.code == 1

    def test_invalid_yaml_prints_helpful_message(self, monkeypatch, tmp_path, capsys):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)
        config_path.write_text("key: [\nbad yaml")

        with pytest.raises(SystemExit):
            task.load_config()

        captured = capsys.readouterr()
        assert "not valid YAML" in captured.err or "Error" in captured.err


# ---------------------------------------------------------------------------
# _create_default_config — permission error
# ---------------------------------------------------------------------------

class TestCreateDefaultConfigErrors:
    def test_exits_gracefully_on_permission_error(self, monkeypatch, tmp_path, capsys):
        task, config_path, config_dir = _import_task(monkeypatch, tmp_path)

        # Simulate inability to write by patching open
        original_open = open

        def _mock_open(path, mode="r", **kwargs):
            if str(path) == str(config_path) and "w" in mode:
                raise OSError("Permission denied")
            return original_open(path, mode, **kwargs)

        monkeypatch.setattr("builtins.open", _mock_open)

        with pytest.raises(SystemExit) as exc_info:
            task._create_default_config()

        assert exc_info.value.code == 1

    def test_permission_error_prints_helpful_message(
        self, monkeypatch, tmp_path, capsys
    ):
        task, config_path, config_dir = _import_task(monkeypatch, tmp_path)

        original_open = open

        def _mock_open(path, mode="r", **kwargs):
            if str(path) == str(config_path) and "w" in mode:
                raise OSError("Permission denied")
            return original_open(path, mode, **kwargs)

        monkeypatch.setattr("builtins.open", _mock_open)

        with pytest.raises(SystemExit):
            task._create_default_config()

        captured = capsys.readouterr()
        assert "Error" in captured.err
        assert "permission" in captured.err.lower() or str(config_path) in captured.err


# ---------------------------------------------------------------------------
# Integration: CLI does not crash without config file
# ---------------------------------------------------------------------------

class TestCLIIntegration:
    def test_list_command_without_config(self, monkeypatch, tmp_path, capsys):
        task, config_path, _ = _import_task(monkeypatch, tmp_path)

        # Also point tasks_file inside tmp so we don't touch real FS
        default = task.DEFAULT_CONFIG.copy()
        default["tasks_file"] = str(tmp_path / "tasks.json")
        monkeypatch.setattr(task, "DEFAULT_CONFIG", default)

        # Simulate `task list`
        monkeypatch.setattr(sys, "argv", ["task.py", "list"])

        try:
            task.main()
        except SystemExit as exc:
            # Exit code 0 is acceptable (no tasks message)
            assert exc.code == 0 or exc.code is None
        except FileNotFoundError:
            pytest.fail("main() raised FileNotFoundError — config not handled")
