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
from fourdt_memory.lance_index import LanceIndex
from fourdt_memory.sqlite_store import MemoryStore


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


class DoctorTests(unittest.TestCase):
    def test_doctor_missing_store_is_non_mutating_degraded_status(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["status"], "degraded_setup_required")
            self.assertIn("memory_store_not_initialized", payload["warnings"])
            self.assertIn("recovery", payload)
            self.assertFalse(storage.exists())

    def test_doctor_reports_index_counts_and_mismatch_warning(self) -> None:
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
                    content="Use SQLite validation for search results.",
                    source_type="task",
                    source_ref="tasks/example.md",
                )
                store.update_index_metadata([memory_id], embedding_model="hash:sha256-16")
                index = LanceIndex(store.paths.lancedb_dir)
                index.rebuild(
                    provider_model="hash:sha256-16",
                    items=[
                        {"id": memory_id, "vector": [1.0], "providerModel": "hash:sha256-16"},
                        {"id": "mem_missing", "vector": [0.0], "providerModel": "hash:sha256-16"},
                    ],
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            self.assertEqual(payload["status"], "degraded_setup_required")
            self.assertEqual(payload["lancedb"]["indexedItems"], 2)
            self.assertIn("index_missing_sqlite_rows", payload["warnings"])

    def test_doctor_reports_intentional_fallback_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            store = MemoryStore(workspace, storage)
            store.initialize()
            store.close()

            exit_code, payload = run_cli(
                [
                    "doctor",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--intentional-fallback",
                    "--json",
                ]
            )

            self.assertIn(exit_code, (0, 3))
            if payload["warnings"]:
                self.assertEqual(payload["status"], "degraded_intentional_fallback")
                self.assertIn("Intentional lexical fallback is active.", payload["recovery"])


if __name__ == "__main__":
    unittest.main()
