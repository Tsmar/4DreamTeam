from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_db.cli import main


def run_cli(args: list[str]) -> tuple[int, dict[str, object]]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(args)
    output = stdout.getvalue().strip()
    return exit_code, json.loads(output) if output else {}


class DbCliTests(unittest.TestCase):
    def test_backup_create_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            db = workspace / ".4dt" / "db.sqlite3"
            db.parent.mkdir(parents=True)
            with sqlite3.connect(db) as connection:
                connection.execute("CREATE TABLE sample (id TEXT PRIMARY KEY)")
                connection.execute("INSERT INTO sample VALUES ('one')")

            exit_code, payload = run_cli(["--workspace", str(workspace), "--json", "backup", "create"])
            self.assertEqual(exit_code, 0)
            backup = Path(payload["backup"]["backup"])
            self.assertTrue(backup.exists())
            with sqlite3.connect(backup) as connection:
                self.assertEqual(connection.execute("SELECT id FROM sample").fetchone()[0], "one")

            exit_code, payload = run_cli(["--workspace", str(workspace), "--json", "backup", "list"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(payload["backups"]), 1)


if __name__ == "__main__":
    unittest.main()
