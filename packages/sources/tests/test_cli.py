from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_sources.cli import main


def run_cli(args: list[str]) -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = main(args)
    output = stdout.getvalue().strip()
    payload = json.loads(output) if output else {}
    return exit_code, payload, stderr.getvalue()


def run_help(args: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        try:
            main(args)
        except SystemExit as exc:
            return int(exc.code or 0), stdout.getvalue()
    return 0, stdout.getvalue()


class SourcesCliTests(unittest.TestCase):
    def test_agent_help_mentions_approval_and_ranges(self) -> None:
        exit_code, output = run_help(["--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Manage approved source boundaries.", output)
        self.assertIn("Build or check the approved source index.", output)

        exit_code, output = run_help(["registry", "add", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("External paths require explicit operator", output)

        exit_code, output = run_help(["get", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Recommended for focused agent reads.", output)

    def test_registry_validate_initializes_tables(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "registry", "validate"])

            self.assertEqual(exit_code, 2)
            self.assertEqual(payload["status"], "issues")
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            with sqlite3.connect(workspace / ".4dt" / "db.sqlite3") as connection:
                tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            self.assertIn("source_registry", tables)
            self.assertIn("source_inventory", tables)
            self.assertIn("source_index", tables)

    def test_registry_add_requires_operator_approval_and_supports_file_and_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            external = workspace / "external"
            external.mkdir()
            file_source = workspace / "notes.md"
            file_source.write_text("hello", encoding="utf-8")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "registry", "add", str(external)])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "operator_approval_required")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "registry", "add", str(external), "--operator-approved"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["source"]["kind"], "directory")

            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "registry",
                    "add",
                    str(file_source),
                    "--label",
                    "Notes",
                    "--operator-approved",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["source"]["kind"], "file")

            with sqlite3.connect(workspace / ".4dt" / "db.sqlite3") as connection:
                rows = connection.execute("SELECT id, label FROM source_registry ORDER BY id").fetchall()
            self.assertIn(("notes", "Notes"), rows)

    def test_index_search_get_stats_and_range_safety(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            small = source_root / "app.py"
            small.write_text("def hello():\n    return 'world'\n", encoding="utf-8")
            large = source_root / "large.txt"
            large.write_text("\n".join(f"line {index}" for index in range(5000)), encoding="utf-8")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "index", "build"])
            self.assertEqual(exit_code, 0)
            self.assertGreaterEqual(payload["index"]["entryCount"], 3)
            with sqlite3.connect(workspace / ".4dt" / "db.sqlite3") as connection:
                inventory_count = connection.execute("SELECT COUNT(*) FROM source_inventory").fetchone()[0]
                source_index_count = connection.execute("SELECT COUNT(*) FROM source_index").fetchone()[0]
            self.assertGreaterEqual(inventory_count, 3)
            self.assertEqual(source_index_count, 1)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "app.py"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["matches"][0]["relative_path"], "app.py")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "sources/app.py"])
            self.assertEqual(exit_code, 0)
            self.assertIn("def hello", payload["file"]["content"])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "sources/large.txt"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "range_required")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "get", "sources/large.txt", "--range", "2:3"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["file"]["content"], "line 1\nline 2")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "stats"])
            self.assertEqual(exit_code, 0)
            self.assertGreaterEqual(payload["stats"]["sourceCount"], 1)

    def test_index_excludes_builtin_ignored_and_forbidden_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            (source_root / "app.md").write_text("allowed", encoding="utf-8")
            node_modules = source_root / "node_modules" / "pkg"
            node_modules.mkdir(parents=True)
            (node_modules / "index.js").write_text("dependency", encoding="utf-8")
            (source_root / ".env").write_text("SECRET=value", encoding="utf-8")
            (source_root / ".env.local").write_text("SECRET=value", encoding="utf-8")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "index", "build"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["index"]["issues"]["errors"], [])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "app.md"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["matches"]), 1)

            for query in ("node_modules", ".env"):
                exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", query])
                self.assertEqual(exit_code, 0)
                self.assertEqual(payload["matches"], [])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "sources/.env"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_path_excluded")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "sources/.env.local"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_path_excluded")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "get", "sources/node_modules/pkg/index.js"]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_path_excluded")

    def test_index_and_get_honor_workspace_gitignore(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            source_root = workspace / "sources"
            source_root.mkdir()
            (source_root / ".gitignore").write_text("ignored.md\ncache/\n*.tmp\n!keep.tmp\n", encoding="utf-8")
            (source_root / "keep.md").write_text("keep", encoding="utf-8")
            (source_root / "ignored.md").write_text("ignored", encoding="utf-8")
            cache = source_root / "cache"
            cache.mkdir()
            (cache / "data.md").write_text("cached", encoding="utf-8")
            (source_root / "drop.tmp").write_text("drop", encoding="utf-8")
            (source_root / "keep.tmp").write_text("keep", encoding="utf-8")

            exit_code, _payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "index", "build"])
            self.assertEqual(exit_code, 0)

            for query in ("ignored.md", "cache", "drop.tmp"):
                exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", query])
                self.assertEqual(exit_code, 0)
                self.assertEqual(payload["matches"], [])

            for query in ("keep.md", "keep.tmp"):
                exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", query])
                self.assertEqual(exit_code, 0)
                self.assertEqual(len(payload["matches"]), 1)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "sources/ignored.md"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_path_excluded")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "sources/cache/data.md"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_path_excluded")

    def test_index_honors_gitignore_for_registered_directory_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            (workspace / "sources").mkdir()
            external = workspace / "external"
            external.mkdir()
            (external / ".gitignore").write_text("private/\n*.log\n", encoding="utf-8")
            (external / "public.md").write_text("public", encoding="utf-8")
            private = external / "private"
            private.mkdir()
            (private / "note.md").write_text("private", encoding="utf-8")
            (external / "debug.log").write_text("debug", encoding="utf-8")

            exit_code, _payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "registry", "add", str(external), "--operator-approved"]
            )
            self.assertEqual(exit_code, 0)
            exit_code, _payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "index", "build"])
            self.assertEqual(exit_code, 0)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", "public.md"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["matches"]), 1)

            for query in ("note.md", "debug.log"):
                exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "search", query])
                self.assertEqual(exit_code, 0)
                self.assertEqual(payload["matches"], [])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", str(private / "note.md")])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_path_excluded")

    def test_get_rejects_paths_outside_allowed_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            outside = workspace / "outside.txt"
            outside.write_text("secret-ish", encoding="utf-8")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "get", "outside.txt"])

            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "source_not_allowed")


if __name__ == "__main__":
    unittest.main()
