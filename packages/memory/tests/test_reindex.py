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


class ReindexTests(unittest.TestCase):
    def test_reindex_checks_live_rows_without_persisted_search_index(self) -> None:
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
                    content="Check live memory only.",
                    source_type="task",
                    source_ref="tasks/live.md",
                )
                store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Expired memory is skipped.",
                    source_type="task",
                    source_ref="tasks/expired.md",
                    ttl_at="2000-01-01T00:00:00Z",
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                ["reindex", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["checkedItems"], 1)
            self.assertEqual(payload["searchBackend"], "4dt-search")
            self.assertEqual(payload["warnings"], [])


if __name__ == "__main__":
    unittest.main()
