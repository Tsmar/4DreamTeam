from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.sqlite_store import MemoryStore


def make_store(tmp_path: Path) -> tuple[MemoryStore, Path, Path]:
    workspace = tmp_path / "workspace"
    storage = tmp_path / "storage"
    workspace.mkdir()
    store = MemoryStore(workspace, storage)
    store.initialize()
    return store, workspace, storage


class StoreTests(unittest.TestCase):
    def test_initialize_creates_sqlite_under_storage_root_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            store, workspace, storage = make_store(Path(raw_tmp))
            try:
                self.assertTrue(store.paths.sqlite_path.exists())
                self.assertIn(storage.resolve(), store.paths.sqlite_path.parents)
                self.assertNotIn(workspace.resolve(), store.paths.sqlite_path.parents)
                self.assertFalse((workspace / "state.sqlite3").exists())
            finally:
                store.close()

    def test_workspace_row_is_idempotent_and_avoids_raw_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            store, workspace, _storage = make_store(Path(raw_tmp))
            try:
                first = store.workspace_row()
                store.upsert_workspace()
                second = store.workspace_row()

                self.assertEqual(first["id"], second["id"])
                self.assertNotIn("root_path", first)
                self.assertNotIn(str(workspace.resolve()), str(first))
            finally:
                store.close()

    def test_schema_version_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            store, _workspace, _storage = make_store(Path(raw_tmp))
            try:
                self.assertEqual(store.schema_version(), 2)
            finally:
                store.close()

    def test_v1_database_migrates_contract_entries(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            store = MemoryStore(workspace, storage)
            connection = store.connect()
            connection.executescript(
                """
                CREATE TABLE workspaces (
                  id TEXT PRIMARY KEY,
                  display_label TEXT NOT NULL,
                  root_hash TEXT NOT NULL,
                  git_remote_hash TEXT,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE TABLE memory_audit_log (
                  id TEXT PRIMARY KEY,
                  workspace_id TEXT NOT NULL REFERENCES workspaces(id),
                  action TEXT NOT NULL,
                  memory_id TEXT,
                  payload_json TEXT,
                  created_at TEXT NOT NULL
                );

                PRAGMA user_version = 1;
                """
            )
            store.close()

            migrated = MemoryStore(workspace, storage)
            try:
                migrated.initialize()
                self.assertEqual(migrated.schema_version(), 2)
                entry = migrated.set_contract_entry("project.rules", "Use contract onboarding.", value_type="text")
                self.assertEqual(entry["value"], "Use contract onboarding.")
            finally:
                migrated.close()

    def test_memory_crud_live_filtering_and_soft_delete(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            store, _workspace, _storage = make_store(Path(raw_tmp))
            try:
                live_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    role="lead",
                    content="Use local memory storage.",
                    source_type="report",
                    source_ref="reports/example.md",
                )
                expired_id = store.create_memory_item(
                    scope="workspace",
                    type="note",
                    content="Expired note.",
                    ttl_at="2000-01-01T00:00:00Z",
                )

                live_rows = store.list_live_memory_items(now="2026-01-01T00:00:00Z")
                self.assertEqual([row["id"] for row in live_rows], [live_id])
                self.assertIsNotNone(store.get_memory_item(expired_id))

                self.assertTrue(store.soft_delete_memory_item(live_id, "test cleanup"))
                self.assertIsNone(store.get_memory_item(live_id))
                self.assertIsNotNone(store.get_memory_item(live_id, include_deleted=True))
                self.assertEqual(store.list_live_memory_items(now="2026-01-01T00:00:00Z"), [])
            finally:
                store.close()

    def test_evidence_session_and_audit_entries(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            store, _workspace, _storage = make_store(Path(raw_tmp))
            try:
                memory_id = store.create_memory_item(
                    scope="workspace",
                    type="constraint",
                    content="Do not read sources before approval.",
                    source_type="handoff",
                    source_ref="reports/handoffs/example.md",
                )
                evidence_id = store.add_evidence(
                    memory_id,
                    source_type="handoff",
                    source_ref="reports/handoffs/example.md",
                    quote_hash="abc123",
                )

                evidence = store.evidence_for(memory_id)
                self.assertEqual(evidence[0]["id"], evidence_id)
                self.assertEqual(evidence[0]["quote_hash"], "abc123")

                store.set_session_state("session-1", {"step": "storage"})
                self.assertEqual(store.get_session_state("session-1"), {"step": "storage"})

                actions = [entry["action"] for entry in store.audit_entries()]
                self.assertIn("init", actions)
                self.assertIn("remember", actions)
                self.assertIn("session_set", actions)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
