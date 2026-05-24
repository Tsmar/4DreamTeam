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


class DegradedModeTests(unittest.TestCase):
    def test_initialized_search_is_ready_without_optional_runtime_dependencies(self) -> None:
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
                    type="constraint",
                    content="Runtime search remains available.",
                    source_type="task",
                    source_ref="tasks/example.md",
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                ["search", "runtime", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["warnings"], [])
            self.assertEqual(payload["recovery"], [])


if __name__ == "__main__":
    unittest.main()
