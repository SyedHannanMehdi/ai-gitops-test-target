"""Tests for config loading behaviour in task.py."""

import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_config_paths(tmp_path: Path):
    """Return a context-manager that points CONFIG_PATH/CONFIG_DIR to tmp_path."""
    config_path = tmp_path / "config.yaml"
    config_dir = tmp_path

    return patch.multiple(
        "task",
        CONFIG_PATH=config_path,
        CONFIG_DIR=config_dir,
    )


def _load_task_module():
    """Import (or return already-imported) task module."""
    import task  # noqa: PLC0415
    return task


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMissingConfig:
    """Config file does not exist yet."""

    def test_auto_creates_config_file(self, tmp_path):
        import task
        with _patch_config_paths(tmp_path):
            result = task.load_config()
        assert (tmp_path / "config.yaml").exists()

    def test_returns_defaults_when_missing(self, tmp_path):
        import task
        with _patch_config_paths(tmp_path):
            result = task.load_config()
        assert result == task.DEFAULT_CONFIG

    def test_written_yaml_is_valid(self, tmp_path):
        import task
        with _patch_config_paths(tmp_path):
            task.load_config()
        written = yaml.safe_load((tmp_path / "config.yaml").read_text())
        assert isinstance(written, dict)


class TestEmptyConfig:
    """Config file exists but is completely empty."""

    def test_empty_file_returns_defaults(self, tmp_path):
        import task
        cfg = tmp_path / "config.yaml"
        cfg.write_text("")
        with _patch_config_paths(tmp_path):
            result = task.load_config()
        assert result == task.DEFAULT_CONFIG


class TestInvalidYaml:
    """Config file contains malformed YAML."""

    def test_invalid_yaml_exits_with_error(self, tmp_path):
        import task
        cfg = tmp_path / "config.yaml"
        cfg.write_text(": : invalid: yaml:::")
        with _patch_config_paths(tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                task.load_config()
        assert exc_info.value.code == 1


class TestNonMappingYaml:
    """Config file contains valid YAML but not a mapping at root."""

    def test_scalar_root_exits_with_error(self, tmp_path):
        import task
        cfg = tmp_path / "config.yaml"
        cfg.write_text("just a string\n")
        with _patch_config_paths(tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                task.load_config()
        assert exc_info.value.code == 1

    def test_list_root_exits_with_error(self, tmp_path):
        import task
        cfg = tmp_path / "config.yaml"
        cfg.write_text("- item1\n- item2\n")
        with _patch_config_paths(tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                task.load_config()
        assert exc_info.value.code == 1


class TestValidConfig:
    """Config file is well-formed and contains overrides."""

    def test_merges_with_defaults(self, tmp_path):
        import task
        cfg = tmp_path / "config.yaml"
        cfg.write_text("tasks_file: /custom/path/tasks.json\n")
        with _patch_config_paths(tmp_path):
            result = task.load_config()
        assert result["tasks_file"] == "/custom/path/tasks.json"

    def test_unknown_keys_preserved(self, tmp_path):
        import task
        cfg = tmp_path / "config.yaml"
        cfg.write_text("extra_key: extra_value\n")
        with _patch_config_paths(tmp_path):
            result = task.load_config()
        assert result["extra_key"] == "extra_value"
        # Defaults still present
        assert "tasks_file" in result
