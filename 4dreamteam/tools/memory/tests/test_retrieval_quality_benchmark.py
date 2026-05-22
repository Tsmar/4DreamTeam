from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.benchmark import MEMORY_FIXTURE, QUERY_FIXTURE, retrieval_quality_benchmark
from fourdt_memory.cli import main


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


class RetrievalQualityBenchmarkTests(unittest.TestCase):
    def test_retrieval_quality_fixture_is_realistic_and_safe(self) -> None:
        self.assertGreaterEqual(len(MEMORY_FIXTURE), 20)
        self.assertGreaterEqual(len(QUERY_FIXTURE), 20)
        categories = {memory.category for memory in MEMORY_FIXTURE}
        for expected in (
            "accepted_decision",
            "user_preference",
            "source_boundary_rule",
            "implementation_lesson",
            "process_constraint",
        ):
            self.assertIn(expected, categories)

        forbidden_terms = ("-----begin", "api_key =", "password =", "token =", "production dump")
        for memory in MEMORY_FIXTURE:
            self.assertTrue(memory.source_type)
            self.assertTrue(memory.source_ref)
            self.assertLess(len(memory.content), 400)
            lowered = memory.content.lower()
            for term in forbidden_terms:
                self.assertNotIn(term, lowered)

    def test_retrieval_quality_benchmark_reports_required_metrics(self) -> None:
        payload = retrieval_quality_benchmark()

        self.assertEqual(payload["profile"], "retrieval-quality")
        self.assertEqual(payload["fixture"]["sourceBoundary"], "does_not_read_sources")
        self.assertTrue(payload["fixture"]["safeFixture"])
        self.assertGreaterEqual(payload["fixture"]["queryCount"], 20)

        modes = {mode["mode"]: mode for mode in payload["modes"]}
        self.assertEqual(set(modes), {"none-lexical", "hash-smoke"})
        for mode in modes.values():
            for metric in ("top1", "top3", "top5", "mrr", "falseNegatives", "irrelevantStaleRecalls"):
                self.assertIn(metric, mode)
            self.assertEqual(mode["queryCount"], payload["fixture"]["queryCount"])
            self.assertEqual(len(mode["queries"]), payload["fixture"]["queryCount"])

        self.assertIn("not semantic-quality search", payload["interpretation"]["hashMode"])

    def test_cli_retrieval_quality_profile_is_machine_readable_and_non_mutating(self) -> None:
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
                [
                    "benchmark",
                    "--profile",
                    "retrieval-quality",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "benchmark_complete")
            self.assertEqual(payload["profile"], "retrieval-quality")
            self.assertFalse(storage.exists())
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "sentinel")


if __name__ == "__main__":
    unittest.main()
