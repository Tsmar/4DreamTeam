from __future__ import annotations

import contextlib
import io
import json
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


class BoardCliTests(unittest.TestCase):
    def test_create_index_move_section_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)

            exit_code, payload, _stderr = run_cli(["--workspace", str(workspace), "--json", "create", "epic", "Workflow Rules"])
            self.assertEqual(exit_code, 0)
            epic_id = payload["item"]["id"]
            self.assertEqual(epic_id, "EPIC-0001")
            self.assertEqual(payload["item"]["path"], "tasks/backlog/EPIC-0001-workflow-rules.md")

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
            self.assertTrue((workspace / payload["item"]["path"]).exists())

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
            self.assertEqual(payload["latest_comments"][0]["metadata"]["type"], "developer_implementation")

    def test_validate_reports_deprecated_next_owner_and_board_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            path = workspace / "tasks" / "backlog" / "EPIC-0001-TASK-0001-example.md"
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
