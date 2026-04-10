"""Browser detection - scan installed browsers and resolve profile paths."""

import json
import os
import platform
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrowserProfile:
    directory: str  # "Default", "Profile 1", etc.
    name: str  # User-visible name, e.g. "张三", "Work Account"


@dataclass(frozen=True)
class BrowserDetectionResult:
    browser_type: str  # "chrome", "edge", "chromium"
    display_name: str  # "Google Chrome", "Microsoft Edge"
    profile_path: str
    executable_path: str | None = None


# Windows: (display_name, browser_type, exe relative paths, profile subpath under LOCALAPPDATA)
_WINDOWS_BROWSERS = (
    (
        "Google Chrome",
        "chrome",
        (r"Google\Chrome\Application\chrome.exe",),
        r"Google\Chrome\User Data",
    ),
    (
        "Microsoft Edge",
        "edge",
        (r"Microsoft\Edge\Application\msedge.exe",),
        r"Microsoft\Edge\User Data",
    ),
    (
        "Chromium",
        "chromium",
        (r"Chromium\Application\chrome.exe",),
        r"Chromium\User Data",
    ),
)

# macOS: (display_name, browser_type, app_path, profile subdir under ~/Library/Application Support)
_MACOS_BROWSERS = (
    ("Google Chrome", "chrome", "/Applications/Google Chrome.app", "Google/Chrome"),
    ("Microsoft Edge", "edge", "/Applications/Microsoft Edge.app", "Microsoft Edge"),
    ("Chromium", "chromium", "/Applications/Chromium.app", "Chromium"),
)


def scan_installed_browsers() -> list[BrowserDetectionResult]:
    """Scan the system for installed Chromium-based browsers and return results."""
    system = platform.system()
    if system == "Windows":
        return _scan_windows()
    elif system == "Darwin":
        return _scan_macos()
    return []


def _scan_windows() -> list[BrowserDetectionResult]:
    """Scan Windows for installed browsers in Program Files and LOCALAPPDATA."""
    results = []
    search_roots = []

    program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
    local_app_data = os.environ.get("LOCALAPPDATA", "")

    if program_files:
        search_roots.append(Path(program_files))
    if program_files_x86:
        search_roots.append(Path(program_files_x86))
    if local_app_data:
        search_roots.append(Path(local_app_data))

    for display_name, browser_type, exe_subpaths, profile_subpath in _WINDOWS_BROWSERS:
        exe_path = None
        for root in search_roots:
            for subpath in exe_subpaths:
                candidate = root / subpath
                if candidate.exists():
                    exe_path = str(candidate)
                    break
            if exe_path:
                break

        if not exe_path:
            continue

        profile_path = ""
        if local_app_data:
            profile_path = str(Path(local_app_data) / profile_subpath)

        if not profile_path or not Path(profile_path).exists():
            continue

        results.append(BrowserDetectionResult(
            browser_type=browser_type,
            display_name=display_name,
            profile_path=profile_path,
            executable_path=exe_path,
        ))

    return results


def _scan_macos() -> list[BrowserDetectionResult]:
    """Scan macOS for installed browsers in /Applications."""
    results = []
    for display_name, browser_type, app_path, profile_subdir in _MACOS_BROWSERS:
        if not Path(app_path).exists():
            continue

        profile_path = str(
            Path.home() / "Library" / "Application Support" / profile_subdir
        )
        if not Path(profile_path).exists():
            continue

        results.append(BrowserDetectionResult(
            browser_type=browser_type,
            display_name=display_name,
            profile_path=profile_path,
            executable_path=app_path,
        ))

    return results


def scan_profiles(user_data_dir: str) -> list[BrowserProfile]:
    """Scan a browser's User Data directory for available profiles.

    Reads 'Local State' JSON to get profile display names,
    falls back to scanning directories if Local State is unavailable.
    """
    data_dir = Path(user_data_dir)
    profiles: list[BrowserProfile] = []

    # Try reading Local State for profile name mapping
    local_state_path = data_dir / "Local State"
    name_map: dict[str, str] = {}
    if local_state_path.is_file():
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            info_cache = state.get("profile", {}).get("info_cache", {})
            for dir_name, info in info_cache.items():
                display = info.get("name", dir_name)
                name_map[dir_name] = display
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    # Scan for profile directories
    for entry in sorted(data_dir.iterdir()):
        if not entry.is_dir():
            continue
        # Chrome profiles are "Default" or "Profile N"
        dir_name = entry.name
        if dir_name == "Default" or dir_name.startswith("Profile "):
            # Verify it's a real profile (has a Preferences file)
            if (entry / "Preferences").is_file():
                display_name = name_map.get(dir_name, dir_name)
                profiles.append(BrowserProfile(
                    directory=dir_name,
                    name=display_name,
                ))

    return profiles
