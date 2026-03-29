"""Tests for config loading behavior in task.py."""

import sys
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml


def _setup_config_patch(tmp_path):
    """Configure task module constants to point at tmp_path for isolation.

    Patches CONFIG_PATH and CONFIG_DIR so that each test operates in its own
    temporary directory without touching the real ~/.config/task-cli/ location.
    """
    config_path = tmp_path / "config.yaml"
    config_dir = tmp_path

    return {
        "task.CONFIG_PATH": config_path,
        "task.CONFIG_DIR": config_dir,
    }


# ---------------------------------------------------------------------------
# Helper to import a fresh load_config with patched paths
# ---------------------------------------------------------------------------

def _load_config_with_patches(tmp_path):
    """Call load_config() with CONFIG_PATH/CONFIG_DIR patched to tmp_path."""
    config_path = tmp_path / "config.yaml"
    patches = _setup_config_patch(tmp_path)
    with patch("task.CONFIG_PATH", config_path), \
         patch("task.CONFIG_DIR", tmp_path):
        import task
        return task.load_config()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestConfigMissing:
    """Config file does not exist yet."""

    def test_auto_creates_config_file(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            task.load_config()
        assert config_path.exists(), "Config file should be auto-created"

    def test_returns_default_values(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            result = task.load_config()
        assert "tasks_file" in result
        assert "default_priority" in result
        assert result["default_priority"] == "medium"

    def test_created_file_is_valid_yaml(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            task.load_config()
        with open(config_path) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)


class TestConfigEmpty:
    """Config file exists but is empty."""

    def test_empty_file_returns_defaults(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text("")
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            result = task.load_config()
        assert result["default_priority"] == "medium"


class TestConfigInvalidYAML:
    """Config file contains syntactically invalid YAML."""

    def test_invalid_yaml_exits_with_error(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text(": bad: yaml: [unclosed")
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            with pytest.raises(SystemExit) as exc_info:
                task.load_config()
        assert exc_info.value.code == 1


class TestConfigNonMappingYAML:
    """Config file contains valid YAML that is not a mapping."""

    def test_scalar_yaml_exits_with_error(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text("just a string\n")
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            with pytest.raises(SystemExit) as exc_info:
                task.load_config()
        assert exc_info.value.code == 1

    def test_list_yaml_exits_with_error(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text("- item1\n- item2\n")
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            with pytest.raises(SystemExit) as exc_info:
                task.load_config()
        assert exc_info.value.code == 1


class TestConfigValidPartial:
    """Config file exists and has some but not all keys."""

    def test_partial_config_merges_with_defaults(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config_path.write_text("default_priority: high\n")
        with patch("task.CONFIG_PATH", config_path), patch("task.CONFIG_DIR", tmp_path):
            import task
            result = task.load_config()
        assert result["default_priority"] == "high"
        assert "tasks_file" in result  # merged from defaults


class TestCLIIntegration:
    """Basic CLI smoke test."""

    def test_no_args_prints_usage(self, tmp_path, capsys):
        config_path = tmp_path / "config.yaml"
        with patch("task.CONFIG_PATH", config_path), \
             patch("task.CONFIG_DIR", tmp_path), \
             patch("sys.argv", ["task"]):
            import task
            # Re-load config so tmp_path is used
            task.config = task.load_config()
            with pytest.raises(SystemExit) as exc_info:
                task.main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Usage" in captured.out
