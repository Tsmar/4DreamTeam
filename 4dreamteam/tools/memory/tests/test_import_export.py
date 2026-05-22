from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.cli import main
from fourdt_memory.sqlite_store import MemoryStore


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


class ImportExportTests(unittest.TestCase):
    def test_jsonl_export_import_round_trip_with_apply(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            fresh_workspace = tmp_path / "fresh-workspace"
            fresh_storage = tmp_path / "fresh-storage"
            export_path = tmp_path / "memory.jsonl"
            workspace.mkdir()
            fresh_workspace.mkdir()
            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                memory_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    role="lead",
                    content="Export safe accepted memory.",
                    metadata={"epic": "EPIC-0007"},
                    source_type="task",
                    source_ref="tasks/done/example.md",
                )
                store.add_evidence(memory_id, source_type="task", source_ref="tasks/done/example.md")
            finally:
                store.close()

            exit_code, payload = run_cli(
                [
                    "export",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--output",
                    str(export_path),
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "exported")
            self.assertEqual(payload["count"], 1)
            self.assertIn("export_contains_sensitive_accepted_memory", payload["warnings"])

            exit_code, payload = run_cli(
                [
                    "import",
                    str(export_path),
                    "--workspace",
                    str(fresh_workspace),
                    "--storage-root",
                    str(fresh_storage),
                    "--apply",
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "imported")
            self.assertEqual(payload["written"], 1)
            imported_store = MemoryStore(fresh_workspace, fresh_storage)
            try:
                rows = imported_store.list_live_memory_items()
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["content"], "Export safe accepted memory.")
                self.assertIsNone(rows[0]["indexed_at"])
                self.assertEqual(len(imported_store.audit_entries("import")), 1)
            finally:
                imported_store.close()

    def test_import_dry_run_writes_no_rows(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            import_path = tmp_path / "memory.jsonl"
            workspace.mkdir()
            import_path.write_text(
                json.dumps(
                    {
                        "scope": "workspace",
                        "type": "decision",
                        "content": "Dry run validates only.",
                        "sourceType": "task",
                        "sourceRef": "tasks/example.md",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code, payload = run_cli(
                ["import", str(import_path), "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "dry_run")
            self.assertEqual(payload["written"], 0)
            self.assertFalse(storage.exists())

    def test_import_blocks_unsafe_rows_without_raw_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            import_path = tmp_path / "memory.jsonl"
            workspace.mkdir()
            unsafe_content = "api_key = sk_test_12345678901234567890"
            import_path.write_text(
                json.dumps(
                    {
                        "scope": "workspace",
                        "type": "constraint",
                        "content": unsafe_content,
                        "sourceType": "task",
                        "sourceRef": "tasks/example.md",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code, payload = run_cli(
                [
                    "import",
                    str(import_path),
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--apply",
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 4)
            self.assertEqual(payload["status"], "import_rejected")
            self.assertEqual(payload["errors"][0]["code"], "unsafe_save_blocked")
            self.assertNotIn(unsafe_content, json.dumps(payload))
            self.assertFalse(storage.exists())


if __name__ == "__main__":
    unittest.main()
