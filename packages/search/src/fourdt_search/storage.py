from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .records import SearchChunk

RUNTIME_ROOT = Path(".4dt")
SEARCH_MANIFEST_ID = "default"


def sqlite_path(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "db.sqlite3"


def connect(workspace: Path) -> sqlite3.Connection:
    (workspace / RUNTIME_ROOT).mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path(workspace))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    ensure_schema(connection)
    return connection


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS search_chunks (
          id TEXT PRIMARY KEY,
          domain TEXT NOT NULL,
          kind TEXT NOT NULL,
          authority TEXT NOT NULL,
          title TEXT NOT NULL DEFAULT '',
          path TEXT NOT NULL DEFAULT '',
          source_id TEXT NOT NULL DEFAULT '',
          page_id TEXT NOT NULL DEFAULT '',
          item_id TEXT NOT NULL DEFAULT '',
          line_start INTEGER,
          line_end INTEGER,
          section TEXT NOT NULL DEFAULT '',
          entry_id TEXT NOT NULL DEFAULT '',
          metadata_json TEXT NOT NULL DEFAULT '{}',
          text TEXT NOT NULL,
          content_hash TEXT NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_chunks_domain ON search_chunks(domain)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_search_chunks_content_hash ON search_chunks(content_hash)")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS search_manifest (
          id TEXT PRIMARY KEY,
          manifest_json TEXT NOT NULL,
          generated_at TEXT NOT NULL
        )
        """
    )
    connection.commit()


def chunk_values(chunk: SearchChunk) -> tuple[Any, ...]:
    return (
        chunk.id,
        chunk.domain,
        chunk.kind,
        chunk.authority,
        chunk.title,
        chunk.path,
        chunk.source_id,
        chunk.page_id,
        chunk.item_id,
        chunk.line_start,
        chunk.line_end,
        chunk.section,
        chunk.entry_id,
        json.dumps(chunk.metadata, ensure_ascii=False, sort_keys=True),
        chunk.text,
        chunk.content_hash,
    )


def chunk_from_row(row: sqlite3.Row) -> SearchChunk:
    try:
        metadata = json.loads(row["metadata_json"])
    except json.JSONDecodeError:
        metadata = {}
    return SearchChunk(
        id=row["id"],
        domain=row["domain"],
        kind=row["kind"],
        authority=row["authority"],
        title=row["title"],
        path=row["path"],
        source_id=row["source_id"],
        page_id=row["page_id"],
        item_id=row["item_id"],
        line_start=row["line_start"],
        line_end=row["line_end"],
        section=row["section"],
        entry_id=row["entry_id"],
        metadata=metadata if isinstance(metadata, dict) else {},
        text=row["text"],
        content_hash=row["content_hash"],
    )


def write_chunks(workspace: Path, chunks: list[SearchChunk]) -> None:
    connection = connect(workspace)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM search_chunks")
        connection.executemany(
            """
            INSERT INTO search_chunks (
              id, domain, kind, authority, title, path, source_id, page_id, item_id,
              line_start, line_end, section, entry_id, metadata_json, text, content_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [chunk_values(chunk) for chunk in chunks],
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def read_chunks(workspace: Path) -> list[SearchChunk]:
    connection = connect(workspace)
    try:
        rows = connection.execute("SELECT * FROM search_chunks ORDER BY domain, id").fetchall()
        return [chunk_from_row(row) for row in rows]
    finally:
        connection.close()


def find_chunk(workspace: Path, result_id: str) -> SearchChunk | None:
    connection = connect(workspace)
    try:
        row = connection.execute("SELECT * FROM search_chunks WHERE id = ?", (result_id,)).fetchone()
        return chunk_from_row(row) if row is not None else None
    finally:
        connection.close()


def write_manifest(workspace: Path, value: dict[str, Any]) -> None:
    connection = connect(workspace)
    try:
        connection.execute(
            """
            INSERT INTO search_manifest (id, manifest_json, generated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              manifest_json = excluded.manifest_json,
              generated_at = excluded.generated_at
            """,
            (
                SEARCH_MANIFEST_ID,
                json.dumps(value, ensure_ascii=False, sort_keys=True),
                str(value.get("generatedAt", "")),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def read_manifest(workspace: Path) -> dict[str, Any]:
    connection = connect(workspace)
    try:
        row = connection.execute("SELECT manifest_json FROM search_manifest WHERE id = ?", (SEARCH_MANIFEST_ID,)).fetchone()
    finally:
        connection.close()
    if row is None:
        return {}
    try:
        value = json.loads(row["manifest_json"])
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def has_chunks(workspace: Path) -> bool:
    connection = connect(workspace)
    try:
        row = connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'search_chunks'").fetchone()
        return row is not None
    finally:
        connection.close()


def index_bytes(workspace: Path) -> int:
    path = sqlite_path(workspace)
    return path.stat().st_size if path.exists() else 0
