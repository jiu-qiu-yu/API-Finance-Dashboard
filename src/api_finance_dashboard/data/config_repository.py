"""Repository for key-value application settings."""

import sqlite3
from pathlib import Path

from api_finance_dashboard.data.database import DEFAULT_DB_PATH, get_connection


class ConfigRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def get(self, key: str, default: str | None = None) -> str | None:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default
        finally:
            conn.close()

    def set(self, key: str, value: str) -> None:
        conn = self._conn()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (key, value),
                )
        finally:
            conn.close()

    def delete(self, key: str) -> bool:
        conn = self._conn()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM settings WHERE key = ?", (key,))
                return cursor.rowcount > 0
        finally:
            conn.close()

    def get_all(self) -> dict[str, str]:
        conn = self._conn()
        try:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            return {row["key"]: row["value"] for row in rows}
        finally:
            conn.close()

    # Convenience accessors for common settings
    def get_browser_path(self) -> str | None:
        return self.get("browser_profile_path")

    def set_browser_path(self, path: str) -> None:
        self.set("browser_profile_path", path)

    def get_exchange_rate(self) -> str:
        return self.get("exchange_rate", "7.2")

    def set_exchange_rate(self, rate: str) -> None:
        self.set("exchange_rate", rate)

    def get_display_currency(self) -> str:
        return self.get("display_currency", "CNY")

    def set_display_currency(self, currency: str) -> None:
        self.set("display_currency", currency)

    def get_browser_type(self) -> str | None:
        return self.get("browser_type")

    def set_browser_type(self, browser_type: str) -> None:
        self.set("browser_type", browser_type)

    def get_browser_profile_dir(self) -> str:
        return self.get("browser_profile_dir", "Default")

    def set_browser_profile_dir(self, profile_dir: str) -> None:
        self.set("browser_profile_dir", profile_dir)

    def get_browser_executable(self) -> str | None:
        return self.get("browser_executable")

    def set_browser_executable(self, path: str) -> None:
        self.set("browser_executable", path)

    def get_automation_profile_path(self) -> str:
        """Return the automation profile directory path.

        If no value is stored, auto-resolves and persists the default path.
        """
        path = self.get("automation_profile_path")
        if path:
            return path
        from api_finance_dashboard.engine.automation_profile import (
            get_default_automation_profile_dir,
        )
        default = str(get_default_automation_profile_dir())
        self.set_automation_profile_path(default)
        return default

    def set_automation_profile_path(self, path: str) -> None:
        self.set("automation_profile_path", path)
