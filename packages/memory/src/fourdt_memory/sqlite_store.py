from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .migrations import migrate, schema_version
from .paths import WorkspaceIdentity, WorkspacePaths, workspace_identity, workspace_paths


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_after_seconds(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


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
            self.paths.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
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
    ) -> str:
        memory_id = new_id("mem")
        now = utc_now()
        self.connect().execute(
            """
            INSERT INTO memory_items (
              id, workspace_id, scope, type, role, content, summary, metadata_json,
              confidence, source_type, source_ref, evidence_hash, ttl_at,
              created_at, updated_at, deleted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
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

    def get_contract_entry(self, key: str) -> dict[str, Any] | None:
        row = self.connect().execute(
            """
            SELECT * FROM memory_contract_entries
            WHERE workspace_id = ? AND key = ?
            """,
            (self.identity.id, key),
        ).fetchone()
        if row is None:
            return None
        entry = dict(row)
        entry["value"] = json.loads(entry["value_json"])
        return entry

    def list_contract_entries(self) -> list[dict[str, Any]]:
        rows = self.connect().execute(
            """
            SELECT * FROM memory_contract_entries
            WHERE workspace_id = ?
            ORDER BY key ASC
            """,
            (self.identity.id,),
        ).fetchall()
        entries = []
        for row in rows:
            entry = dict(row)
            entry["value"] = json.loads(entry["value_json"])
            entries.append(entry)
        return entries

    def set_contract_entry(self, key: str, value: Any, *, value_type: str) -> dict[str, Any]:
        now = utc_now()
        value_json = json.dumps(value, sort_keys=True, ensure_ascii=False)
        self.connect().execute(
            """
            INSERT INTO memory_contract_entries (workspace_id, key, value_json, value_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(workspace_id, key) DO UPDATE SET
              value_json = excluded.value_json,
              value_type = excluded.value_type,
              updated_at = excluded.updated_at
            """,
            (self.identity.id, key, value_json, value_type, now, now),
        )
        self.connect().commit()
        self.audit("contract_set", payload={"key": key, "valueType": value_type})
        entry = self.get_contract_entry(key)
        if entry is None:
            raise RuntimeError(f"Contract entry was not saved: {key}")
        return entry

    def delete_contract_entry(self, key: str) -> bool:
        cursor = self.connect().execute(
            """
            DELETE FROM memory_contract_entries
            WHERE workspace_id = ? AND key = ?
            """,
            (self.identity.id, key),
        )
        self.connect().commit()
        deleted = cursor.rowcount > 0
        self.audit("contract_delete", payload={"key": key, "deleted": deleted})
        return deleted

    def evidence_for(self, memory_id: str) -> list[dict[str, Any]]:
        rows = self.connect().execute(
            "SELECT * FROM memory_evidence WHERE memory_id = ? ORDER BY created_at ASC",
            (memory_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def live_memory_export_rows(self) -> list[dict[str, Any]]:
        rows = []
        for item in self.list_live_memory_items():
            metadata = json.loads(item["metadata_json"])
            if not isinstance(metadata, dict):
                metadata = {}
            evidence = self.evidence_for(item["id"])
            rows.append(
                {
                    "id": item["id"],
                    "scope": item["scope"],
                    "type": item["type"],
                    "role": item["role"],
                    "content": item["content"],
                    "summary": item["summary"],
                    "metadata": metadata,
                    "confidence": item["confidence"],
                    "sourceType": item["source_type"],
                    "sourceRef": item["source_ref"],
                    "evidence": [
                        {
                            "sourceType": row["source_type"],
                            "sourceRef": row["source_ref"],
                            "quoteHash": row["quote_hash"],
                        }
                        for row in evidence
                    ],
                    "ttlAt": item["ttl_at"],
                    "createdAt": item["created_at"],
                    "updatedAt": item["updated_at"],
                }
            )
        return rows

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

    def set_session_record(self, session_id: str, state: dict[str, Any], *, ttl_seconds: int) -> str:
        expires_at = utc_after_seconds(ttl_seconds)
        self.set_session_state(session_id, {"state": state, "expiresAt": expires_at})
        return expires_at

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

    def get_session_record(self, session_id: str, *, now: str | None = None) -> dict[str, Any] | None:
        value = self.get_session_state(session_id)
        if value is None:
            return None
        if "state" not in value or "expiresAt" not in value:
            return {"state": value, "expiresAt": None, "expired": False}
        expires_at = value.get("expiresAt")
        if isinstance(expires_at, str) and expires_at <= (now or utc_now()):
            return None
        state = value.get("state")
        if not isinstance(state, dict):
            return None
        return {"state": state, "expiresAt": expires_at, "expired": False}

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
