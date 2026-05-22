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


class ForgetTests(unittest.TestCase):
    def test_forget_soft_deletes_memory_and_list_excludes_it(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                memory_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Use soft delete for forget.",
                    source_type="task",
                    source_ref="tasks/done/example.md",
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                [
                    "forget",
                    memory_id,
                    "--reason",
                    "superseded by operator decision",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "forgotten")
            self.assertTrue(payload["deleted"])

            exit_code, payload = run_cli(
                ["list", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["items"], [])

            store = MemoryStore(workspace, storage)
            try:
                self.assertIsNone(store.get_memory_item(memory_id))
                self.assertIsNotNone(store.get_memory_item(memory_id, include_deleted=True))
                forgets = store.audit_entries("forget")
                self.assertEqual(len(forgets), 1)
                self.assertIn("superseded by operator decision", forgets[0]["payload_json"])
                self.assertNotIn("Use soft delete", forgets[0]["payload_json"])
            finally:
                store.close()

    def test_forget_missing_item_returns_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            run_cli(["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"])

            exit_code, payload = run_cli(
                [
                    "forget",
                    "mem_missing",
                    "--reason",
                    "cleanup",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
