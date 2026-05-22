from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path


DEFAULT_STORAGE_ROOT = Path.home() / ".codex" / "storage" / "4dreamteam" / "memory"


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
    lancedb_dir: Path


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def git_remote_for(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "config", "--get", "remote.origin.url"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    remote = result.stdout.strip()
    return remote or None


def workspace_identity(workspace: str | Path) -> WorkspaceIdentity:
    root = normalize_path(workspace)
    remote = git_remote_for(root)
    normalized_root = root.as_posix()
    normalized_remote = remote.strip() if remote else None
    identity_basis = normalized_remote or normalized_root
    display_label = root.name or "workspace"

    return WorkspaceIdentity(
        id=sha256_text(identity_basis),
        display_label=display_label,
        root_hash=sha256_text(normalized_root),
        git_remote_hash=sha256_text(normalized_remote) if normalized_remote else None,
    )


def resolve_storage_root(storage_root: str | Path | None = None) -> Path:
    return normalize_path(storage_root) if storage_root is not None else DEFAULT_STORAGE_ROOT


def workspace_paths(workspace: str | Path, storage_root: str | Path | None = None) -> WorkspacePaths:
    resolved_storage_root = resolve_storage_root(storage_root)
    identity = workspace_identity(workspace)
    workspace_dir = resolved_storage_root / "workspaces" / identity.id

    return WorkspacePaths(
        storage_root=resolved_storage_root,
        workspace_dir=workspace_dir,
        sqlite_path=workspace_dir / "state.sqlite3",
        lancedb_dir=workspace_dir / "lancedb",
    )
