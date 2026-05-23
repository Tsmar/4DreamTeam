from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fourdt_memory.paths import (
    DEFAULT_STORAGE_ROOT,
    resolve_storage_root,
    workspace_identity,
    workspace_paths,
)


class PathTests(unittest.TestCase):
    def test_default_storage_root_is_workspace_local(self) -> None:
        import tempfile

        self.assertEqual(DEFAULT_STORAGE_ROOT, Path(".4dt") / "memory")
        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            self.assertEqual(resolve_storage_root(workspace=workspace), workspace.resolve() / ".4dt" / "memory")

    def test_explicit_storage_root_controls_workspace_layout(self) -> None:
        with self.subTest("workspace layout"):
            import tempfile

            with tempfile.TemporaryDirectory() as raw_tmp:
                tmp_path = Path(raw_tmp)
                workspace = tmp_path / "workspace"
                storage = tmp_path / "storage"
                workspace.mkdir()

                paths = workspace_paths(workspace, storage)

                self.assertEqual(paths.storage_root, storage.resolve())
                self.assertEqual(paths.workspace_dir.parent, storage.resolve() / "workspaces")
                self.assertEqual(paths.sqlite_path, paths.workspace_dir / "state.sqlite3")
                self.assertEqual(paths.lancedb_dir, paths.workspace_dir / "lancedb")
                self.assertNotIn(workspace.resolve(), paths.sqlite_path.parents)

    def test_default_workspace_layout_stays_inside_workspace(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw_tmp:
            workspace = Path(raw_tmp) / "workspace"
            workspace.mkdir()

            paths = workspace_paths(workspace)

            self.assertEqual(paths.storage_root, workspace.resolve() / ".4dt" / "memory")
            self.assertIn(workspace.resolve(), paths.sqlite_path.parents)

    def test_workspace_identity_is_stable_and_does_not_store_raw_path(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp_path = Path(raw_tmp)
            workspace = tmp_path / "workspace"
            workspace.mkdir()

            first = workspace_identity(workspace)
            second = workspace_identity(workspace)

            self.assertEqual(first, second)
            self.assertEqual(first.display_label, "workspace")
            self.assertNotIn(str(workspace.resolve()), first.id)
            self.assertNotIn(str(workspace.resolve()), first.root_hash)

    def test_resolve_storage_root_accepts_override(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as raw_tmp:
            storage = Path(raw_tmp) / "storage"
            self.assertEqual(resolve_storage_root(storage), storage.resolve())


if __name__ == "__main__":
    unittest.main()
