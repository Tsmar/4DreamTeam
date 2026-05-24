from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.cli import main
from fourdt_memory.sqlite_store import MemoryStore


def run_cli(args: list[str]) -> tuple[int, dict[str, object], float]:
    stdout = io.StringIO()
    started = time.perf_counter()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return exit_code, json.loads(stdout.getvalue()), elapsed_ms


class PerformanceTests(unittest.TestCase):
    def test_local_memory_operations_fit_interactive_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            uninitialized_exit, _payload, doctor_cold_ms = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(uninitialized_exit, 3)

            exit_code, _payload, remember_ms = run_cli(
                [
                    "remember",
                    "Performance smoke memory uses concise accepted evidence.",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--scope",
                    "workspace",
                    "--type",
                    "decision",
                    "--source-type",
                    "task",
                    "--source-ref",
                    "tasks/performance.md",
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)

            exit_code, _payload, doctor_ready_ms = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertIn(exit_code, (0, 3))

            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                for index in range(999):
                    store.create_memory_item(
                        scope="workspace",
                        type="note",
                        content=f"Performance fixture item {index} searchable local memory.",
                        source_type="task",
                        source_ref="tasks/performance.md",
                    )
            finally:
                store.close()

            exit_code, payload, list_ms = run_cli(
                ["list", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["items"]), 1000)

            exit_code, _payload, search_ms = run_cli(
                ["search", "searchable", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)

            exit_code, _payload, reindex_ms = run_cli(
                ["reindex", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)

            export_path = tmp_path / "memory.jsonl"
            exit_code, _payload, export_ms = run_cli(
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

            import_workspace = tmp_path / "import-workspace"
            import_storage = tmp_path / "import-storage"
            import_workspace.mkdir()
            exit_code, _payload, import_dry_run_ms = run_cli(
                [
                    "import",
                    str(export_path),
                    "--workspace",
                    str(import_workspace),
                    "--storage-root",
                    str(import_storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)

            exit_code, _payload, import_apply_ms = run_cli(
                [
                    "import",
                    str(export_path),
                    "--workspace",
                    str(import_workspace),
                    "--storage-root",
                    str(import_storage),
                    "--apply",
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)

            measurements = {
                "doctorColdMs": doctor_cold_ms,
                "rememberMs": remember_ms,
                "doctorReadyMs": doctor_ready_ms,
                "list1000Ms": list_ms,
                "search1000Ms": search_ms,
                "reindex1000Ms": reindex_ms,
                "export1000Ms": export_ms,
                "importDryRun1000Ms": import_dry_run_ms,
                "importApply1000Ms": import_apply_ms,
            }
            for name, value in measurements.items():
                with self.subTest(metric=name):
                    self.assertLess(value, 10_000)


if __name__ == "__main__":
    unittest.main()
