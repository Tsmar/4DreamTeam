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


def run_cli(args: list[str]) -> tuple[int, dict[str, object], str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = main(args)
    output = stdout.getvalue().strip()
    payload = json.loads(output) if output else {}
    return exit_code, payload, stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_init_doctor_list_and_get_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload, _stderr = run_cli(
                ["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["status"], "ready")
            self.assertIn("project.rules", payload["seededContracts"])

            exit_code, payload, _stderr = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertIn(exit_code, (0, 3))
            self.assertIn(payload["status"], ("ready", "degraded_setup_required"))
            self.assertIn("sqlite", payload)

            exit_code, payload, _stderr = run_cli(
                ["list", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["items"], [])

            exit_code, payload, _stderr = run_cli(
                ["onboarding", "questions", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["questions"], [])

            store = MemoryStore(workspace, storage)
            store.initialize()
            try:
                memory_id = store.create_memory_item(
                    scope="workspace",
                    type="decision",
                    content="Use local storage.",
                    source_type="report",
                    source_ref="reports/example.md",
                )
            finally:
                store.close()

            exit_code, payload, _stderr = run_cli(
                ["get", memory_id, "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["item"]["id"], memory_id)

    def test_get_not_found_is_structured_user_error(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            run_cli(["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"])

            exit_code, payload, _stderr = run_cli(
                ["get", "mem_missing", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "not_found")

    def test_init_seeds_only_missing_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload, _stderr = run_cli(
                ["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["seededContracts"]), 9)

            exit_code, payload, _stderr = run_cli(
                [
                    "keys",
                    "set",
                    "project.rules",
                    "--value",
                    "Custom operator rule.",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)

            exit_code, payload, _stderr = run_cli(
                ["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["seededContracts"], [])

            exit_code, payload, _stderr = run_cli(
                ["keys", "get", "project.rules", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )
            self.assertEqual(payload["key"]["entry"]["value"], "Custom operator rule.")

    def test_export_requires_initialized_store(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload, _stderr = run_cli(
                ["export", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            self.assertEqual(payload["status"], "degraded_setup_required")
            self.assertEqual(payload["error"]["code"], "not_initialized")


if __name__ == "__main__":
    unittest.main()
