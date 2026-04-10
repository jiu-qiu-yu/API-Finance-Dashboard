"""SQLite database initialization and connection management."""

import sqlite3
from pathlib import Path

# Default database path in user's app data directory
DEFAULT_DB_PATH = Path.home() / ".api-finance-dashboard" / "data.db"

SCHEMA_VERSION = 2

_CREATE_SITES_TABLE = """
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('main', 'upstream')),
    url TEXT NOT NULL,
    panel_type TEXT NOT NULL DEFAULT 'custom',
    css_selector TEXT DEFAULT NULL,
    regex_pattern TEXT DEFAULT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    alert_threshold REAL DEFAULT NULL,
    dashboard_url TEXT DEFAULT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

_CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

_CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Get a database connection. Creates the database directory if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


_MIGRATIONS = {
    2: [
        "ALTER TABLE sites ADD COLUMN dashboard_url TEXT DEFAULT NULL",
    ],
}


def _run_migrations(conn: sqlite3.Connection, current_version: int) -> None:
    """Apply pending migrations from current_version up to SCHEMA_VERSION."""
    for version in range(current_version + 1, SCHEMA_VERSION + 1):
        statements = _MIGRATIONS.get(version, [])
        for stmt in statements:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                # Column/table already exists — skip
                pass
        conn.execute(
            "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
            (version,),
        )


def init_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Initialize the database schema. Safe to call multiple times."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(_CREATE_SCHEMA_VERSION_TABLE)
            conn.execute(_CREATE_SITES_TABLE)
            conn.execute(_CREATE_SETTINGS_TABLE)

            row = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            current = row["version"] if row else 0

            if current == 0:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (SCHEMA_VERSION,),
                )
            elif current < SCHEMA_VERSION:
                _run_migrations(conn, current)
    finally:
        conn.close()
