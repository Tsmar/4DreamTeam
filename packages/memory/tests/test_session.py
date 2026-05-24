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


class SessionTests(unittest.TestCase):
    def test_session_set_and_get_json_object_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "session",
                    "set",
                    "session-1",
                    '{"step":"import"}',
                    "--ttl-seconds",
                    "60",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["status"], "session_saved")
            self.assertIn("expiresAt", payload)

            exit_code, payload = run_cli(
                [
                    "session",
                    "get",
                    "session-1",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["state"], {"step": "import"})

    def test_session_rejects_invalid_json_and_oversized_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "session",
                    "set",
                    "session-1",
                    "[]",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "invalid_session_json")

            exit_code, payload = run_cli(
                [
                    "session",
                    "set",
                    "session-2",
                    json.dumps({"value": "x" * 9000}),
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["error"]["code"], "session_too_large")

    def test_session_expiry_returns_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()
            run_cli(
                [
                    "session",
                    "set",
                    "session-1",
                    '{"step":"short"}',
                    "--ttl-seconds",
                    "1",
                    "--workspace",
                    str(workspace),
                    "--storage-root",
                    str(storage),
                    "--json",
                ]
            )

            from fourdt_memory.sqlite_store import MemoryStore

            store = MemoryStore(workspace, storage)
            try:
                self.assertIsNone(store.get_session_record("session-1", now="2999-01-01T00:00:00Z"))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
