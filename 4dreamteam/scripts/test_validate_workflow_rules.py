import tempfile
import unittest
from pathlib import Path

import validate_workflow_rules


class WorkflowRulesValidationTests(unittest.TestCase):
    def test_current_agent_facing_rules_pass(self):
        result = validate_workflow_rules.run()
        self.assertTrue(result["ok"], result["issues"])

    def test_direct_task_instruction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "rule.md"
            path.write_text("Read tasks/developer/TASK-0001.md before coding.\n", encoding="utf-8")
            result = validate_workflow_rules.run(["rule.md"], root=root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["issues"][0]["code"], "direct_task_paths")

    def test_tool_managed_storage_reference_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "rule.md"
            path.write_text("Use 4dt-board; tasks/developer/ is internal storage only.\n", encoding="utf-8")
            result = validate_workflow_rules.run(["rule.md"], root=root)
            self.assertTrue(result["ok"], result["issues"])

    def test_required_new_session_memory_recall_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = root / "4dreamteam" / "references" / "lead" / "preflight.md"
            memory = root / "4dreamteam" / "references" / "lead" / "memory.md"
            runtime = root / "docs" / "architecture" / "runtime-entrypoint.md"
            preflight.parent.mkdir(parents=True)
            runtime.parent.mkdir(parents=True)
            preflight.write_text("4dt-board --workspace . --json validate\n", encoding="utf-8")
            memory.write_text("Memory policy placeholder.\n", encoding="utf-8")
            runtime.write_text("one status line for each tool\n", encoding="utf-8")

            issues = validate_workflow_rules.validate_required_text(root)

            codes = {issue["code"] for issue in issues}
            self.assertIn("new_session_memory_recall", codes)

    def test_operator_memory_intent_requirements_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = root / "4dreamteam" / "references" / "lead" / "preflight.md"
            memory = root / "4dreamteam" / "references" / "lead" / "memory.md"
            runtime = root / "docs" / "architecture" / "runtime-entrypoint.md"
            preflight.parent.mkdir(parents=True)
            runtime.parent.mkdir(parents=True)
            preflight.write_text(
                "\n".join(
                    [
                        "4dt-memory defaults load --workspace . --json",
                        "4dt-memory onboarding questions --workspace . --json",
                        "4dt-board --workspace . --json validate",
                        "4dt-sources --workspace . --json registry validate",
                        "4dt-wiki --workspace . --json validate",
                        "4dt-memory doctor --workspace . --json",
                        "do not dump all memory into context",
                        "Repair commands require explicit operator confirmation.",
                    ]
                ),
                encoding="utf-8",
            )
            memory.write_text("Operator Memory Intent\nMemory Placement Policy\n", encoding="utf-8")
            runtime.write_text("reports each tool status\n", encoding="utf-8")

            issues = validate_workflow_rules.validate_required_text(root)

            codes = {issue["code"] for issue in issues}
            self.assertIn("role_scoped_recall", codes)
            self.assertIn("memory_intent_russian_phrase", codes)
            self.assertIn("memory_behavior_change_plus_lesson", codes)
            self.assertIn("memory_english_for_any_operator_language", codes)

    def test_contract_rules_via_semantic_search_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "rule.md"
            path.write_text(
                '4dt-memory search "project rules operator preferences active modes workflow constraints" --workspace . --json\n',
                encoding="utf-8",
            )
            result = validate_workflow_rules.run(["rule.md"], root=root)
            self.assertFalse(result["ok"])
            self.assertEqual(result["issues"][0]["code"], "contract_rules_via_semantic_search")


if __name__ == "__main__":
    unittest.main()
