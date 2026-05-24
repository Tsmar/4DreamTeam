from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


DEFAULT_STORAGE_ROOT = Path(".4dt") / "memory"


@dataclass(frozen=True)
class WorkspaceIdentity:
    id: str
    display_label: str
    root_hash: str
    git_remote_hash: str | None


@dataclass(frozen=True)
class WorkspacePaths:
    storage_root: Path
    workspace_dir: Path
    sqlite_path: Path


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def workspace_identity(workspace: str | Path) -> WorkspaceIdentity:
    root = normalize_path(workspace)
    normalized_root = root.as_posix()
    display_label = root.name or "workspace"

    return WorkspaceIdentity(
        id=sha256_text(normalized_root),
        display_label=display_label,
        root_hash=sha256_text(normalized_root),
        git_remote_hash=None,
    )


def resolve_storage_root(storage_root: str | Path | None = None, workspace: str | Path | None = None) -> Path:
    if storage_root is not None:
        return normalize_path(storage_root)
    if workspace is not None:
        return normalize_path(workspace) / DEFAULT_STORAGE_ROOT
    return normalize_path(DEFAULT_STORAGE_ROOT)


def workspace_paths(workspace: str | Path, storage_root: str | Path | None = None) -> WorkspacePaths:
    resolved_storage_root = resolve_storage_root(storage_root, workspace)
    workspace_dir = resolved_storage_root

    return WorkspacePaths(
        storage_root=resolved_storage_root,
        workspace_dir=workspace_dir,
        sqlite_path=workspace_dir / "db" / "state.sqlite3",
    )
