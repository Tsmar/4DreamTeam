from __future__ import annotations

import contextlib
import io
import json
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
