from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_wiki.cli import main


def run_cli(args: list[str]) -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = main(args)
    output = stdout.getvalue().strip()
    payload = json.loads(output) if output else {}
    return exit_code, payload, stderr.getvalue()


class WikiCliTests(unittest.TestCase):
    def test_init_creates_single_workspace_wiki_and_queries_sections(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "init"])
            self.assertEqual(exit_code, 0)
            self.assertTrue((workspace / "docs" / "overview.md").exists())
            self.assertFalse((workspace / "docs" / "index.md").exists())
            self.assertTrue((workspace / "docs" / "sources.md").exists())

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "overview", "--section", "summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["section"], "summary")
            self.assertEqual(payload["content"], "TBD")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "status"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["issues"], [])

    def test_page_create_update_search_and_adr(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "init"])

            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "create",
                    "domains/payments.md",
                    "--title",
                    "Payments",
                    "--type",
                    "domain",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["id"], "domains-payments")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "page", "update", "domains-payments", "--status", "actual"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["status"], "actual")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "Payments"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["id"], "domains-payments")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "adr", "create", "Use Markdown Storage"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["kind"], "decision")

    def test_docs_index_is_rejected_by_validation_and_page_create(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "init"])

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "page", "create", "index.md", "--title", "Index", "--type", "overview"]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "removed_registry")

            (workspace / "docs" / "index.md").write_text("# Old registry\n", encoding="utf-8")
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "validate"])
            self.assertEqual(exit_code, 2)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("removed_registry", codes)


if __name__ == "__main__":
    unittest.main()
