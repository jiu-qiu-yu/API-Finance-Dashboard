from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from api_finance_dashboard.engine.browser_engine import (
    BrowserEngine,
    _classify_startup_failure,
    detect_browser_conflict,
    find_chrome_executable,
    validate_browser_profile_path,
)


def test_classify_startup_failure_detects_about_blank():
    message = _classify_startup_failure(
        "startup blank page",
        page_url="about:blank",
    )

    assert "about:blank" in message
    assert "主配置目录不支持被自动化复用" in message


def test_classify_startup_failure_detects_warning_page():
    message = _classify_startup_failure(
        "Target page, context or browser has been closed",
        "您使用的是不受支持的命令行标记：--no-sandbox",
    )

    assert "--no-sandbox" in message


@patch("api_finance_dashboard.engine.browser_engine.platform")
def test_find_chrome_executable_skips_chromium_path_fallback(mock_platform):
    mock_platform.system.return_value = "Linux"

    with patch("api_finance_dashboard.engine.browser_engine.shutil.which") as mock_which:
        mock_which.side_effect = lambda name: {
            "chromium": "/usr/bin/chromium",
            "chrome": None,
            "google-chrome": None,
            "msedge": None,
        }.get(name)

        assert find_chrome_executable() is None


class TestValidateBrowserProfilePath:
    def test_valid_directory(self, tmp_path):
        valid, msg = validate_browser_profile_path(str(tmp_path))
        assert valid is True

    def test_nonexistent_path(self):
        valid, msg = validate_browser_profile_path("/nonexistent/path")
        assert valid is False
        assert "does not exist" in msg

    def test_empty_automation_profile_is_valid(self, tmp_path):
        """Automation profile dirs are valid even without Default/ or Local State."""
        profile = tmp_path / "automation_profile"
        profile.mkdir()
        valid, msg = validate_browser_profile_path(str(profile))
        assert valid is True


class TestDetectBrowserConflict:
    def test_no_lock_files(self, tmp_path):
        has_conflict, msg = detect_browser_conflict(str(tmp_path))
        assert has_conflict is False

    def test_lockfile_detected(self, tmp_path):
        (tmp_path / "lockfile").write_text("")
        has_conflict, msg = detect_browser_conflict(str(tmp_path))
        assert has_conflict is True
        assert "自动化浏览器" in msg

    def test_singleton_lock_detected(self, tmp_path):
        (tmp_path / "SingletonLock").write_text("")
        has_conflict, msg = detect_browser_conflict(str(tmp_path))
        assert has_conflict is True

    def test_message_says_daily_browser_ok(self, tmp_path):
        (tmp_path / "lockfile").write_text("")
        _, msg = detect_browser_conflict(str(tmp_path))
        assert "日常浏览器无需关闭" in msg


@pytest.mark.asyncio
async def test_start_accepts_about_blank_for_automation_profile():
    """about:blank is normal for a fresh automation profile — should NOT raise."""
    engine = BrowserEngine(
        profile_path=r"C:\Users\test\AppData\Local\api-finance-dashboard\automation_profile",
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )

    page = AsyncMock()
    page.url = "about:blank"
    context = AsyncMock()
    context.pages = [page]
    chromium = AsyncMock()
    chromium.launch_persistent_context = AsyncMock(return_value=context)
    playwright = AsyncMock()
    playwright.chromium = chromium

    with patch(
        "api_finance_dashboard.engine.browser_engine.detect_browser_conflict",
        return_value=(False, "ok"),
    ), patch(
        "api_finance_dashboard.engine.browser_engine.async_playwright"
    ) as mock_async_playwright:
        mock_async_playwright.return_value.start = AsyncMock(return_value=playwright)

        await engine.start()  # Should succeed, not raise


@pytest.mark.asyncio
async def test_start_uses_resolved_executable():
    engine = BrowserEngine(
        profile_path=r"C:\Users\test\AppData\Local\api-finance-dashboard\automation_profile",
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )

    context = AsyncMock()
    chromium = AsyncMock()
    chromium.launch_persistent_context = AsyncMock(return_value=context)
    playwright = AsyncMock()
    playwright.chromium = chromium

    with patch(
        "api_finance_dashboard.engine.browser_engine.detect_browser_conflict",
        return_value=(False, "ok"),
    ), patch(
        "api_finance_dashboard.engine.browser_engine.async_playwright",
    ) as mock_async_playwright:
        mock_async_playwright.return_value.start = AsyncMock(return_value=playwright)

        await engine.start()

    launch_kwargs = chromium.launch_persistent_context.await_args.kwargs
    assert launch_kwargs["executable_path"].endswith("chrome.exe")
    assert launch_kwargs["chromium_sandbox"] is True
    # No profile-directory arg needed — profile_path points directly to the dir
    assert "--profile-directory" not in str(launch_kwargs.get("args", []))
