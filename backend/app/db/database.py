"""SQLite connection utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.app.config import DB_PATH
from backend.app.db.schema import SCHEMA_SQL


def get_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection with row dictionaries enabled."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: Path = DB_PATH) -> None:
    """Create database tables if they do not exist."""
    with get_connection(path) as conn:
        conn.executescript(SCHEMA_SQL)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(user_settings)").fetchall()}
        if "avoid_penny_stocks" not in columns:
            conn.execute("ALTER TABLE user_settings ADD COLUMN avoid_penny_stocks INTEGER NOT NULL DEFAULT 1")
