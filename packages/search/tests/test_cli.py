from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for tool in ("search", "sources", "wiki", "board", "memory"):
    sys.path.insert(0, str(ROOT / "packages" / tool / "src"))

from fourdt_board.cli import main as board_main
from fourdt_memory.cli import main as memory_main
from fourdt_search.cli import main as search_main
from fourdt_wiki.cli import main as wiki_main


def run(main_func, args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
        exit_code = main_func(args)
    output = stdout.getvalue().strip()
    return exit_code, json.loads(output) if output else {}


def run_help(main_func, args: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
        try:
            main_func(args)
        except SystemExit as exc:
            return int(exc.code or 0), stdout.getvalue()
    return 0, stdout.getvalue()


class SearchCliTests(unittest.TestCase):
    def test_agent_help_mentions_query_modes_and_index_modes(self) -> None:
        exit_code, output = run_help(search_main, ["--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Build or check the unified search index.", output)
        self.assertIn("Resolve a search result id through its authoritative", output)

        exit_code, output = run_help(search_main, ["query", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Payload sources: pass query text as an argument", output)
        self.assertIn("structured query from --query-json or --query-file", output)
        self.assertIn("readonly", output)
        self.assertIn("reports stale indexes", output)

    def test_stats_initializes_tables_without_legacy_search_directories(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "stats"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "search").exists())
            with sqlite3.connect(workspace / ".4dt" / "db.sqlite3") as connection:
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            self.assertIn("search_chunks", tables)
            self.assertIn("search_manifest", tables)

    def test_build_search_get_sources_wiki_and_board(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            (source_root / "app.py").write_text("def hello_search():\n    return 'world'\n", encoding="utf-8")

            run(wiki_main, ["--workspace", str(workspace), "--json", "init"])
            run(
                wiki_main,
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "page",
                    "section-set",
                    "overview",
                    "summary",
                    "--content",
                    "Search workflow overview.",
                ],
            )
            run(wiki_main, ["--workspace", str(workspace), "--json", "page", "tags", "add", "overview", "search-topic"])
            run(board_main, ["--workspace", str(workspace), "--json", "create", "task", "--standalone", "Search CLI"])
            run(
                board_main,
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "comment",
                    "add",
                    "TASK-0001",
                    "--role",
                    "developer",
                    "--type",
                    "developer_implementation",
                    "--summary",
                    "Implemented search contract",
                    "--body",
                    "Added universal search command surface.",
                ],
            )

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "index", "build"])
            self.assertEqual(exit_code, 0)
            self.assertGreaterEqual(payload["index"]["chunkCount"], 3)
            self.assertEqual(payload["index"]["chunksStore"], ".4dt/db.sqlite3:search_chunks")
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "search" / "chunks.jsonl").exists())

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "stats"])
            self.assertEqual(exit_code, 0)
            self.assertGreaterEqual(payload["stats"]["domainCounts"]["sources"], 1)
            self.assertGreaterEqual(payload["stats"]["domainCounts"]["wiki"], 1)
            self.assertGreaterEqual(payload["stats"]["domainCounts"]["board"], 1)

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "hello search", "--domain", "sources"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["domain"], "sources")
            self.assertIn("getCommand", payload["matches"][0])
            self.assertEqual(payload["matches"][0]["locator"]["domain"], "sources")
            result_id = payload["matches"][0]["id"]
            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "get", result_id])
            self.assertEqual(exit_code, 0)
            self.assertIn("hello_search", payload["result"]["content"]["content"])

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "workflow overview", "--domain", "wiki"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["domain"], "wiki")

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "search-topic", "--domain", "wiki", "--explain"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["metadata"]["tags"], ["search-topic"])
            self.assertTrue(payload["explain"]["wikiFts"]["available"])
            self.assertTrue(payload["explain"]["wikiFts"]["used"])
            self.assertGreaterEqual(payload["explain"]["wikiFts"]["hitCount"], 1)

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "implemented search contract", "--domain", "board"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["domain"], "board")
            self.assertEqual(payload["matches"][0]["locator"]["domain"], "board")

    def test_memory_domain_is_live_and_gettable_without_persistent_index(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run(memory_main, ["init", "--workspace", str(workspace), "--json"])
            run(
                memory_main,
                [
                    "remember",
                    "Workflow configuration lives in project.workflow.modes and current mode contracts.",
                    "--workspace",
                    str(workspace),
                    "--scope",
                    "workspace",
                    "--type",
                    "decision",
                    "--source-type",
                    "task",
                    "--source-ref",
                    "tasks/workflow.md",
                    "--json",
                ],
            )

            exit_code, payload = run(
                search_main,
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "query",
                    "workflow configuration",
                    "--domain",
                    "memory",
                    "--explain",
                ],
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["domain"], "memory")
            self.assertEqual(payload["matches"][0]["locator"]["domain"], "memory")
            self.assertIn("4dt-memory get", payload["matches"][0]["getCommand"])
            self.assertEqual(payload["index"]["liveDomains"], ["memory"])
            result_id = payload["matches"][0]["id"]

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "get", result_id])
            self.assertEqual(exit_code, 0)
            self.assertIn("project.workflow.modes", payload["result"]["content"]["item"]["content"])

    def test_source_exclusions_and_stale_results_are_structured(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            allowed = source_root / "allowed.md"
            allowed.write_text("allowed searchable content", encoding="utf-8")
            (source_root / ".env").write_text("SECRET=value", encoding="utf-8")

            run(search_main, ["--workspace", str(workspace), "--json", "index", "build"])

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "SECRET", "--domain", "sources"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"], [])

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "allowed searchable", "--domain", "sources"])
            self.assertEqual(exit_code, 0)
            result_id = payload["matches"][0]["id"]
            allowed.write_text("changed content", encoding="utf-8")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "get", result_id])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "stale_result")

    def test_index_check_and_error_contracts_are_structured(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            (source_root / "contract.md").write_text("contract searchable content", encoding="utf-8")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "index", "check"])
            self.assertEqual(exit_code, 2)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "issues")
            self.assertEqual(payload["issues"][0]["code"], "missing_manifest")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "index", "build"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "ready")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "index", "check"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["issues"], [])

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "contract", "--domain", "invalid"],
            )
            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "invalid_domain")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "contract", "--limit", "0"])
            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "invalid_limit")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "get", "missing-result"])
            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "not_found")

    def test_index_modes_auto_readonly_and_rebuild_are_structured(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            source_file = source_root / "contract.md"
            source_file.write_text("contract searchable content", encoding="utf-8")

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "query", "contract", "--domain", "sources", "--index", "readonly"],
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "index_not_ready")

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "query", "contract", "--domain", "sources", "--index", "auto"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "indexed_then_searched")
            self.assertTrue(payload["index"]["rebuilt"])

            source_file.write_text("contract searchable changed", encoding="utf-8")
            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "query", "changed", "--domain", "sources", "--index", "readonly"],
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "index_not_ready")

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "query", "changed", "--domain", "sources", "--index", "rebuild"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "indexed_then_searched")
            self.assertEqual(payload["index"]["reason"], "forced")

    def test_advanced_match_extended_json_fields_and_explain(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            (source_root / "alpha.md").write_text("alpha token visible workflow", encoding="utf-8")
            (source_root / "beta.md").write_text("beta token hidden secret", encoding="utf-8")
            alpha_path = str((source_root / "alpha.md").resolve())
            beta_path = str((source_root / "beta.md").resolve())
            run(search_main, ["--workspace", str(workspace), "--json", "index", "build"])

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "alpha missing", "--domain", "sources"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"], [])

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "alpha missing", "--domain", "sources", "--match", "any"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["path"], alpha_path)

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "alpha | beta", "--domain", "sources", "--mode", "extended", "--limit", "2"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual({match["path"] for match in payload["matches"]}, {alpha_path, beta_path})

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "alpha !secret", "--domain", "sources", "--mode", "extended", "--field", "body"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["path"], alpha_path)

            for pattern, field in (("=alpha.md", "title"), ("'visible", "body"), ("^alpha", "body"), ("workflow$", "body")):
                exit_code, payload = run(
                    search_main,
                    ["--workspace", str(workspace), "--json", "search", pattern, "--domain", "sources", "--mode", "extended", "--field", field],
                )
                self.assertEqual(exit_code, 0)
                self.assertEqual(payload["matches"][0]["path"], alpha_path)

            query = json.dumps({"$and": [{"body": "alpha"}, {"path": "alpha.md"}]})
            exit_code, payload = run(
                search_main,
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "search",
                    "--query-json",
                    query,
                    "--domain",
                    "sources",
                    "--explain",
                ],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["path"], alpha_path)
            self.assertEqual(payload["explain"]["mode"], "json")
            self.assertEqual(payload["explain"]["queryType"], "json")
            self.assertGreaterEqual(payload["explain"]["candidateCount"], 1)

            query_file = workspace / "query.json"
            query_file.write_text(json.dumps({"$or": [{"body": "beta"}, {"path": "alpha.md"}]}), encoding="utf-8")
            exit_code, payload = run(
                search_main,
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "search",
                    "--query-file",
                    str(query_file),
                    "--domain",
                    "sources",
                    "--limit",
                    "2",
                ],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["matches"]), 2)

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "visible", "--domain", "sources", "--field", "path"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"], [])

            exit_code, payload = run(
                search_main,
                ["--workspace", str(workspace), "--json", "search", "visible", "--domain", "sources", "--field", "body"],
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["path"], alpha_path)

    def test_advanced_search_invalid_inputs_are_structured(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            (workspace / "sources").mkdir()
            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "alpha", "--query-json", "{}"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_query")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "--query-json", "{}", "--mode", "extended"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_query")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "--mode", "json", "alpha"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_query")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "alpha", "--field", "unknown"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_field")

            exit_code, payload = run(search_main, ["--workspace", str(workspace), "--json", "search", "alpha", "--limit", "2", "--max-candidates", "1"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_max_candidates")


if __name__ == "__main__":
    unittest.main()
