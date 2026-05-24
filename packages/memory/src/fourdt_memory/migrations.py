from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_VERSION = 3
SCHEMA_PATH = Path(__file__).with_name("schema.sql")

CONTRACT_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS memory_contract_entries (
  workspace_id TEXT NOT NULL REFERENCES workspaces(id),
  key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  value_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (workspace_id, key)
);

CREATE INDEX IF NOT EXISTS idx_memory_contract_entries_workspace
  ON memory_contract_entries(workspace_id);
"""


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

    if current_version == 0:
        connection.executescript(schema_sql())
    elif current_version == 1:
        connection.executescript(CONTRACT_SCHEMA_SQL)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    connection.commit()
