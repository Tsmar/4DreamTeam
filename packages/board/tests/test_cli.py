from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_board.cli import main


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


class BoardCliTests(unittest.TestCase):
    def test_agent_help_mentions_timeline_entry_contract(self) -> None:
        exit_code, output = run_help(["--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Append role-scoped task or epic timeline entries.", output)
        self.assertIn("Show full task details or concise task summaries.", output)

        exit_code, output = run_help(["comment", "add", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("deterministic scripted", output)
        self.assertIn("developer_implementation", output)

        exit_code, output = run_help(["move", "--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Target board column.", output)

    def test_create_index_move_section_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "create", "epic", "Workflow Rules"])
            self.assertEqual(exit_code, 0)
            epic_id = payload["item"]["id"]
            self.assertEqual(epic_id, "EPIC-0001")
            self.assertEqual(payload["item"]["path"], "backlog/EPIC-0001-workflow-rules.md")
            self.assertTrue((workspace / ".4dt" / "db.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "board" / "board.sqlite3").exists())
            self.assertFalse((workspace / ".4dt" / "board" / ".index.json").exists())
            self.assertFalse((workspace / ".4dt" / "board" / "tasks" / payload["item"]["path"]).exists())

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "create", "task", "--epic", epic_id, "Board CLI"]
            )
            self.assertEqual(exit_code, 0)
            task_id = payload["item"]["id"]
            self.assertEqual(task_id, "EPIC-0001-TASK-0001")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "next-id", "task"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["id"], "TASK-0002")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "move", task_id, "analytic", "--status", "ready"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["item"]["board_column"], "analytic")
            self.assertEqual(payload["item"]["path"], "analytic/EPIC-0001-TASK-0001-board-cli.md")
            self.assertFalse((workspace / ".4dt" / "board" / "tasks" / payload["item"]["path"]).exists())

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "section", "get", task_id, "product_baseline"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["content"], "TBD")

            exit_code, payload, _stderr = run_cli(
                [
                    "--workspace",
                    str(workspace),
                    "--json",
                    "comment",
                    "add",
                    task_id,
                    "--role",
                    "developer",
                    "--type",
                    "developer_implementation",
                    "--summary",
                    "Implemented CLI",
                    "--body",
                    "Added command surface.",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["entry"]["type"], "developer_implementation")

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "comments", "latest", task_id, "--role", "developer"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["comments"][0]["metadata"]["role"], "developer")

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "task", "summary", task_id])
            self.assertEqual(exit_code, 0)
            export_path = workspace / "board-export.json"
            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "export", "--output", str(export_path)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["export"]["itemCount"], 2)
            self.assertEqual(payload["export"]["commentCount"], 1)

            imported = workspace / "imported"
            exit_code, payload, _stderr = run_cli(["--workspace", str(imported), "--json", "import", str(export_path)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "dry_run")
            exit_code, payload, _stderr = run_cli(["--workspace", str(imported), "--json", "import", str(export_path), "--apply"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["import"]["written"], 2)
            exit_code, payload, _stderr = run_cli(["--workspace", str(imported), "--json", "comments", "latest", task_id])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["comments"][0]["metadata"]["type"], "developer_implementation")

    def test_validate_reports_deprecated_next_owner_and_board_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            path = workspace / ".4dt" / "board" / "tasks" / "backlog" / "EPIC-0001-TASK-0001-example.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                """---
id: EPIC-0001-TASK-0001
kind: task
title: Example
epic: EPIC-0001
board_column: backlog
status: ready
next_owner: developer
created_at: 2026-05-23
updated_at: 2026-05-23
---

# Example

## Board State

- Current column: backlog

## Product Baseline

TBD
""",
                encoding="utf-8",
            )

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "validate"])

            self.assertEqual(exit_code, 0)
            codes = {issue["code"] for issue in payload["issues"]}
            self.assertIn("deprecated_field", codes)
            self.assertIn("deprecated_section", codes)

    def test_metadata_set_rejects_uncontrolled_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "create", "task", "--standalone", "Standalone"])

            exit_code, payload, _stderr = run_cli(
                ["--workspace", str(workspace), "--json", "metadata", "set", "TASK-0001", "next_owner", "developer"]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_field")

    def test_parallel_timeline_comments_preserve_both_entries(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "create", "task", "--standalone", "Parallel Timeline"])

            env = {
                **os.environ,
                "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
                "PYTHONPYCACHEPREFIX": "/tmp/4dt-pycache",
            }
            commands = [
                [
                    sys.executable,
                    "-m",
                    "fourdt_board.cli",
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
                    "--entry-id",
                    "entry-parallel-dev",
                    "--summary",
                    "Developer update",
                    "--body",
                    "Developer body.",
                ],
                [
                    sys.executable,
                    "-m",
                    "fourdt_board.cli",
                    "--workspace",
                    str(workspace),
                    "--json",
                    "comment",
                    "add",
                    "TASK-0001",
                    "--role",
                    "wiki",
                    "--type",
                    "wiki_update",
                    "--entry-id",
                    "entry-parallel-wiki",
                    "--summary",
                    "Wiki update",
                    "--body",
                    "Wiki body.",
                ],
            ]
            processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env) for command in commands]
            for process in processes:
                stdout, stderr = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 0, stderr + stdout)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "comments", "list", "TASK-0001"])
            self.assertEqual(exit_code, 0)
            entry_ids = {entry["metadata"]["entry_id"] for entry in payload["comments"]}
            self.assertEqual(entry_ids, {"entry-parallel-dev", "entry-parallel-wiki"})

    def test_timeline_types_are_listed_and_validated(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            run_cli(["--workspace", str(workspace), "--json", "create", "task", "--standalone", "Timeline"])

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "types", "list"])
            self.assertEqual(exit_code, 0)
            type_names = {entry["type"] for entry in payload["types"]}
            self.assertIn("developer_implementation", type_names)
            self.assertIn("quality_acceptance", type_names)

            exit_code, payload, _stderr = run_cli(
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
                    "unknown_action",
                ]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_type")

            exit_code, payload, _stderr = run_cli(
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
                    "quality_acceptance",
                ]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "type_role_mismatch")


if __name__ == "__main__":
    unittest.main()
