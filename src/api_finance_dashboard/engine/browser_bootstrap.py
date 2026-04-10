"""Browser bootstrap - check browser availability at startup.

Verifies that a compatible Chromium-based browser (Chrome/Edge) is
installed before the main window loads. If none is found, offers to
install Playwright's bundled Chromium as a fallback.
"""

import subprocess
import sys
from dataclasses import dataclass

# Hide console window when spawning subprocesses on Windows
_SUBPROCESS_FLAGS = (
    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
)

from api_finance_dashboard.engine.browser_detector import scan_installed_browsers
from api_finance_dashboard.engine.browser_engine import find_chrome_executable


@dataclass(frozen=True)
class BrowserCheckResult:
    available: bool
    browser_name: str | None = None
    executable_path: str | None = None
    needs_playwright_install: bool = False


def check_browser_availability() -> BrowserCheckResult:
    """Check if a usable browser is available on the system.

    Priority:
    1. System Chrome / Edge (preferred - preserves user profile reuse)
    2. Playwright bundled Chromium (fallback)
    """
    # Check for system Chrome/Edge
    exe = find_chrome_executable()
    if exe:
        browsers = scan_installed_browsers()
        name = browsers[0].display_name if browsers else "Chrome/Edge"
        return BrowserCheckResult(
            available=True,
            browser_name=name,
            executable_path=exe,
        )

    # Check if Playwright Chromium is already installed
    if _is_playwright_chromium_installed():
        return BrowserCheckResult(
            available=True,
            browser_name="Playwright Chromium",
        )

    # Nothing available
    return BrowserCheckResult(
        available=False,
        needs_playwright_install=True,
    )


def install_playwright_chromium() -> tuple[bool, str]:
    """Run `playwright install chromium` and return (success, output).

    Returns:
        (True, stdout) on success, (False, error_message) on failure.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300,
            creationflags=_SUBPROCESS_FLAGS,
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, "下载超时，请检查网络连接后重试。"
    except Exception as e:
        return False, str(e)


def _is_playwright_chromium_installed() -> bool:
    """Check if Playwright's bundled Chromium is already installed."""
    try:
        from playwright._impl._driver import compute_driver_executable

        driver_exec = compute_driver_executable()
        result = subprocess.run(
            [str(driver_exec), "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=_SUBPROCESS_FLAGS,
        )
        # If dry-run shows nothing to install, it's already there
        return "is already installed" in result.stdout.lower()
    except Exception:
        return False
