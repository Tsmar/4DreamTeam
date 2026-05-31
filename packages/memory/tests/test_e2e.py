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


class EndToEndTests(unittest.TestCase):
    def test_full_cli_smoke_sequence(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            import_workspace = tmp_path / "import-workspace"
            import_storage = tmp_path / "import-storage"
            export_path = tmp_path / "memory.jsonl"
            full_export_path = tmp_path / "memory-full.json"
            full_import_workspace = tmp_path / "full-import-workspace"
            full_import_storage = tmp_path / "full-import-storage"
            workspace.mkdir()
            import_workspace.mkdir()
            full_import_workspace.mkdir()

            exit_code, payload = run_cli(
                ["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")

            exit_code, payload = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertIn(exit_code, (0, 3))
            self.assertIn(payload["status"], ("ready", "degraded_setup_required"))

            exit_code, payload = run_cli(
                [
                    "remember",
                    "E2E smoke memory uses source-backed evidence.",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--scope",
                    "workspace",
                    "--type",
                    "decision",
                    "--role",
                    "lead",
                    "--source-type",
                    "task",
                    "--source-ref",
                    "tasks/done/example.md",
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            memory_id = payload["id"]

            exit_code, payload = run_cli(
                ["list", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["items"][0]["id"], memory_id)

            exit_code, payload = run_cli(
                ["get", str(memory_id), "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["item"]["content"], "E2E smoke memory uses source-backed evidence.")

            exit_code, payload = run_cli(
                ["search", "source-backed", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["items"][0]["id"], memory_id)
            self.assertIn("preview", payload["items"][0])
            self.assertNotIn("content", payload["items"][0])

            exit_code, payload = run_cli(
                ["reindex", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["checkedItems"], 1)

            exit_code, payload = run_cli(
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
            self.assertIn("export_contains_sensitive_accepted_memory", payload["warnings"])

            exit_code, payload = run_cli(
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
            self.assertEqual(payload["status"], "dry_run")
            self.assertFalse(import_storage.exists())

            exit_code, payload = run_cli(
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
            self.assertEqual(payload["written"], 1)

            exit_code, payload = run_cli(
                [
                    "export",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--format",
                    "json",
                    "--output",
                    str(full_export_path),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["format"], "json")
            exit_code, payload = run_cli(
                [
                    "import",
                    str(full_export_path),
                    "--workspace",
                    str(full_import_workspace),
                    "--storage-root",
                    str(full_import_storage),
                    "--format",
                    "json",
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "dry_run")
            exit_code, payload = run_cli(
                [
                    "import",
                    str(full_export_path),
                    "--workspace",
                    str(full_import_workspace),
                    "--storage-root",
                    str(full_import_storage),
                    "--format",
                    "json",
                    "--apply",
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "imported")
            exit_code, payload = run_cli(
                ["defaults", "load", "--workspace", str(full_import_workspace), "--storage-root", str(full_import_storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertIn("project.rules", {entry["key"] for entry in payload["keys"]})

            exit_code, payload = run_cli(
                [
                    "session",
                    "set",
                    "session-e2e",
                    '{"step":"e2e"}',
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "session_saved")

            exit_code, payload = run_cli(
                [
                    "session",
                    "get",
                    "session-e2e",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["state"], {"step": "e2e"})

            exit_code, payload = run_cli(
                ["benchmark", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["seedFromWiki"], "deferred")

            exit_code, payload = run_cli(
                [
                    "forget",
                    str(memory_id),
                    "--reason",
                    "e2e cleanup",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "forgotten")

            exit_code, payload = run_cli(
                ["list", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["items"], [])


if __name__ == "__main__":
    unittest.main()
