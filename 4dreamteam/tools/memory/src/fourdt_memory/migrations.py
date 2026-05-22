from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_VERSION = 1
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def schema_sql() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def schema_version(connection: sqlite3.Connection) -> int:
    row = connection.execute("PRAGMA user_version").fetchone()
    return int(row[0])


def migrate(connection: sqlite3.Connection) -> None:
    current_version = schema_version(connection)
    if current_version > SCHEMA_VERSION:
        raise RuntimeError(
            f"Database schema version {current_version} is newer than supported {SCHEMA_VERSION}"
        )
    if current_version == SCHEMA_VERSION:
        return

    connection.executescript(schema_sql())
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    connection.commit()
