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


class JsonContractTests(unittest.TestCase):
    def test_json_envelope_fields_are_stable(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                ["init", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 0)
            for key in ("ok", "status", "warnings", "workspaceId", "storageRoot", "sqlitePath"):
                self.assertIn(key, payload)

    def test_not_initialized_error_shape_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                ["list", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "not_initialized")
            self.assertEqual(payload["warnings"], [])

    def test_unsafe_save_error_shape_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                [
                    "remember",
                    "api_key = sk_test_12345678901234567890",
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
            )

            self.assertEqual(exit_code, 4)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["status"], "unsafe_save_blocked")
            self.assertEqual(payload["error"]["code"], "unsafe_save_blocked")
            self.assertIn("reasons", payload["error"])
            self.assertEqual(payload["warnings"], [])


if __name__ == "__main__":
    unittest.main()
