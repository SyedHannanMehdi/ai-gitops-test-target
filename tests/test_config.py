"""Tests for config loading — focusing on the missing-config-file scenario."""

import sys
import json
import importlib
from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def reload_task_module():
    """Re-import task so module-level constants pick up monkeypatched paths."""
    if "task" in sys.modules:
        del sys.modules["task"]
    import task as t
    return t


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLoadConfigMissingFile:
    """load_config() should never raise FileNotFoundError."""

    def test_creates_config_file_when_missing(self, tmp_path, monkeypatch):
        """When config is absent load_config creates the file and returns defaults."""
        config_dir = tmp_path / "task-cli"
        config_file = config_dir / "config.yaml"

        # Patch the module-level constants before import
        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        assert not config_file.exists(), "Pre-condition: file must not exist"

        result = t.load_config()

        assert config_file.exists(), "Config file should have been created"
        assert isinstance(result, dict)

    def test_returns_default_values_when_missing(self, tmp_path, monkeypatch):
        """Returned config contains all expected default keys."""
        config_dir = tmp_path / "task-cli"
        config_file = config_dir / "config.yaml"

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        result = t.load_config()

        assert "storage" in result
        assert "default_priority" in result
        assert "date_format" in result

    def test_written_file_is_valid_yaml(self, tmp_path, monkeypatch):
        """The auto-generated config file must be parseable YAML."""
        config_dir = tmp_path / "task-cli"
        config_file = config_dir / "config.yaml"

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        t.load_config()

        with open(config_file, "r", encoding="utf-8") as f:
            parsed = yaml.safe_load(f)

        assert isinstance(parsed, dict)

    def test_no_crash_without_config(self, tmp_path, monkeypatch, capsys):
        """load_config must not raise FileNotFoundError or any unhandled exception."""
        config_dir = tmp_path / "does-not-exist" / "task-cli"
        config_file = config_dir / "config.yaml"

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        # This must NOT raise
        try:
            result = t.load_config()
        except FileNotFoundError as exc:
            pytest.fail(f"FileNotFoundError was raised: {exc}")
        except SystemExit as exc:
            pytest.fail(f"SystemExit was raised unexpectedly: {exc}")

        assert isinstance(result, dict)

    def test_informative_message_printed_to_stderr(self, tmp_path, monkeypatch, capsys):
        """A helpful message should be printed to stderr when the file is missing."""
        config_dir = tmp_path / "task-cli"
        config_file = config_dir / "config.yaml"

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        t.load_config()

        captured = capsys.readouterr()
        assert captured.err, "Expected an informative message on stderr"
        assert "config" in captured.err.lower()


class TestLoadConfigExistingFile:
    """load_config() should read user values when the file exists."""

    def test_reads_existing_config(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "task-cli"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        user_cfg = {"default_priority": "high", "date_format": "%d/%m/%Y"}
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(user_cfg, f)

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        result = t.load_config()

        assert result["default_priority"] == "high"
        assert result["date_format"] == "%d/%m/%Y"

    def test_defaults_merged_with_user_config(self, tmp_path, monkeypatch):
        """Keys absent from the user config fall back to defaults."""
        config_dir = tmp_path / "task-cli"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"

        user_cfg = {"default_priority": "low"}
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(user_cfg, f)

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        result = t.load_config()

        # User override
        assert result["default_priority"] == "low"
        # Default still present
        assert "storage" in result
        assert "date_format" in result

    def test_invalid_yaml_exits_gracefully(self, tmp_path, monkeypatch):
        """Corrupt YAML must produce SystemExit(1), not a traceback."""
        config_dir = tmp_path / "task-cli"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.yaml"
        config_file.write_text("key: [unclosed bracket", encoding="utf-8")

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        with pytest.raises(SystemExit) as exc_info:
            t.load_config()

        assert exc_info.value.code == 1


class TestCreateDefaultConfig:
    """_create_default_config() internal helper."""

    def test_creates_intermediate_directories(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "a" / "b" / "c" / "task-cli"
        config_file = config_dir / "config.yaml"

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        t._create_default_config()

        assert config_file.exists()

    def test_default_config_contains_required_keys(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "task-cli"
        config_file = config_dir / "config.yaml"

        import task as t
        monkeypatch.setattr(t, "CONFIG_DIR", config_dir)
        monkeypatch.setattr(t, "CONFIG_PATH", config_file)

        t._create_default_config()

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for key in ("storage", "default_priority", "date_format"):
            assert key in data, f"Missing key '{key}' in default config"
