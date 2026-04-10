"""Unit tests for browser detection via system scan."""

from pathlib import Path
from unittest.mock import patch

import pytest

from api_finance_dashboard.engine.browser_detector import (
    BrowserDetectionResult,
    scan_installed_browsers,
)


class TestScanInstalledBrowsers:
    @patch("api_finance_dashboard.engine.browser_detector.platform")
    def test_unsupported_platform(self, mock_platform):
        mock_platform.system.return_value = "Linux"
        assert scan_installed_browsers() == []

    @patch("api_finance_dashboard.engine.browser_detector.platform")
    @patch("api_finance_dashboard.engine.browser_detector._scan_windows")
    def test_windows_delegates(self, mock_scan, mock_platform):
        mock_platform.system.return_value = "Windows"
        expected = [BrowserDetectionResult(
            browser_type="chrome",
            display_name="Google Chrome",
            profile_path=r"C:\Users\test\AppData\Local\Google\Chrome\User Data",
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        )]
        mock_scan.return_value = expected
        result = scan_installed_browsers()
        assert result == expected

    @patch("api_finance_dashboard.engine.browser_detector.platform")
    @patch("api_finance_dashboard.engine.browser_detector._scan_macos")
    def test_macos_delegates(self, mock_scan, mock_platform):
        mock_platform.system.return_value = "Darwin"
        expected = [BrowserDetectionResult(
            browser_type="chrome",
            display_name="Google Chrome",
            profile_path="/Users/test/Library/Application Support/Google/Chrome",
            executable_path="/Applications/Google Chrome.app",
        )]
        mock_scan.return_value = expected
        result = scan_installed_browsers()
        assert result == expected

    @patch("api_finance_dashboard.engine.browser_detector.platform")
    @patch("api_finance_dashboard.engine.browser_detector._scan_windows")
    def test_no_browsers_found(self, mock_scan, mock_platform):
        mock_platform.system.return_value = "Windows"
        mock_scan.return_value = []
        assert scan_installed_browsers() == []


class TestBrowserDetectionResult:
    def test_frozen(self):
        result = BrowserDetectionResult(
            browser_type="chrome",
            display_name="Google Chrome",
            profile_path="/path",
        )
        with pytest.raises(AttributeError):
            result.browser_type = "edge"

    def test_optional_executable(self):
        result = BrowserDetectionResult(
            browser_type="edge",
            display_name="Microsoft Edge",
            profile_path="/path",
        )
        assert result.executable_path is None
