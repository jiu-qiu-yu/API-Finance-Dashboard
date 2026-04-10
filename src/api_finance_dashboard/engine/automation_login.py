"""Per-site login session using the automation browser profile.

Launches a persistent browser context, navigates to the target URL,
and waits for the user to close the browser after logging in.
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

from api_finance_dashboard.engine.browser_engine import find_chrome_executable

_LOCK_FILE_NAMES = ("lockfile", "SingletonLock", "SingletonSocket")
_LOCK_WAIT_INTERVAL = 0.5  # seconds
_LOCK_WAIT_TIMEOUT = 10.0  # seconds


async def _wait_for_lock_release(profile_path: str) -> None:
    """Wait until Chrome releases lock files in the profile directory.

    After Playwright reports the context as closed, the underlying Chrome
    process may still be cleaning up (flushing cookies, releasing locks).
    We must wait for the lock files to disappear before the caller can
    safely launch a new browser instance on the same profile.
    """
    profile = Path(profile_path)
    elapsed = 0.0
    while elapsed < _LOCK_WAIT_TIMEOUT:
        locks = [profile / name for name in _LOCK_FILE_NAMES]
        if not any(lock.exists() for lock in locks):
            return
        await asyncio.sleep(_LOCK_WAIT_INTERVAL)
        elapsed += _LOCK_WAIT_INTERVAL


async def run_login_session(
    executable_path: str | None,
    automation_profile_path: str,
    target_url: str,
) -> None:
    """Launch browser with automation profile, navigate to URL, wait for close.

    The user manually logs in via the browser window. When the user closes
    the browser, this function waits for the Chrome process to fully exit
    (lock files released) before returning — ensuring the profile directory
    is safe to reuse immediately.
    """
    exe = executable_path or find_chrome_executable()
    if not exe:
        raise RuntimeError(
            "未找到已安装的 Chrome 或 Edge 浏览器。\n\n"
            "请安装 Google Chrome 或 Microsoft Edge。"
        )

    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=automation_profile_path,
            executable_path=exe,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--disable-extensions", "--enable-automation"],
            chromium_sandbox=True,
        )

        # Navigate the first page to the target URL
        if context.pages:
            page = context.pages[0]
        else:
            page = await context.new_page()

        await page.goto(target_url, wait_until="domcontentloaded")

        # Wait until the user closes the browser
        try:
            await context.wait_for_event("close", timeout=0)
        except Exception:
            pass
        finally:
            try:
                await context.close()
            except Exception:
                pass

    # Playwright has stopped, but Chrome process may still be exiting.
    # Wait for lock files to be released before returning.
    await _wait_for_lock_release(automation_profile_path)
