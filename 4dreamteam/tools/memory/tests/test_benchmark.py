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


class BenchmarkTests(unittest.TestCase):
    def test_benchmark_outputs_required_modes_and_metrics_without_sources(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            storage = Path(raw_tmp) / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                ["benchmark", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "benchmark_harness")
            self.assertEqual(payload["seedFromWiki"], "deferred")
            self.assertEqual(payload["sourceBoundary"], "does_not_read_sources")
            modes = {entry["mode"]: entry["metrics"] for entry in payload["modes"]}
            self.assertEqual(set(modes), {"wiki-only", "memory-only", "memory-plus-wiki"})
            for metrics in modes.values():
                for key in (
                    "correctness",
                    "completeness",
                    "irrelevantStaleRecalls",
                    "filesRead",
                    "latencyMs",
                    "safety",
                ):
                    self.assertIn(key, metrics)


if __name__ == "__main__":
    unittest.main()
