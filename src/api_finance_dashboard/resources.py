"""Resource path resolution for both development and PyInstaller environments."""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """Resolve a resource file path that works in both dev and packaged modes.

    In development: resolves relative to the project root.
    In PyInstaller bundle: resolves relative to sys._MEIPASS.
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base = Path(sys._MEIPASS)
    else:
        # Running in development — project root is 3 levels up from this file
        base = Path(__file__).resolve().parent.parent.parent

    return str(base / relative_path)
