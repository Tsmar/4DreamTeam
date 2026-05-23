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


class SearchTests(unittest.TestCase):
    def test_search_returns_stable_degraded_json_with_previews(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            long_content = "SQLite authoritative validation " + ("details " * 40)
            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                memory_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    role="lead",
                    content=long_content,
                    source_type="task",
                    source_ref="tasks/example.md",
                )
            finally:
                store.close()

            exit_code, payload = run_cli(
                ["search", "SQLite validation", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "degraded_setup_required")
            self.assertEqual(payload["query"], "SQLite validation")
            self.assertIn("using_lexical_fallback", payload["warnings"])
            self.assertEqual(payload["items"][0]["id"], memory_id)
            self.assertIn("preview", payload["items"][0])
            self.assertNotIn("content", payload["items"][0])
            self.assertLessEqual(len(payload["items"][0]["preview"]), 160)

    def test_deleted_and_expired_rows_are_excluded_from_search(self) -> None:
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
                    content="Memory search should find live validation.",
                    source_type="task",
                    source_ref="tasks/live.md",
                )
                deleted_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Memory search should not find deleted validation.",
                    source_type="task",
                    source_ref="tasks/deleted.md",
                )
                expired_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Memory search should not find expired validation.",
                    source_type="task",
                    source_ref="tasks/expired.md",
                    ttl_at="2000-01-01T00:00:00Z",
                )
                store.soft_delete_memory_item(deleted_id, "test")
            finally:
                store.close()

            exit_code, payload = run_cli(
                ["search", "validation", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            ids = [item["id"] for item in payload["items"]]
            self.assertEqual(ids, [live_id])
            self.assertNotIn(deleted_id, ids)
            self.assertNotIn(expired_id, ids)

    def test_hash_index_results_are_validated_through_sqlite(self) -> None:
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
                    content="Vector search validates live SQLite rows.",
                    source_type="task",
                    source_ref="tasks/live.md",
                )
                deleted_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Vector search ignores deleted rows.",
                    source_type="task",
                    source_ref="tasks/deleted.md",
                )
                store.soft_delete_memory_item(deleted_id, "test")
            finally:
                store.close()

            run_cli(
                [
                    "reindex",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--embedding-provider",
                    "hash",
                    "--json",
                ]
            )
            index = LanceIndex(MemoryStore(workspace, storage).paths.lancedb_dir)
            data = index.read()
            data["items"].append({"id": deleted_id, "vector": [1.0] * 16, "providerModel": "hash:sha256-16"})
            data["items"].append({"id": "mem_missing", "vector": [1.0] * 16, "providerModel": "hash:sha256-16"})
            index.rebuild(provider_model="hash:sha256-16", items=data["items"])

            exit_code, payload = run_cli(
                [
                    "search",
                    "vector search",
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
            ids = [item["id"] for item in payload["items"]]
            self.assertEqual(ids, [live_id])
            self.assertNotIn(deleted_id, ids)
            self.assertNotIn("mem_missing", ids)


if __name__ == "__main__":
    unittest.main()
