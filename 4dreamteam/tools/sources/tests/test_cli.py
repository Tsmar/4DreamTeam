from __future__ import annotations

import contextlib
import io
import json
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


class SourcesCliTests(unittest.TestCase):
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

            registry = (workspace / "docs" / "sources.md").read_text(encoding="utf-8")
            self.assertIn("maintained by `4dt-sources`", registry)
            self.assertIn("Notes", registry)

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
