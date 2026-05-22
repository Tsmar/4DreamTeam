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


class RememberTests(unittest.TestCase):
    def test_remember_workspace_memory_creates_item_evidence_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "remember",
                    "Source-approved decision: store memory outside the workspace.",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--scope",
                    "workspace",
                    "--type",
                    "decision",
                    "--role",
                    "lead",
                    "--source-type",
                    "task",
                    "--source-ref",
                    "tasks/done/EPIC-0007-TASK-0029.md",
                    "--metadata-json",
                    '{"epic":"EPIC-0007"}',
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "remembered")
            self.assertEqual(payload["scope"], "workspace")
            self.assertEqual(payload["type"], "decision")
            self.assertEqual(payload["role"], "lead")
            self.assertEqual(payload["sourceType"], "task")
            self.assertEqual(payload["sourceRef"], "tasks/done/EPIC-0007-TASK-0029.md")
            self.assertEqual(payload["confidence"], 0.70)
            self.assertIsNone(payload["indexedAt"])

            store = MemoryStore(workspace, storage)
            try:
                item = store.get_memory_item(str(payload["id"]))
                self.assertIsNotNone(item)
                self.assertEqual(json.loads(item["metadata_json"]), {"epic": "EPIC-0007"})
                evidence = store.evidence_for(str(payload["id"]))
                self.assertEqual(len(evidence), 1)
                self.assertEqual(evidence[0]["source_type"], "task")
                self.assertEqual(evidence[0]["source_ref"], "tasks/done/EPIC-0007-TASK-0029.md")
                remembers = store.audit_entries("remember")
                self.assertEqual(len(remembers), 1)
                self.assertNotIn("Source-approved decision", remembers[0]["payload_json"])
            finally:
                store.close()

    def test_workspace_memory_requires_source_ref(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "remember",
                    "Use source references for durable memory.",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--scope",
                    "workspace",
                    "--type",
                    "constraint",
                    "--source-type",
                    "task",
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "missing_source_ref")
            self.assertFalse(storage.exists())

    def test_user_preference_allows_explicit_user_source_without_source_ref(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "remember",
                    "User prefers concise responses in Russian.",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--scope",
                    "user",
                    "--type",
                    "preference",
                    "--source-type",
                    "user",
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["sourceType"], "user")
            self.assertIsNone(payload["sourceRef"])


if __name__ == "__main__":
    unittest.main()
