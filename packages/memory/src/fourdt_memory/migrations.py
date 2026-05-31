from __future__ import annotations

import sqlite3
import hashlib
from importlib import resources


SCHEMA_VERSION = 3
SCHEMA_DOMAIN = "memory"
TOOL_VERSION = "0.5.8"
REQUIRED_TABLES = {
    "memory_items",
    "memory_evidence",
    "memory_agent_sessions",
    "memory_audit_log",
    "memory_contract_entries",
}


class SchemaMismatch(sqlite3.DatabaseError):
    """Raised when an existing memory schema needs operator-controlled migration."""


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


def memory_tables(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name LIKE 'memory_%'
        """
    ).fetchall()
    return {str(row[0]) for row in rows}


def ensure_schema_registry(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tool_schema_versions (
          domain TEXT PRIMARY KEY,
          schema_version INTEGER NOT NULL,
          schema_hash TEXT NOT NULL,
          tool_version TEXT NOT NULL DEFAULT '',
          applied_at TEXT NOT NULL
        )
        """
    )


def record_schema_version(connection: sqlite3.Connection, schema_text: str) -> None:
    ensure_schema_registry(connection)
    connection.execute(
        """
        INSERT INTO tool_schema_versions (domain, schema_version, schema_hash, tool_version, applied_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        ON CONFLICT(domain) DO UPDATE SET
          schema_version = excluded.schema_version,
          schema_hash = excluded.schema_hash,
          tool_version = excluded.tool_version,
          applied_at = excluded.applied_at
        """,
        (SCHEMA_DOMAIN, SCHEMA_VERSION, hashlib.sha256(schema_text.encode("utf-8")).hexdigest(), TOOL_VERSION),
    )


def ensure_current_schema(connection: sqlite3.Connection) -> None:
    current_version = schema_version(connection)
    existing_tables = memory_tables(connection)
    text = schema_sql()
    if not existing_tables:
        connection.executescript(text)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        record_schema_version(connection, text)
        connection.commit()
        return

    missing = REQUIRED_TABLES - existing_tables
    if current_version != SCHEMA_VERSION or missing:
        detail = f"version={current_version}, expected={SCHEMA_VERSION}"
        if missing:
            detail += f", missing={','.join(sorted(missing))}"
        raise SchemaMismatch(f"Memory schema mismatch ({detail}).")
    record_schema_version(connection, text)
    connection.commit()
