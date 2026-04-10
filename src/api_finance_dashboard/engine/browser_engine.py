"""Browser engine for launching Playwright with local user profile."""

import os
import platform
import shutil
from pathlib import Path

try:
    import winreg
except ImportError:
    winreg = None  # type: ignore[assignment]

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

_UNSUPPORTED_LOCAL_PROFILE_FLAGS = frozenset({
    "--no-sandbox",
})
_WARNING_PAGE_INDICATORS = (
    "unsupported command-line flag",
    "不受支持的命令行标记",
)


def validate_browser_profile_path(path: str) -> tuple[bool, str]:
    """Validate that a browser profile path exists and is a directory.

    Automation profile directories are valid even without 'Default/' or
    'Local State' subdirectories — they are created fresh by the app.

    Returns (is_valid, message).
    """
    p = Path(path)
    if not p.exists():
        return False, f"Path does not exist: {path}"
    if not p.is_dir():
        return False, f"Path is not a directory: {path}"
    return True, "Valid browser profile path"


def detect_browser_conflict(profile_path: str) -> tuple[bool, str]:
    """Check if the automation browser is already running with this profile.

    Only checks lock files in the automation profile directory.
    The user's daily browser with a different User Data dir is NOT a
    conflict — Chrome supports multiple instances with different
    --user-data-dir values.

    Returns (has_conflict, message).
    """
    conflict_msg = (
        "检测到自动化浏览器正在运行。\n\n"
        "请先关闭自动化浏览器窗口，然后再试。\n"
        "（您的日常浏览器无需关闭）"
    )

    profile_dir = Path(profile_path)

    # Chromium-based browsers write lock files while running:
    # - Windows: "lockfile" in the user-data-dir
    # - Linux/macOS: "SingletonLock" / "SingletonSocket"
    lock_files = (
        profile_dir / "lockfile",
        profile_dir / "SingletonLock",
        profile_dir / "SingletonSocket",
    )

    for lock in lock_files:
        if lock.exists():
            return True, conflict_msg

    return False, "No browser conflict detected"


def find_chrome_executable() -> str | None:
    """Find the real Chrome/Edge executable on the system.

    Searches in order:
    1. Windows Registry (most reliable on Windows)
    2. Standard installation paths
    3. PATH via shutil.which

    Returns the path to the executable, or None if not found.
    """
    system = platform.system()

    if system == "Windows" and winreg is not None:
        # Method 1: Check Windows Registry for Chrome install location
        registry_keys = (
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"),
        )
        for hive, key_path in registry_keys:
            try:
                with winreg.OpenKey(hive, key_path) as key:
                    exe_path, _ = winreg.QueryValueEx(key, "")
                    if exe_path and Path(exe_path).exists():
                        return exe_path
            except (OSError, FileNotFoundError):
                continue

    if system == "Windows":
        # Method 2: Check standard paths
        local_app = os.environ.get("LOCALAPPDATA", "")
        program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        program_files_x86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")

        candidates = []
        for root in (program_files, program_files_x86, local_app):
            if root:
                candidates.append(Path(root) / r"Google\Chrome\Application\chrome.exe")
                candidates.append(Path(root) / r"Microsoft\Edge\Application\msedge.exe")

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

    elif system == "Darwin":
        mac_paths = (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        )
        for p in mac_paths:
            if Path(p).exists():
                return p

    # Method 3: Fallback to PATH
    for name in ("chrome", "google-chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found

    return None


def _build_launch_args(
    profile_dir: str,
    extra_args: tuple[str, ...] = (),
) -> list[str]:
    """Build sanitized launch arguments for local desktop profile reuse."""
    args: list[str] = []
    if profile_dir and profile_dir != "Default":
        args.append(f"--profile-directory={profile_dir}")

    for arg in extra_args:
        if arg not in _UNSUPPORTED_LOCAL_PROFILE_FLAGS and arg not in args:
            args.append(arg)

    return args


def _classify_startup_failure(
    error_msg: str,
    page_content: str | None = None,
    page_url: str | None = None,
) -> str:
    """Classify startup failures into actionable Chinese diagnostics."""
    if page_url and page_url.lower() == "about:blank":
        return (
            "浏览器启动失败：启动后一直停留在 about:blank 空白页。\n\n"
            "这通常表示当前 Chrome/Edge 主配置目录不支持被自动化复用。\n"
            "请改用单独的浏览器配置目录或新的浏览器用户数据目录后重试。"
        )

    if page_content:
        content_lower = page_content.lower()
        if any(indicator in content_lower for indicator in _WARNING_PAGE_INDICATORS):
            return (
                "浏览器启动失败：检测到不受支持的启动参数警告页。\n\n"
                "请移除 `--no-sandbox` 等不受支持参数后重试。"
            )

    return _translate_launch_error(error_msg)


def _translate_launch_error(error_msg: str) -> str:
    """Translate Playwright launch errors into user-friendly Chinese messages."""
    lower = error_msg.lower()

    if "user data dir" in lower or "already running" in lower:
        return (
            "浏览器启动失败：配置目录被占用。\n\n"
            "请关闭所有使用该配置的浏览器窗口后重试。"
        )

    if "target page, context or browser has been closed" in lower:
        return (
            "浏览器启动后立即关闭了。\n\n"
            "可能原因：\n"
            "1. 浏览器仍在后台运行 — 请检查任务管理器\n"
            "2. 浏览器配置目录被锁定 — 请关闭所有浏览器后重试\n"
            "3. 浏览器版本不兼容 — 请更新浏览器到最新版本"
        )

    if "executable doesn't exist" in lower or "not found" in lower:
        return (
            "未找到浏览器可执行文件。\n\n"
            "请在设置中重新检测浏览器，或手动指定浏览器路径。"
        )

    if "timeout" in lower:
        return (
            "浏览器启动超时。\n\n"
            "请检查系统资源是否充足，或尝试关闭其他程序后重试。"
        )

    return f"浏览器启动失败：{error_msg}"


class BrowserEngine:
    """Manages Playwright browser lifecycle with automation profile.

    Uses a dedicated automation profile directory (not the user's daily
    browser profile). The profile_path points directly to the automation
    profile dir — no sub-profile selection needed.

    CRITICAL: Must use the user's actual installed browser (executable_path)
    instead of Playwright's bundled Chromium. Using a different Chromium
    version on the profile directory triggers a version migration/downgrade
    that corrupts profile data (cookies, extensions, bookmarks, passwords).
    """

    def __init__(
        self,
        profile_path: str,
        executable_path: str | None = None,
    ) -> None:
        self._profile_path = profile_path
        self._executable_path = executable_path
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def start(self) -> None:
        """Launch the user's own browser with their profile directory.

        CRITICAL: We MUST use executable_path to point to the user's real
        Chrome/Edge. Playwright's channel="chrome" is unreliable on Windows
        and silently falls back to bundled Chromium, which triggers a
        version downgrade that corrupts the user's profile data.
        """
        # Final safety check before launch
        has_conflict, msg = detect_browser_conflict(self._profile_path)
        if has_conflict:
            raise RuntimeError(
                "浏览器正在使用相同的配置目录，无法安全启动。\n"
                "请关闭使用该配置的浏览器窗口后重试。"
            )

        # Resolve the real browser executable — NEVER use bundled Chromium
        exe = self._executable_path or find_chrome_executable()
        if not exe:
            raise RuntimeError(
                "未找到已安装的 Chrome 或 Edge 浏览器。\n\n"
                "请安装 Google Chrome 或 Microsoft Edge，\n"
                "或在设置中点击「自动检测浏览器」。"
            )

        self._playwright = await async_playwright().start()

        # Prevent Cloudflare and other anti-bot systems from detecting automation.
        # --disable-blink-features=AutomationControlled removes navigator.webdriver=true
        args: list[str] = [
            "--disable-blink-features=AutomationControlled",
        ]

        # Playwright adds these flags by default which we must suppress:
        # --disable-extensions: prevents user extensions from loading
        # --enable-automation: triggers "Chrome is being controlled" banner
        ignore_defaults = ["--disable-extensions", "--enable-automation"]

        # Playwright defaults Chromium sandboxing to false, which can inject
        # --no-sandbox and trigger Chrome's unsupported-flag warning page.
        # Explicitly opt into sandboxing so Playwright does not add that flag.
        try:
            self._context = (
                await self._playwright.chromium.launch_persistent_context(
                    user_data_dir=self._profile_path,
                    executable_path=exe,
                    headless=False,
                    args=args,
                    ignore_default_args=ignore_defaults,
                    chromium_sandbox=True,
                )
            )

            startup_issue = await self._detect_startup_issue()
            if startup_issue:
                raise RuntimeError(startup_issue)
        except Exception as e:
            await self._cleanup_playwright()
            raise RuntimeError(
                _classify_startup_failure(str(e))
            ) from e

    async def _detect_startup_issue(self) -> str | None:
        """Detect startup states that block scraping before navigation.

        Note: about:blank is normal for the dedicated automation profile
        (empty/fresh profile). The scraper navigates to the real URL after
        start(), so about:blank at launch is not a problem.
        """
        if self._context is None or not self._context.pages:
            return (
                "浏览器启动失败：未检测到可用页面。\n\n"
                "请确认浏览器可以正常启动，并检查当前配置目录是否可复用。"
            )

        page = self._context.pages[0]
        page_url = page.url

        # about:blank is expected for the automation profile — skip check.
        if page_url.lower() == "about:blank":
            return None

        try:
            content = await page.content()
        except Exception:
            return None

        content_lower = content.lower()
        if any(indicator in content_lower for indicator in _WARNING_PAGE_INDICATORS):
            return _classify_startup_failure(
                "unsupported launch warning page",
                content,
                page_url=page_url,
            )
        return None

    async def _detect_startup_warning_page(self) -> str | None:
        """Detect browser warning pages caused by unsupported launch flags."""
        issue = await self._detect_startup_issue()
        if issue and "不受支持的启动参数警告页" in issue:
            return issue
        return None

    async def _cleanup_playwright(self) -> None:
        """Clean up Playwright instance and reset context reference."""
        self._context = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def new_page(self) -> Page:
        """Create a new page in the browser context."""
        if self._context is None:
            raise RuntimeError("Browser not started. Call start() first.")
        return await self._context.new_page()

    async def close_page(self, page: Page) -> None:
        """Close a specific page."""
        if not page.is_closed():
            await page.close()

    async def stop(self) -> None:
        """Close browser and cleanup. Never raises."""
        try:
            if self._context:
                await self._context.close()
        except Exception:
            pass
        finally:
            self._context = None
        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._playwright = None

    @staticmethod
    def detect_startup_warning_page(page_content: str) -> bool:
        """Detect warning pages caused by unsupported browser launch flags."""
        content_lower = page_content.lower()
        return any(
            indicator in content_lower
            for indicator in _WARNING_PAGE_INDICATORS
        )

    @staticmethod
    def detect_cloudflare_challenge(page_content: str, page_url: str) -> bool:
        """Detect Cloudflare Turnstile / challenge pages."""
        content_lower = page_content.lower()
        cf_indicators = [
            "challenge-platform",
            "cloudflare",
            "cf-troubleshoot",
            "id=\"verifying\"",
            "正在验证",
            "验证失败",
        ]
        url_indicators = ["challenge-platform", "/cdn-cgi/"]
        url_lower = page_url.lower()

        if any(ind in url_lower for ind in url_indicators):
            return True
        hits = sum(1 for ind in cf_indicators if ind in content_lower)
        return hits >= 2

    @staticmethod
    def detect_session_expired(page_content: str, page_url: str) -> bool:
        """Detect if the page shows a login form, indicating expired session.

        Checks for common login page indicators across panels.
        """
        login_indicators = [
            "login", "登录", "sign in", "signin", "log in",
            "password", "密码", "验证码", "captcha",
        ]
        content_lower = page_content.lower()
        url_lower = page_url.lower()

        # Check URL for login-related paths
        if any(ind in url_lower for ind in ["login", "signin", "auth"]):
            return True

        # Check page content for login form indicators (need multiple hits)
        hits = sum(1 for ind in login_indicators if ind in content_lower)
        return hits >= 2
