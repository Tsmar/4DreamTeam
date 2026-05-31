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

    def test_schema_status_lists_recorded_domains(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            db = workspace / ".4dt" / "db.sqlite3"
            db.parent.mkdir(parents=True)
            with sqlite3.connect(db) as connection:
                connection.execute(
                    """
                    CREATE TABLE tool_schema_versions (
                      domain TEXT PRIMARY KEY,
                      schema_version INTEGER NOT NULL,
                      schema_hash TEXT NOT NULL,
                      tool_version TEXT NOT NULL DEFAULT '',
                      applied_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "INSERT INTO tool_schema_versions VALUES ('memory', 3, 'abc', '0.5.7', '2026-06-01T00:00:00Z')"
                )

            exit_code, payload = run_cli(["--workspace", str(workspace), "--json", "schema", "status"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["schema"]["domains"][0]["domain"], "memory")
            self.assertEqual(payload["schema"]["domains"][0]["schemaVersion"], 3)

    def test_migration_plan_and_apply_copy_table_without_row_content_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp)
            db = workspace / ".4dt" / "db.sqlite3"
            db.parent.mkdir(parents=True)
            with sqlite3.connect(db) as connection:
                connection.execute("CREATE TABLE old_items (id TEXT PRIMARY KEY, body TEXT NOT NULL)")
                connection.execute("CREATE TABLE new_items (id TEXT PRIMARY KEY, body TEXT NOT NULL, importance REAL NOT NULL)")
                connection.execute("INSERT INTO old_items VALUES ('one', 'secret body')")
                connection.execute(
                    """
                    CREATE TABLE tool_schema_versions (
                      domain TEXT PRIMARY KEY,
                      schema_version INTEGER NOT NULL,
                      schema_hash TEXT NOT NULL,
                      tool_version TEXT NOT NULL DEFAULT '',
                      applied_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "INSERT INTO tool_schema_versions VALUES ('memory', 3, 'old-hash', '0.5.7', '2026-06-01T00:00:00Z')"
                )
            spec = workspace / "migration.json"
            spec.write_text(
                json.dumps(
                    {
                        "id": "memory-test",
                        "domain": "memory",
                        "from": {"schemaVersion": 3, "schemaHash": "old-hash"},
                        "to": {"schemaVersion": 4, "schemaHash": "new-hash"},
                        "steps": [
                            {
                                "op": "copy_table",
                                "fromTable": "old_items",
                                "toTable": "new_items",
                                "columns": {"id": "id", "body": "body"},
                                "defaults": {"importance": 0.7},
                            },
                            {"op": "validate_counts", "leftTable": "old_items", "rightTable": "new_items"},
                            {"op": "validate_not_null", "table": "new_items", "columns": ["id", "body", "importance"]},
                            {"op": "record_schema"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code, payload = run_cli(["--workspace", str(workspace), "--json", "migrate", "plan", "--file", str(spec)])
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["migration"]["steps"][0]["sourceRows"], 1)
            self.assertNotIn("secret body", json.dumps(payload))

            exit_code, payload = run_cli(
                ["--workspace", str(workspace), "--json", "migrate", "apply", "--file", str(spec), "--backup"]
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue(Path(payload["migration"]["backup"]["backup"]).exists())
            self.assertNotIn("secret body", json.dumps(payload))
            with sqlite3.connect(db) as connection:
                row = connection.execute("SELECT body, importance FROM new_items WHERE id = 'one'").fetchone()
                schema = connection.execute("SELECT schema_version, schema_hash FROM tool_schema_versions WHERE domain = 'memory'").fetchone()
            self.assertEqual(row, ("secret body", 0.7))
            self.assertEqual(schema, (4, "new-hash"))


if __name__ == "__main__":
    unittest.main()
