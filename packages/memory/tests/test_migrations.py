from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.migrations import schema_sql


class MigrationResourceTests(unittest.TestCase):
    def test_schema_sql_loads_from_filesystem_package(self) -> None:
        text = schema_sql()
        self.assertIn("CREATE TABLE IF NOT EXISTS memory_items", text)
        self.assertNotIn("memory_workspaces", text)

    def test_schema_sql_loads_from_zipimport_package(self) -> None:
        package_dir = Path(__file__).resolve().parents[1] / "src" / "fourdt_memory"
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            archive = tmp_path / "fourdt_memory_test.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                for name in ("__init__.py", "migrations.py", "schema.sql"):
                    zf.write(package_dir / name, f"fourdt_memory/{name}")

            script = (
                "from fourdt_memory.migrations import schema_sql; "
                "text = schema_sql(); "
                "assert 'CREATE TABLE IF NOT EXISTS memory_items' in text; "
                "assert 'memory_workspaces' not in text; "
                "print('ok')"
            )
            env = dict(os.environ)
            env["PYTHONPATH"] = str(archive)
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=tmp_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "ok")


if __name__ == "__main__":
    unittest.main()
