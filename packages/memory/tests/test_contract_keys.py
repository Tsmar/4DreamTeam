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
from fourdt_memory.sqlite_store import MemoryStore


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = main(args)
    output = stdout.getvalue().strip()
    payload = json.loads(output) if output else {}
    return exit_code, payload


class ContractKeysTests(unittest.TestCase):
    def valid_modes(self) -> dict[str, dict[str, object]]:
        return {
            "simple": {
                "description": "Short controlled work loop.",
                "autonomy": "low",
                "approval_gates": ["repair", "push"],
                "reporting_style": "brief",
                "commit_policy": "commit per task",
                "push_policy": "ask every time",
                "validation_expectations": ["unit tests"],
            }
        }

    def test_keys_list_get_set_delete_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(["keys", "list", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            keys = {entry["key"]: entry for entry in payload["keys"]}
            self.assertIn("project.rules", keys)
            self.assertFalse(keys["project.rules"]["configured"])

            exit_code, payload = run_cli(["keys", "get", "project.rules", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "missing")
            self.assertTrue(payload["key"]["missing"])

            exit_code, payload = run_cli(
                ["keys", "set", "project.rules", "--value", "Use short operator updates.", "--workspace", str(workspace), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["key"]["value"], "Use short operator updates.")
            self.assertEqual(payload["key"]["valueType"], "text")

            exit_code, payload = run_cli(["keys", "delete", "project.rules", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["deleted"])

            with MemoryStore(workspace) as store:
                actions = [entry["action"] for entry in store.audit_entries()]
            self.assertIn("contract_set", actions)
            self.assertIn("contract_delete", actions)

    def test_workflow_modes_require_defined_current_mode(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(["mode", "set-current", "simple", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "undefined_mode")
            self.assertEqual(payload["questions"][0]["key"], "project.workflow.current_mode")

            exit_code, payload = run_cli(
                [
                    "keys",
                    "set",
                    "project.workflow.modes",
                    "--value",
                    json.dumps(self.valid_modes()),
                    "--workspace",
                    str(workspace),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)

            exit_code, payload = run_cli(["mode", "set-current", "simple", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["currentMode"], "simple")
            self.assertEqual(payload["definition"]["push_policy"], "ask every time")

            exit_code, payload = run_cli(["mode", "get", "simple", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["defined"])

    def test_onboarding_rules_and_questions_report_missing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(["onboarding", "rules", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "missing_contract")
            self.assertIn("project.workflow.current_mode", payload["missingKeys"])
            self.assertIn("contract_keys_missing", payload["warnings"])
            self.assertGreater(len(payload["questions"]), 0)

            exit_code, payload = run_cli(["onboarding", "questions", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "questions_available")
            question_keys = {entry["key"] for entry in payload["questions"]}
            self.assertIn("project.operator.approval_policy", question_keys)

    def test_defaults_load_reports_ready_or_incomplete_without_searching(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(["defaults", "load", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "defaults_incomplete")
            self.assertTrue(payload["onboardingRequired"])
            self.assertEqual(payload["onboardingCommand"], "4dt-memory onboarding questions --workspace . --json")

            values = {
                "project.rules": "Use the current request, workspace instructions, and managed tools first.",
                "project.workflow.modes": self.valid_modes(),
                "project.workflow.current_mode": "simple",
                "project.operator.preferences": "Keep operator updates brief.",
                "project.operator.approval_policy": "Ask before repair, commits, pushes, and publication.",
                "project.sources.policy": "Workspace sources are approved; external sources require explicit approval.",
                "project.delivery.git_policy": "Commit per task and ask before push.",
                "project.quality.validation_policy": "Run focused automated checks before commit.",
                "project.communication.style": "Concise Russian summaries.",
            }
            for key, value in values.items():
                raw_value = json.dumps(value) if isinstance(value, dict) else value
                exit_code, payload = run_cli(["keys", "set", key, "--value", raw_value, "--workspace", str(workspace), "--json"])
                self.assertEqual(exit_code, 0)

            exit_code, payload = run_cli(["defaults", "load", "--workspace", str(workspace), "--json"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "ready")
            self.assertFalse(payload["onboardingRequired"])
            self.assertIsNone(payload["onboardingCommand"])
            self.assertEqual(payload["currentMode"], "simple")
            self.assertEqual(payload["currentModeDefinition"]["push_policy"], "ask every time")

    def test_contract_values_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "keys",
                    "set",
                    "project.rules",
                    "--value",
                    "OPENAI_API_KEY=sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "--workspace",
                    str(workspace),
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 4)
            self.assertEqual(payload["error"]["code"], "unsafe_save_blocked")

    def test_invalid_contract_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(["keys", "get", "project.unknown", "--workspace", str(workspace), "--json"])

            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_key")

    def test_workflow_mode_contract_requires_fixed_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "keys",
                    "set",
                    "project.workflow.modes",
                    "--value",
                    json.dumps({"simple": {"description": "Partial mode."}}),
                    "--workspace",
                    str(workspace),
                    "--json",
                ]
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_value")
            self.assertEqual(payload["error"]["mode"], "simple")
            self.assertIn("autonomy", payload["error"]["missingFields"])


if __name__ == "__main__":
    unittest.main()
