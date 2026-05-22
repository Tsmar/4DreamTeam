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


class DoctorTests(unittest.TestCase):
    def test_doctor_missing_store_is_non_mutating_degraded_status(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            storage = tmp_path / "storage"
            workspace.mkdir()

            exit_code, payload = run_cli(
                ["doctor", "--workspace", str(workspace), "--storage-root", str(storage), "--json"]
            )

            self.assertEqual(exit_code, 3)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["status"], "not_initialized")
            self.assertIn("memory_store_not_initialized", payload["warnings"])
            self.assertFalse(storage.exists())


if __name__ == "__main__":
    unittest.main()
