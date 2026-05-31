from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "search" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.cli import main
from fourdt_memory.sqlite_store import MemoryStore


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


class DoctorTests(unittest.TestCase):
    def test_doctor_initializes_missing_store(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "ready")
            self.assertTrue((storage / "db.sqlite3").exists())
            self.assertFalse((storage / "memory").exists())

    def test_doctor_uses_shared_workspace_database_without_legacy_memory_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload = run_cli(["doctor", "--workspace", str(workspace), "--json"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "memory").exists())

    def test_doctor_reports_schema_mismatch_without_migration(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            db = workspace / ".4dt" / "db.sqlite3"
            db.parent.mkdir(parents=True)

            with sqlite3.connect(db) as connection:
                connection.executescript(
                    """
                    CREATE TABLE memory_audit_log (
                      id TEXT PRIMARY KEY,
                      action TEXT NOT NULL,
                      memory_id TEXT,
                      payload_json TEXT,
                      created_at TEXT NOT NULL
                    );
                    PRAGMA user_version = 1;
                    """
                )

            exit_code, payload = run_cli(["doctor", "--workspace", str(workspace), "--json"])

            self.assertEqual(exit_code, 2)
            self.assertEqual(payload["status"], "schema_mismatch")
            self.assertEqual(payload["error"]["code"], "schema_mismatch")
            self.assertIn("memory_schema_mismatch", payload["warnings"])

    def test_doctor_reports_sqlite_and_runtime_search_backend(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Use SQLite validation for search results.",
                    source_type="task",
                    source_ref="tasks/example.md",
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["warnings"], [])
            self.assertTrue(payload["sqlite"]["ok"])
            self.assertEqual(payload["memory"]["searchBackend"], "4dt-search")
            self.assertEqual(payload["memory"]["liveItems"], 1)


if __name__ == "__main__":
    unittest.main()
