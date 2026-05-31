from __future__ import annotations

import contextlib
import io
import json
import os
import sqlite3
import subprocess
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
    def test_validate_initializes_tables_without_legacy_wiki_directories(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "validate"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "wiki").exists())
            with sqlite3.connect(workspace / ".4dt" / "db.sqlite3") as connection:
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            self.assertIn("wiki_pages", tables)
            self.assertIn("wiki_sections", tables)
            self.assertIn("wiki_index", tables)

    def test_init_creates_single_workspace_wiki_and_queries_sections(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "init"])
            self.assertEqual(exit_code, 0)
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "wiki" / "wiki.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "wiki" / "index.json").exists())
            self.assertFalse((workspace / ".4dt" / "wiki" / "pages" / "overview.md").exists())
            self.assertFalse((workspace / ".4dt" / "wiki" / "pages" / "index.md").exists())
            self.assertFalse((workspace / "docs").exists())

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "overview", "--section", "summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["section"], "summary")
            self.assertEqual(payload["content"], "TBD")
            with sqlite3.connect(workspace / ".4dt" / "db.sqlite3") as connection:
                columns = {row[1] for row in connection.execute("PRAGMA table_info(wiki_pages)").fetchall()}
                section_count = connection.execute("SELECT COUNT(*) FROM wiki_sections").fetchone()[0]
                wiki_index_count = connection.execute("SELECT COUNT(*) FROM wiki_index").fetchone()[0]
            self.assertNotIn("body", columns)
            self.assertNotIn("frontmatter_json", columns)
            self.assertIn("id", columns)
            self.assertIn("kind", columns)
            self.assertIn("status", columns)
            self.assertIn("extra_frontmatter_json", columns)
            self.assertGreaterEqual(section_count, 24)
            self.assertEqual(wiki_index_count, 1)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "status"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["issues"], [])

    def test_init_imports_legacy_markdown_pages_into_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            legacy_page = workspace / ".4dt" / "wiki" / "pages" / "domains" / "legacy.md"
            legacy_page.parent.mkdir(parents=True, exist_ok=True)
            legacy_page.write_text(
                """---
id: domains-legacy
kind: domain
title: Legacy
status: actual
created_at: 2026-05-31T00:00:00Z
updated_at: 2026-05-31T00:00:00Z
owner: wiki
source_refs: []
task_refs: []
tags: ["legacy-domain", "imported knowledge"]
---

# Legacy

## Summary

Imported summary.

## Content

Imported content.

## Evidence

- None.

## Decisions

- None.

## Open Questions

- None.

## Related

- None.
""",
                encoding="utf-8",
            )

            exit_code, _payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "init"])
            self.assertEqual(exit_code, 0)

            legacy_page.unlink()
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "domains-legacy", "--section", "summary"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["content"], "Imported summary.")
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "legacy-domain"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["tags"], ["imported-knowledge", "legacy-domain"])

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
                    "--tag",
                    "payment-domain",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["id"], "domains-payments")
            self.assertEqual(payload["page"]["tags"], ["payment-domain"])

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
                ["--workspace", str(workspace), "--json", "page", "tags", "add", "domains-payments", "Billing", "cash-flow"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["tags"], ["billing", "cash-flow", "payment-domain"])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "cash-flow"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["id"], "domains-payments")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "tags", "list"])
            self.assertEqual(exit_code, 0)
            tag_names = {entry["name"] for entry in payload["tags"]}
            self.assertIn("billing", tag_names)

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
            self.assertEqual(payload["section"], "summary")
            self.assertNotIn("content", payload)

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
                    "tags": ["billing", "cash-flow", "payment-domain"],
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
            self.assertEqual(payload["page"]["tags"], ["billing", "cash-flow", "payment-domain"])
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "domains-payments"])
            self.assertEqual(exit_code, 0)
            self.assertIn("Payments summary from stdin.", payload["body"])
            self.assertIn("- It supports line arrays.", payload["body"])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "Payments"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["id"], "domains-payments")
            self.assertIn("match_sections", payload["matches"][0])
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "payment-domain"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["id"], "domains-payments")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "adr", "create", "Use Markdown Storage", "--tag", "storage-decision"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["page"]["kind"], "decision")
            self.assertEqual(payload["page"]["tags"], ["storage-decision"])

    def test_page_section_writes_reject_sections_larger_than_32kb(self) -> None:
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
                    "--tag",
                    "Payment Domain",
                ]
            )

            at_limit = "x" * 32_000
            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "domains-payments",
                    "content",
                    "--content",
                    at_limit,
                ]
            )
            self.assertEqual(exit_code, 0)

            oversized = "x" * 32_001
            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "domains-payments",
                    "content",
                    "--content",
                    oversized,
                ]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "section_too_large")

            stdin_payload = json.dumps({"sections": {"content": oversized}})
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
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "section_too_large")

    def test_parallel_section_writes_preserve_both_updates(self) -> None:
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
                    "--tag",
                    "Payment Domain",
                ]
            )
            env = {
                **os.environ,
                "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
                "PYTHONPYCACHEPREFIX": "/tmp/4dt-pycache",
            }
            commands = [
                [
                    sys.executable,
                    "-m",
                    "fourdt_wiki.cli",
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "domains-payments",
                    "summary",
                    "--content",
                    "Parallel summary update.",
                ],
                [
                    sys.executable,
                    "-m",
                    "fourdt_wiki.cli",
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "domains-payments",
                    "content",
                    "--content",
                    "Parallel content update.",
                ],
            ]
            processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env) for command in commands]
            for process in processes:
                stdout, stderr = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 0, stderr + stdout)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "domains-payments"])
            self.assertEqual(exit_code, 0)
            self.assertIn("Parallel summary update.", payload["body"])
            self.assertIn("Parallel content update.", payload["body"])

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
            old.parent.mkdir(parents=True, exist_ok=True)
            old.write_text("# Old registry\n", encoding="utf-8")
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "validate"])
            self.assertEqual(exit_code, 2)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("removed_registry", codes)

    def test_legacy_sources_page_is_validated_not_silently_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "init"])

            legacy = workspace / ".4dt" / "wiki" / "pages" / "sources.md"
            legacy.parent.mkdir(parents=True, exist_ok=True)
            legacy.write_text("# Legacy Sources\n", encoding="utf-8")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "validate"])
            self.assertEqual(exit_code, 2)
            issues = [issue for issue in payload["issues"] if issue["path"] == "sources.md"]
            self.assertTrue(issues)
            self.assertIn("missing_frontmatter", {issue["code"] for issue in issues})

    def test_export_renders_sqlite_pages_to_sources_target(self) -> None:
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
                    "--tag",
                    "Payment Domain",
                ]
            )
            target = workspace / "sources" / "4DreamTeam" / "docs"
            metadata_file = workspace / ".4dt" / "wiki" / "pages" / ".DS_Store"
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            metadata_file.write_bytes(b"macos metadata")

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
            exported_payment = (target / "domains" / "payments.md").read_text(encoding="utf-8")
            self.assertIn("id: domains-payments", exported_payment)
            self.assertIn("kind: domain", exported_payment)
            self.assertIn("source_refs: []", exported_payment)
            self.assertIn("task_refs: []", exported_payment)
            self.assertIn('tags: ["payment-domain"]', exported_payment)

            json_export = workspace / "wiki-export.json"
            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "export", "--format", "json", "--output", str(json_export)]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["export"]["format"], "json")
            self.assertTrue(json_export.exists())
            imported = workspace / "imported"
            exit_code, payload, _stderr = run_cli(["--workspace", str(imported), "--json", "import", str(json_export)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "dry_run")
            exit_code, payload, _stderr = run_cli(["--workspace", str(imported), "--json", "import", str(json_export), "--apply"])
            self.assertEqual(exit_code, 0)
            self.assertGreaterEqual(payload["import"]["written"], 2)
            exit_code, payload, _stderr = run_cli(["--workspace", str(imported), "--json", "search", "payment-domain"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["tags"], ["payment-domain"])

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
        self.assertIn("Create, update, section-edit, or apply combined page", output)

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
