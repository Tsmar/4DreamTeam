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


def run_cli(args: list[str], stdin: str = "") -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    original_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(stdin)
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = main(args)
    finally:
        sys.stdin = original_stdin
    output = stdout.getvalue().strip()
    payload = json.loads(output) if output else {}
    return exit_code, payload, stderr.getvalue()


def run_help(args: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), self_exit_to_code() as code:
        main(args)
    return code[0], stdout.getvalue()


@contextlib.contextmanager
def self_exit_to_code():
    code = [0]
    try:
        yield code
    except SystemExit as exc:
        code[0] = int(exc.code or 0)


class WikiCliTests(unittest.TestCase):
    def test_init_creates_single_workspace_wiki_and_queries_sections(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "init"])
            self.assertEqual(exit_code, 0)
            self.assertTrue((workspace / ".4dt" / "wiki" / "pages" / "overview.md").exists())
            self.assertFalse((workspace / ".4dt" / "wiki" / "pages" / "index.md").exists())
            self.assertFalse((workspace / "docs").exists())

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
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "update",
                    "domains-payments",
                    "--status",
                    "actual",
                    "--source-refs-json",
                    '["sources/app.py"]',
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["status"], "actual")

            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "domains-payments",
                    "summary",
                    "--content",
                    "Payments handles billing context.",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["content"], "Payments handles billing context.")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "domains-payments"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["frontmatter"]["source_refs"], '["sources/app.py"]')
            self.assertIn("Payments handles billing context.", payload["body"])

            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "apply",
                    "domains-payments",
                ]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_payload")

            with tempfile.NamedTemporaryFile("w", encoding="utf-8") as payload_file:
                json.dump(
                    {
                        "status": "accepted",
                        "source_refs": ["sources/billing.py"],
                        "sections": {
                            "content": ["Payments now describes billing behavior.", "", "- It supports line arrays."],
                            "evidence": ["- `sources/billing.py`"],
                        },
                    },
                    payload_file,
                )
                payload_file.flush()
                exit_code, payload, _stderr = run_cli(
                    [
                        "--workspace",
                        str(workspace),
                        "--json",
                        "page",
                        "apply",
                        "domains-payments",
                        "--file",
                        payload_file.name,
                    ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["status"], "accepted")

            stdin_payload = json.dumps(
                {
                    "status": "actual",
                    "sections": {
                        "summary": "Payments summary from stdin.",
                        "related": ["- [Billing](../domains/billing.md)"],
                    },
                }
            )
            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "apply",
                    "domains-payments",
                ],
                stdin=stdin_payload,
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["status"], "actual")
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "domains-payments"])
            self.assertEqual(exit_code, 0)
            self.assertIn("Payments summary from stdin.", payload["body"])
            self.assertIn("- It supports line arrays.", payload["body"])

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

            old = workspace / ".4dt" / "wiki" / "pages" / "index.md"
            old.write_text("# Old registry\n", encoding="utf-8")
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "validate"])
            self.assertEqual(exit_code, 2)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("removed_registry", codes)

    def test_export_copies_only_wiki_pages_to_sources_target(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "init"])
            run_cli(
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
            target = workspace / "sources" / "4DreamTeam" / "docs"
            (workspace / ".4dt" / "wiki" / "pages" / ".DS_Store").write_bytes(b"macos metadata")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "export", "--target", str(target)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["export"]["target"], target.resolve().as_posix())
            self.assertIn("overview.md", payload["export"]["exported"])
            self.assertIn("domains/payments.md", payload["export"]["exported"])
            self.assertNotIn(".DS_Store", payload["export"]["exported"])
            self.assertTrue((target / "overview.md").exists())
            self.assertTrue((target / "domains" / "payments.md").exists())
            self.assertFalse((target / "index.json").exists())
            self.assertFalse((target / ".DS_Store").exists())

            run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "overview",
                    "summary",
                    "--content",
                    "Updated overview.",
                ]
            )

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "export", "--target", str(target)])
            self.assertEqual(exit_code, 0)
            self.assertIn("Updated overview.", (target / "overview.md").read_text(encoding="utf-8"))

    def test_agent_help_mentions_stdin_first_page_apply(self) -> None:
        exit_code, output = run_help(["--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Create, update, section-edit, or atomically apply page", output)

        exit_code, output = run_help(["page", "apply", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Agent default: omit --file and pass generated JSON on stdin.", output)
        self.assertIn("Use --file only when the payload already exists", output)

        exit_code, output = run_help(["page", "section-set", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("If omitted, content is read", output)

    def test_export_rejects_targets_outside_workspace_sources(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "init"])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "export"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "target_required")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "export", "--target", str(workspace / "docs")]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "target_not_allowed")


if __name__ == "__main__":
    unittest.main()
