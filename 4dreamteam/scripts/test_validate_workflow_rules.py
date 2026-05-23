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
            workflows = root / "docs" / "workflows.md"
            preflight.parent.mkdir(parents=True)
            workflows.parent.mkdir(parents=True)
            preflight.write_text("4dt-board --workspace . --json validate\n", encoding="utf-8")
            workflows.write_text("one status line for each tool\n", encoding="utf-8")

            issues = validate_workflow_rules.validate_required_text(root)

            codes = {issue["code"] for issue in issues}
            self.assertIn("new_session_memory_recall", codes)


if __name__ == "__main__":
    unittest.main()
