"""Cross-platform notification system."""

import platform
import subprocess
import sys
from decimal import Decimal

# Hide console window when spawning subprocesses on Windows
_SUBPROCESS_FLAGS = (
    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
)

from api_finance_dashboard.data.models import SiteResult, SiteStatus


def _notify_windows(title: str, message: str) -> None:
    """Send Windows Toast notification via PowerShell."""
    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast duration="short">
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
        <audio src="ms-winsoundevent:Notification.Default"/>
    </toast>
"@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("API Finance Dashboard").Show($toast)
    """
    try:
        subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, timeout=10,
            creationflags=_SUBPROCESS_FLAGS,
        )
    except Exception:
        # Fallback: use plyer
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=10)
        except Exception:
            pass


def _notify_macos(title: str, message: str) -> None:
    """Send macOS notification via osascript."""
    script = (
        f'display notification "{message}" with title "{title}" sound name "default"'
    )
    try:
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, timeout=10,
            creationflags=_SUBPROCESS_FLAGS,
        )
    except Exception:
        pass


def send_notification(title: str, message: str) -> None:
    """Send a system notification (cross-platform)."""
    system = platform.system()
    if system == "Windows":
        _notify_windows(title, message)
    elif system == "Darwin":
        _notify_macos(title, message)


def check_and_alert(site_results: list[SiteResult]) -> list[str]:
    """Check all results for low balance and send alerts.

    Returns list of alert messages sent.
    """
    alerts = []
    for result in site_results:
        if result.status == SiteStatus.LOW_BALANCE and result.balance is not None:
            threshold = result.site.alert_threshold or Decimal("0")
            currency_symbol = "￥" if result.site.currency.value == "CNY" else "$"
            msg = (
                f"{result.site.name} 余额 {currency_symbol}{result.balance}，"
                f"低于阈值 {currency_symbol}{threshold}"
            )
            alerts.append(msg)

    if alerts:
        title = "额度告警"
        message = "\n".join(alerts)
        send_notification(title, message)

    return alerts
