"""Repository for site configuration CRUD operations."""

import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from api_finance_dashboard.data.database import DEFAULT_DB_PATH, get_connection
from api_finance_dashboard.data.models import Currency, SiteConfig, SiteType


def _row_to_site(row: sqlite3.Row) -> SiteConfig:
    return SiteConfig(
        id=row["id"],
        name=row["name"],
        type=SiteType(row["type"]),
        url=row["url"],
        panel_type=row["panel_type"],
        css_selector=row["css_selector"],
        regex_pattern=row["regex_pattern"],
        currency=Currency(row["currency"]),
        alert_threshold=Decimal(str(row["alert_threshold"])) if row["alert_threshold"] is not None else None,
        dashboard_url=row["dashboard_url"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class SiteRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection:
        return get_connection(self._db_path)

    def get_all(self) -> list[SiteConfig]:
        """Get all sites ordered by type (main first) then name."""
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT * FROM sites ORDER BY "
                "CASE type WHEN 'main' THEN 0 ELSE 1 END, name"
            ).fetchall()
            return [_row_to_site(r) for r in rows]
        finally:
            conn.close()

    def get_by_id(self, site_id: int) -> SiteConfig | None:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT * FROM sites WHERE id = ?", (site_id,)
            ).fetchone()
            return _row_to_site(row) if row else None
        finally:
            conn.close()

    def create(
        self,
        name: str,
        site_type: SiteType,
        url: str,
        panel_type: str = "custom",
        css_selector: str | None = None,
        regex_pattern: str | None = None,
        currency: Currency = Currency.USD,
        alert_threshold: Decimal | None = None,
        dashboard_url: str | None = None,
    ) -> SiteConfig:
        conn = self._conn()
        try:
            now = datetime.now().isoformat()
            with conn:
                cursor = conn.execute(
                    """INSERT INTO sites (name, type, url, panel_type, css_selector,
                       regex_pattern, currency, alert_threshold, dashboard_url,
                       created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        name,
                        site_type.value,
                        url,
                        panel_type,
                        css_selector,
                        regex_pattern,
                        currency.value,
                        float(alert_threshold) if alert_threshold is not None else None,
                        dashboard_url,
                        now,
                        now,
                    ),
                )
                row = conn.execute(
                    "SELECT * FROM sites WHERE id = ?", (cursor.lastrowid,)
                ).fetchone()
                return _row_to_site(row)
        finally:
            conn.close()

    def update(self, site_id: int, **kwargs) -> SiteConfig | None:
        """Update site fields. Accepts any SiteConfig field name as keyword argument."""
        allowed = {
            "name", "type", "url", "panel_type", "css_selector",
            "regex_pattern", "currency", "alert_threshold", "dashboard_url",
        }
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get_by_id(site_id)

        # Convert enums to their values for storage
        if "type" in updates and isinstance(updates["type"], SiteType):
            updates["type"] = updates["type"].value
        if "currency" in updates and isinstance(updates["currency"], Currency):
            updates["currency"] = updates["currency"].value
        if "alert_threshold" in updates and updates["alert_threshold"] is not None:
            updates["alert_threshold"] = float(updates["alert_threshold"])

        updates["updated_at"] = datetime.now().isoformat()

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [site_id]

        conn = self._conn()
        try:
            with conn:
                conn.execute(
                    f"UPDATE sites SET {set_clause} WHERE id = ?", values
                )
            return self.get_by_id(site_id)
        finally:
            conn.close()

    def delete(self, site_id: int) -> bool:
        conn = self._conn()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM sites WHERE id = ?", (site_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()
