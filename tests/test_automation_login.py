"""Tests for per-site login session."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from api_finance_dashboard.engine.automation_login import (
    _wait_for_lock_release,
    run_login_session,
)


@pytest.mark.asyncio
async def test_run_login_session_launches_and_waits():
    """Verify login session launches persistent context and waits for close."""
    page = AsyncMock()
    context = AsyncMock()
    context.pages = [page]
    context.wait_for_event = AsyncMock(return_value=None)

    chromium = AsyncMock()
    chromium.launch_persistent_context = AsyncMock(return_value=context)
    playwright = AsyncMock()
    playwright.chromium = chromium

    with patch(
        "api_finance_dashboard.engine.automation_login.async_playwright"
    ) as mock_pw, patch(
        "api_finance_dashboard.engine.automation_login._wait_for_lock_release",
        new_callable=AsyncMock,
    ) as mock_wait:
        mock_pw.return_value.__aenter__ = AsyncMock(return_value=playwright)
        mock_pw.return_value.__aexit__ = AsyncMock(return_value=False)

        await run_login_session(
            executable_path=r"C:\chrome.exe",
            automation_profile_path=r"C:\auto_profile",
            target_url="https://panel.example.com/login",
        )

    chromium.launch_persistent_context.assert_awaited_once()
    launch_kwargs = chromium.launch_persistent_context.await_args.kwargs
    assert launch_kwargs["user_data_dir"] == r"C:\auto_profile"
    assert launch_kwargs["executable_path"] == r"C:\chrome.exe"
    assert launch_kwargs["headless"] is False

    page.goto.assert_awaited_once_with(
        "https://panel.example.com/login", wait_until="domcontentloaded"
    )
    context.wait_for_event.assert_awaited_once_with("close", timeout=0)
    mock_wait.assert_awaited_once_with(r"C:\auto_profile")


@pytest.mark.asyncio
async def test_run_login_session_raises_if_no_browser():
    """Should raise RuntimeError if no Chrome/Edge found."""
    with patch(
        "api_finance_dashboard.engine.automation_login.find_chrome_executable",
        return_value=None,
    ):
        with pytest.raises(RuntimeError, match="未找到"):
            await run_login_session(
                executable_path=None,
                automation_profile_path=r"C:\auto_profile",
                target_url="https://example.com",
            )


@pytest.mark.asyncio
async def test_wait_for_lock_release_returns_when_no_locks(tmp_path):
    """Should return immediately if no lock files exist."""
    await _wait_for_lock_release(str(tmp_path))


@pytest.mark.asyncio
async def test_wait_for_lock_release_waits_for_lockfile(tmp_path):
    """Should wait until lockfile disappears."""
    lockfile = tmp_path / "lockfile"
    lockfile.write_text("")

    call_count = 0
    original_sleep = __import__("asyncio").sleep

    async def mock_sleep(seconds):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            lockfile.unlink()
        await original_sleep(0)  # yield control without real delay

    with patch("api_finance_dashboard.engine.automation_login.asyncio.sleep", mock_sleep):
        await _wait_for_lock_release(str(tmp_path))

    assert not lockfile.exists()
    assert call_count >= 2
