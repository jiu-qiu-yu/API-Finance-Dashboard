"""Tests for automation profile management and ConfigRepository accessors."""

import platform
from pathlib import Path
from unittest.mock import patch

import pytest

from api_finance_dashboard.engine.automation_profile import (
    ensure_automation_profile_dir,
    get_default_automation_profile_dir,
    reset_automation_profile,
)


class TestGetDefaultAutomationProfileDir:
    @patch("api_finance_dashboard.engine.automation_profile.platform")
    def test_windows_uses_localappdata(self, mock_platform, monkeypatch):
        mock_platform.system.return_value = "Windows"
        monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\test\AppData\Local")

        result = get_default_automation_profile_dir()

        assert result == Path(r"C:\Users\test\AppData\Local\api-finance-dashboard\automation_profile")

    @patch("api_finance_dashboard.engine.automation_profile.platform")
    def test_macos_uses_application_support(self, mock_platform):
        mock_platform.system.return_value = "Darwin"

        result = get_default_automation_profile_dir()

        home = Path.home()
        expected = home / "Library" / "Application Support" / "api-finance-dashboard" / "automation_profile"
        assert result == expected

    @patch("api_finance_dashboard.engine.automation_profile.platform")
    def test_linux_uses_xdg_data_home(self, mock_platform, monkeypatch):
        mock_platform.system.return_value = "Linux"
        monkeypatch.setenv("XDG_DATA_HOME", "/home/test/.local/share")

        result = get_default_automation_profile_dir()

        assert result == Path("/home/test/.local/share/api-finance-dashboard/automation_profile")


class TestEnsureAutomationProfileDir:
    def test_creates_directory_if_missing(self, tmp_path):
        target = tmp_path / "auto_profile"

        result = ensure_automation_profile_dir(target)

        assert result.exists()
        assert result.is_dir()

    def test_idempotent_when_exists(self, tmp_path):
        target = tmp_path / "auto_profile"
        target.mkdir()
        marker = target / "marker.txt"
        marker.write_text("keep")

        result = ensure_automation_profile_dir(target)

        assert result.exists()
        assert marker.exists()

    def test_creates_nested_parents(self, tmp_path):
        target = tmp_path / "a" / "b" / "c" / "profile"

        result = ensure_automation_profile_dir(target)

        assert result.exists()
        assert result.is_dir()


class TestResetAutomationProfile:
    def test_deletes_and_recreates(self, tmp_path):
        target = tmp_path / "auto_profile"
        target.mkdir()
        (target / "cookies.db").write_text("data")
        (target / "subdir").mkdir()
        (target / "subdir" / "file.txt").write_text("data")

        result = reset_automation_profile(target)

        assert result.exists()
        assert result.is_dir()
        assert list(result.iterdir()) == []

    def test_creates_if_not_exists(self, tmp_path):
        target = tmp_path / "new_profile"

        result = reset_automation_profile(target)

        assert result.exists()
        assert result.is_dir()


class TestConfigRepositoryAutomationProfile:
    def test_get_automation_profile_path_auto_resolves(self, tmp_path):
        from api_finance_dashboard.data.config_repository import ConfigRepository
        from api_finance_dashboard.data.database import init_database

        db_path = tmp_path / "test.db"
        init_database(db_path)

        repo = ConfigRepository(db_path)

        mock_dir = tmp_path / "mock_auto_profile"
        with patch(
            "api_finance_dashboard.engine.automation_profile.get_default_automation_profile_dir",
            return_value=mock_dir,
        ):
            path = repo.get_automation_profile_path()

        assert path == str(mock_dir)
        # Should be persisted now
        assert repo.get("automation_profile_path") == str(mock_dir)

    def test_get_automation_profile_path_returns_stored(self, tmp_path):
        from api_finance_dashboard.data.config_repository import ConfigRepository
        from api_finance_dashboard.data.database import init_database

        db_path = tmp_path / "test.db"
        init_database(db_path)

        repo = ConfigRepository(db_path)
        repo.set_automation_profile_path("/custom/path")

        path = repo.get_automation_profile_path()

        assert path == "/custom/path"
