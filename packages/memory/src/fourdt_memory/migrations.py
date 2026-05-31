from __future__ import annotations

import sqlite3
from importlib import resources


SCHEMA_VERSION = 3

CONTRACT_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS memory_contract_entries (
  key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  value_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (key)
);
"""


def schema_sql() -> str:
    return resources.files(__package__).joinpath("schema.sql").read_text(encoding="utf-8")


def schema_version(connection: sqlite3.Connection) -> int:
    row = connection.execute("PRAGMA user_version").fetchone()
    return int(row[0])


def memory_schema_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = 'memory_items'
        """
    ).fetchone()
    return row is not None


def migrate(connection: sqlite3.Connection) -> None:
    current_version = schema_version(connection)
    if current_version >= SCHEMA_VERSION:
        if not memory_schema_exists(connection):
            connection.executescript(schema_sql())
            connection.commit()
        return

    if current_version == 0:
        connection.executescript(schema_sql())
    elif current_version == 1:
        connection.executescript(CONTRACT_SCHEMA_SQL)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    connection.commit()
