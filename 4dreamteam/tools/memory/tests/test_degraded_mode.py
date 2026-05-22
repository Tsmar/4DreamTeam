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


class DegradedModeTests(unittest.TestCase):
    def test_search_uses_lexical_fallback_when_semantic_index_is_unavailable(self) -> None:
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
                    content="Fallback search remains recoverable.",
                    source_type="task",
                    source_ref="tasks/example.md",
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                [
                    "search",
                    "fallback",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--embedding-provider",
                    "hash",
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 3)
            self.assertEqual(payload["status"], "degraded")
            self.assertIn("semantic_index_unavailable", payload["warnings"])
            self.assertIn("using_lexical_fallback", payload["warnings"])


if __name__ == "__main__":
    unittest.main()
