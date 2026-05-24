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
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, json.loads(stdout.getvalue())


def remember_args(workspace: Path, storage: Path, content: str) -> list[str]:
    return [
        "remember",
        content,
        "--workspace",
        str(workspace),
        "--storage-root",
        str(storage),
        "--scope",
        "workspace",
        "--type",
        "constraint",
        "--source-type",
        "task",
        "--source-ref",
        "tasks/example.md",
        "--json",
    ]


class RedactionTests(unittest.TestCase):
    def test_private_key_token_and_secret_file_inputs_are_blocked(self) -> None:
        unsafe_inputs = [
            "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----",
            "api_key = sk_test_12345678901234567890",
            "OPENAI_API_KEY=sk-test-12345678901234567890",
        ]
        for content in unsafe_inputs:
            with self.subTest(content=content[:20]):
                with tempfile.TemporaryDirectory() as raw_tmp:
                    tmp_path = Path(raw_tmp)
                    workspace = tmp_path / "workspace"
                    storage = tmp_path / "storage"
                    workspace.mkdir()

                    exit_code, payload = run_cli(remember_args(workspace, storage, content))

                    self.assertEqual(exit_code, 4)
                    self.assertEqual(payload["status"], "unsafe_save_blocked")
                    self.assertEqual(payload["error"]["code"], "unsafe_save_blocked")
                    self.assertFalse(storage.exists())
                    self.assertNotIn(content, json.dumps(payload))

    def test_large_content_and_unaccepted_speculation_are_blocked_without_memory_rows(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            run_cli(["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"])

            large_content = "\n".join(f"line {index}" for index in range(90))
            exit_code, payload = run_cli(remember_args(workspace, storage, large_content))
            self.assertEqual(exit_code, 4)
            self.assertIn("large_artifact", payload["error"]["reasons"])

            exit_code, payload = run_cli(
                remember_args(workspace, storage, "Maybe this project should store hidden memories.")
            )
            self.assertEqual(exit_code, 4)
            self.assertIn("unaccepted_speculation", payload["error"]["reasons"])

            store = MemoryStore(workspace, storage)
            try:
                self.assertEqual(store.list_live_memory_items(), [])
                self.assertEqual(store.audit_entries("remember"), [])
            finally:
                store.close()

    def test_personal_data_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                remember_args(workspace, storage, "Customer contact is person@example.com.")
            )

            self.assertEqual(exit_code, 4)
            self.assertIn("personal_data", payload["error"]["reasons"])


if __name__ == "__main__":
    unittest.main()
