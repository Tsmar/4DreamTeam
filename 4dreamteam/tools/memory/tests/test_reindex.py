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
from fourdt_memory.embedder import HashEmbeddingProvider
from fourdt_memory.sqlite_store import MemoryStore


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


class ReindexTests(unittest.TestCase):
    def test_reindex_marks_live_rows_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                live_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Index live memory only.",
                    source_type="task",
                    source_ref="tasks/live.md",
                )
                expired_id = store.create_memory_item(
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
                [
                    "reindex",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--embedding-provider",
                    "none",
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "degraded_intentional_fallback")
            self.assertEqual(payload["indexedItems"], 1)
            self.assertIn("using_lexical_fallback", payload["warnings"])
            store = MemoryStore(workspace, storage)
            try:
                live = store.get_memory_item(live_id)
                expired = store.get_memory_item(expired_id)
                self.assertEqual(live["embedding_model"], "none:lexical")
                self.assertIsNotNone(live["indexed_at"])
                self.assertIsNone(expired["indexed_at"])
            finally:
                store.close()

    def test_hash_embedding_is_deterministic(self) -> None:
        provider = HashEmbeddingProvider()
        self.assertEqual(provider.embed("repeatable memory"), provider.embed("repeatable memory"))
        self.assertNotEqual(provider.embed("repeatable memory"), provider.embed("different memory"))


if __name__ == "__main__":
    unittest.main()
