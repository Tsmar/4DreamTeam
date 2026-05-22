from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .migrations import migrate, schema_version
from .paths import WorkspaceIdentity, WorkspacePaths, workspace_identity, workspace_paths


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class MemoryStore:
    def __init__(self, workspace: str | Path, storage_root: str | Path | None = None):
        self.workspace_path = Path(workspace).expanduser().resolve(strict=False)
        self.identity: WorkspaceIdentity = workspace_identity(self.workspace_path)
        self.paths: WorkspacePaths = workspace_paths(self.workspace_path, storage_root)
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if self.connection is None:
            self.paths.workspace_dir.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.paths.sqlite_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self) -> "MemoryStore":
        self.initialize()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def initialize(self) -> None:
        connection = self.connect()
        migrate(connection)
        self.upsert_workspace()
        self.audit("init", payload={"schemaVersion": self.schema_version()})

    def schema_version(self) -> int:
        return schema_version(self.connect())

    def upsert_workspace(self) -> None:
        now = utc_now()
        connection = self.connect()
        connection.execute(
            """
            INSERT INTO workspaces (id, display_label, root_hash, git_remote_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              display_label = excluded.display_label,
              root_hash = excluded.root_hash,
              git_remote_hash = excluded.git_remote_hash,
              updated_at = excluded.updated_at
            """,
            (
                self.identity.id,
                self.identity.display_label,
                self.identity.root_hash,
                self.identity.git_remote_hash,
                now,
                now,
            ),
        )
        connection.commit()

    def workspace_row(self) -> dict[str, Any]:
        row = self.connect().execute(
            "SELECT * FROM workspaces WHERE id = ?",
            (self.identity.id,),
        ).fetchone()
        if row is None:
            raise KeyError(self.identity.id)
        return dict(row)

    def audit(
        self,
        action: str,
        memory_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> str:
        audit_id = new_id("audit")
        self.connect().execute(
            """
            INSERT INTO memory_audit_log (id, workspace_id, action, memory_id, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                self.identity.id,
                action,
                memory_id,
                json.dumps(payload or {}, sort_keys=True),
                utc_now(),
            ),
        )
        self.connect().commit()
        return audit_id

    def create_memory_item(
        self,
        *,
        scope: str,
        type: str,
        content: str,
        role: str | None = None,
        summary: str | None = None,
        metadata: dict[str, Any] | None = None,
        confidence: float = 0.70,
        source_type: str | None = None,
        source_ref: str | None = None,
        evidence_hash: str | None = None,
        ttl_at: str | None = None,
        embedding_model: str | None = None,
        indexed_at: str | None = None,
    ) -> str:
        memory_id = new_id("mem")
        now = utc_now()
        self.connect().execute(
            """
            INSERT INTO memory_items (
              id, workspace_id, scope, type, role, content, summary, metadata_json,
              confidence, source_type, source_ref, evidence_hash, ttl_at,
              embedding_model, indexed_at, created_at, updated_at, deleted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (
                memory_id,
                self.identity.id,
                scope,
                type,
                role,
                content,
                summary,
                json.dumps(metadata or {}, sort_keys=True),
                confidence,
                source_type,
                source_ref,
                evidence_hash,
                ttl_at,
                embedding_model,
                indexed_at,
                now,
                now,
            ),
        )
        self.connect().commit()
        self.audit("remember", memory_id=memory_id, payload={"scope": scope, "type": type})
        return memory_id

    def get_memory_item(self, memory_id: str, include_deleted: bool = False) -> dict[str, Any] | None:
        clauses = ["id = ?", "workspace_id = ?"]
        params: list[Any] = [memory_id, self.identity.id]
        if not include_deleted:
            clauses.append("deleted_at IS NULL")

        row = self.connect().execute(
            f"SELECT * FROM memory_items WHERE {' AND '.join(clauses)}",
            params,
        ).fetchone()
        return dict(row) if row else None

    def list_live_memory_items(
        self,
        *,
        scope: str | None = None,
        type: str | None = None,
        role: str | None = None,
        now: str | None = None,
    ) -> list[dict[str, Any]]:
        now_value = now or utc_now()
        clauses = [
            "workspace_id = ?",
            "deleted_at IS NULL",
            "(ttl_at IS NULL OR ttl_at > ?)",
        ]
        params: list[Any] = [self.identity.id, now_value]
        if scope is not None:
            clauses.append("scope = ?")
            params.append(scope)
        if type is not None:
            clauses.append("type = ?")
            params.append(type)
        if role is not None:
            clauses.append("role = ?")
            params.append(role)

        rows = self.connect().execute(
            f"SELECT * FROM memory_items WHERE {' AND '.join(clauses)} ORDER BY created_at ASC",
            params,
        ).fetchall()
        return [dict(row) for row in rows]

    def list_live_memory_ids(self, *, now: str | None = None) -> list[str]:
        return [row["id"] for row in self.list_live_memory_items(now=now)]

    def update_index_metadata(self, memory_ids: list[str], *, embedding_model: str | None) -> None:
        if not memory_ids:
            return
        now = utc_now()
        placeholders = ", ".join("?" for _ in memory_ids)
        self.connect().execute(
            f"""
            UPDATE memory_items
            SET embedding_model = ?, indexed_at = ?, updated_at = ?
            WHERE workspace_id = ? AND id IN ({placeholders})
            """,
            [embedding_model, now, now, self.identity.id, *memory_ids],
        )
        self.connect().commit()
        self.audit(
            "reindex",
            payload={"count": len(memory_ids), "embeddingModel": embedding_model},
        )

    def soft_delete_memory_item(self, memory_id: str, reason: str) -> bool:
        now = utc_now()
        cursor = self.connect().execute(
            """
            UPDATE memory_items
            SET deleted_at = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND deleted_at IS NULL
            """,
            (now, now, memory_id, self.identity.id),
        )
        self.connect().commit()
        if cursor.rowcount:
            self.audit("forget", memory_id=memory_id, payload={"reason": reason})
            return True
        return False

    def add_evidence(
        self,
        memory_id: str,
        *,
        source_type: str,
        source_ref: str | None = None,
        quote_hash: str | None = None,
    ) -> str:
        evidence_id = new_id("evi")
        self.connect().execute(
            """
            INSERT INTO memory_evidence (id, memory_id, source_type, source_ref, quote_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (evidence_id, memory_id, source_type, source_ref, quote_hash, utc_now()),
        )
        self.connect().commit()
        return evidence_id

    def evidence_for(self, memory_id: str) -> list[dict[str, Any]]:
        rows = self.connect().execute(
            "SELECT * FROM memory_evidence WHERE memory_id = ? ORDER BY created_at ASC",
            (memory_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def set_session_state(self, session_id: str, state: dict[str, Any]) -> None:
        now = utc_now()
        state_json = json.dumps(state, sort_keys=True)
        self.connect().execute(
            """
            INSERT INTO agent_sessions (id, workspace_id, state_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              state_json = excluded.state_json,
              updated_at = excluded.updated_at
            """,
            (session_id, self.identity.id, state_json, now, now),
        )
        self.connect().commit()
        self.audit("session_set", payload={"sessionId": session_id})

    def get_session_state(self, session_id: str) -> dict[str, Any] | None:
        row = self.connect().execute(
            "SELECT state_json FROM agent_sessions WHERE id = ? AND workspace_id = ?",
            (session_id, self.identity.id),
        ).fetchone()
        if row is None:
            return None
        value = json.loads(row["state_json"])
        if not isinstance(value, dict):
            raise ValueError("Session state must be a JSON object")
        return value

    def audit_entries(self, action: str | None = None) -> list[dict[str, Any]]:
        clauses = ["workspace_id = ?"]
        params: list[Any] = [self.identity.id]
        if action is not None:
            clauses.append("action = ?")
            params.append(action)
        rows = self.connect().execute(
            f"SELECT * FROM memory_audit_log WHERE {' AND '.join(clauses)} ORDER BY created_at ASC",
            params,
        ).fetchall()
        return [dict(row) for row in rows]
