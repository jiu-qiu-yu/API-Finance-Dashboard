"""Automation browser profile directory management.

Manages a dedicated browser profile directory for automation,
separate from the user's daily browser User Data directory.
"""

import os
import platform
import shutil
from pathlib import Path

_APP_NAME = "api-finance-dashboard"
_PROFILE_DIR_NAME = "automation_profile"


def get_default_automation_profile_dir() -> Path:
    """Resolve platform-specific default path for the automation profile.

    - Windows: %LOCALAPPDATA%/api-finance-dashboard/automation_profile/
    - macOS:   ~/Library/Application Support/api-finance-dashboard/automation_profile/
    """
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("LOCALAPPDATA", "")
        if not base:
            base = str(Path.home() / "AppData" / "Local")
        return Path(base) / _APP_NAME / _PROFILE_DIR_NAME
    elif system == "Darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / _APP_NAME
            / _PROFILE_DIR_NAME
        )
    else:
        # Linux / fallback
        xdg = os.environ.get("XDG_DATA_HOME", "")
        if not xdg:
            xdg = str(Path.home() / ".local" / "share")
        return Path(xdg) / _APP_NAME / _PROFILE_DIR_NAME


def ensure_automation_profile_dir(path: str | Path) -> Path:
    """Create the automation profile directory if it does not exist.

    Returns the resolved Path.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def reset_automation_profile(path: str | Path) -> Path:
    """Delete and re-create the automation profile directory.

    Returns the resolved Path of the freshly created directory.
    """
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()
