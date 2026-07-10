from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import DATABASE_URL


def _sqlite_path(database_url: str = DATABASE_URL) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// database URLs are supported in this starter project.")
    return Path(database_url.replace("sqlite:///", "", 1))


def get_connection(database_url: str = DATABASE_URL) -> sqlite3.Connection:
    db_path = _sqlite_path(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_url: str = DATABASE_URL) -> None:
    with get_connection(database_url) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                summary TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        connection.commit()
