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


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


class NoWorkspacePollutionTests(unittest.TestCase):
    def test_default_storage_stays_outside_workspace_when_explicit_root_points_elsewhere(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "outside-storage"
            sources = workspace / "sources"
            workspace.mkdir()
            sources.mkdir()
            (sources / "do-not-read.txt").write_text("sentinel", encoding="utf-8")

            exit_code, payload = run_cli(
                ["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            sqlite_path = Path(str(payload["sqlitePath"]))
            self.assertIn(storage.resolve(), sqlite_path.parents)
            self.assertNotIn(workspace.resolve(), sqlite_path.parents)
            self.assertFalse((workspace / "state.sqlite3").exists())
            self.assertEqual((sources / "do-not-read.txt").read_text(encoding="utf-8"), "sentinel")

    def test_benchmark_does_not_create_storage_or_read_sources(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            sources = workspace / "sources"
            workspace.mkdir()
            sources.mkdir()
            sentinel = sources / "do-not-read.txt"
            sentinel.write_text("sentinel", encoding="utf-8")

            exit_code, payload = run_cli(
                ["benchmark", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["sourceBoundary"], "does_not_read_sources")
            self.assertFalse(storage.exists())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "sentinel")


if __name__ == "__main__":
    unittest.main()
