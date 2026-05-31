from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


REGISTRY_VERSION = 1
INDEX_VERSION = 1
RUNTIME_ROOT = Path(".4dt")
DEFAULT_LIMIT = 50
MAX_GET_BYTES = 32_000
IGNORE_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".cache",
    ".next",
    ".nuxt",
    ".vite",
    ".turbo",
    ".vercel",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
FORBIDDEN_NAMES = {".env"}
FORBIDDEN_PREFIXES = (".env.",)
FORBIDDEN_SUFFIXES = (".pem", ".key", ".p12", ".dump")


@dataclass
class Source:
    id: str
    path: str
    label: str
    kind: str
    added_at: str


@dataclass
class IgnoreRule:
    pattern: str
    negated: bool
    directory_only: bool
    anchored: bool
    has_slash: bool


class UserError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def kebab(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "source"


def sqlite_path(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "db.sqlite3"


def connect(workspace: Path) -> sqlite3.Connection:
    (workspace / RUNTIME_ROOT).mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path(workspace))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    ensure_schema(connection)
    return connection


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS source_registry (
          id TEXT PRIMARY KEY,
          path TEXT NOT NULL UNIQUE,
          label TEXT NOT NULL,
          kind TEXT NOT NULL,
          added_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS source_inventory (
          source_id TEXT NOT NULL,
          path TEXT NOT NULL,
          relative_path TEXT NOT NULL,
          source_path TEXT NOT NULL,
          kind TEXT NOT NULL,
          status TEXT NOT NULL,
          reason TEXT NOT NULL,
          size INTEGER,
          mtime REAL,
          PRIMARY KEY (source_id, path)
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_source_inventory_kind ON source_inventory(kind)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_source_inventory_relative_path ON source_inventory(relative_path)")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS source_index (
          id TEXT PRIMARY KEY,
          index_json TEXT NOT NULL,
          manifest_json TEXT NOT NULL,
          generated_at TEXT NOT NULL,
          registry_sha256 TEXT NOT NULL,
          source_count INTEGER NOT NULL,
          entry_count INTEGER NOT NULL
        )
        """
    )
    connection.commit()


def workspace_source(workspace: Path) -> Source:
    return Source("workspace-sources", "sources", "Workspace sources", "directory", "builtin")


def normalize_source_path(workspace: Path, value: str) -> str:
    raw = Path(value).expanduser()
    if raw.is_absolute():
        try:
            return raw.resolve(strict=False).as_posix()
        except OSError:
            return raw.as_posix()
    return raw.as_posix()


def resolve_source_path(workspace: Path, source: Source) -> Path:
    raw = Path(source.path).expanduser()
    if raw.is_absolute():
        return raw.resolve(strict=False)
    return (workspace / raw).resolve(strict=False)


def source_id(path: str, label: str | None = None) -> str:
    base = label or Path(path).name or path
    return kebab(base)


def ensure_registry(workspace: Path) -> None:
    connection = connect(workspace)
    connection.close()


def read_registry(workspace: Path) -> list[Source]:
    connection = connect(workspace)
    try:
        rows = connection.execute(
            """
            SELECT id, path, label, kind, added_at
            FROM source_registry
            ORDER BY id
            """
        ).fetchall()
        return [Source(id=row["id"], path=row["path"], label=row["label"], kind=row["kind"], added_at=row["added_at"]) for row in rows]
    finally:
        connection.close()


def all_sources(workspace: Path) -> list[Source]:
    return [workspace_source(workspace), *read_registry(workspace)]


def write_registry(workspace: Path, sources: list[Source]) -> None:
    connection = connect(workspace)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM source_registry")
        connection.executemany(
            """
            INSERT INTO source_registry (id, path, label, kind, added_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(source.id, source.path, source.label, source.kind, source.added_at) for source in sources],
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def registry_sha256(workspace: Path) -> str:
    value = [source.__dict__ for source in read_registry(workspace)]
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True))


def source_kind(path: Path) -> str:
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return "missing"


def source_status(path: Path) -> tuple[str, str]:
    name = path.name
    if name in FORBIDDEN_NAMES or any(name.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        return "forbidden", "secret-name"
    if any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
        return "forbidden", "secret-suffix"
    if name in IGNORE_NAMES:
        return "ignored", "ignore-name"
    return "active", ""


def parse_gitignore_line(raw_line: str) -> IgnoreRule | None:
    line = raw_line.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"):
        return None
    negated = line.startswith("!")
    if negated:
        line = line[1:]
    if line.startswith("\\#") or line.startswith("\\!"):
        line = line[1:]
    line = line.strip()
    if not line:
        return None
    directory_only = line.endswith("/")
    if directory_only:
        line = line.rstrip("/")
    anchored = line.startswith("/")
    if anchored:
        line = line.lstrip("/")
    if not line:
        return None
    return IgnoreRule(
        pattern=line,
        negated=negated,
        directory_only=directory_only,
        anchored=anchored,
        has_slash="/" in line,
    )


def load_gitignore_rules(root: Path) -> list[IgnoreRule]:
    if not root.is_dir():
        return []
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        return []
    try:
        lines = gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return [rule for line in lines if (rule := parse_gitignore_line(line))]


def rule_matches(rule: IgnoreRule, relative_path: str, kind: str) -> bool:
    relative_path = relative_path.strip("/")
    if not relative_path or relative_path == ".":
        return False
    parts = relative_path.split("/")
    pattern = rule.pattern

    if rule.directory_only:
        directories = parts if kind == "directory" else parts[:-1]
        if rule.has_slash or rule.anchored:
            candidates = ["/".join(parts[: index + 1]) for index in range(len(directories))]
            return any(candidate == pattern or candidate.startswith(f"{pattern}/") for candidate in candidates)
        return any(fnmatch(part, pattern) for part in directories)

    if rule.has_slash or rule.anchored:
        if fnmatch(relative_path, pattern):
            return True
        if rule.anchored:
            return False
        return any(fnmatch("/".join(parts[index:]), pattern) for index in range(1, len(parts)))
    return any(fnmatch(part, pattern) for part in parts)


def gitignore_status(root: Path, path: Path, kind: str, rules: list[IgnoreRule]) -> tuple[str, str]:
    if not rules:
        return "active", ""
    try:
        relative = "." if path == root else path.relative_to(root).as_posix()
    except ValueError:
        return "active", ""
    ignored = False
    for rule in rules:
        if rule_matches(rule, relative, kind):
            ignored = not rule.negated
    if ignored:
        return "ignored", "gitignore"
    return "active", ""


def path_policy_status(root: Path, path: Path, kind: str, gitignore_rules: list[IgnoreRule]) -> tuple[str, str]:
    direct_status, direct_reason = source_status(path)
    if direct_status != "active":
        return direct_status, direct_reason
    try:
        relative = path.relative_to(root)
    except ValueError:
        return gitignore_status(root, path, kind, gitignore_rules)
    ancestors = [root / partial for partial in reversed([relative, *relative.parents]) if partial != Path(".")]
    for ancestor in ancestors:
        status, reason = source_status(ancestor)
        if status != "active":
            return status, reason
    return gitignore_status(root, path, kind, gitignore_rules)


def validate_registry(workspace: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen: set[str] = set()
    for source in all_sources(workspace):
        if source.id in seen:
            errors.append(issue("duplicate_source_id", source.path, f"Duplicate source id: {source.id}"))
        seen.add(source.id)
        path = resolve_source_path(workspace, source)
        if not path.exists():
            errors.append(issue("missing_source", source.path, "Source path does not exist."))
            continue
        status, reason = source_status(path)
        if status == "forbidden":
            errors.append(issue("forbidden_source", source.path, f"Source path is forbidden: {reason}."))
        elif status == "ignored":
            warnings.append(issue("ignored_source", source.path, f"Source path is ignored: {reason}."))
    return errors, warnings


def issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def add_source(workspace: Path, raw_path: str, label: str | None, operator_approved: bool) -> dict[str, Any]:
    if not operator_approved:
        raise UserError(
            "operator_approval_required",
            "Adding an external source requires --operator-approved because it may be read and may be modified by executors/developers.",
        )
    sources = read_registry(workspace)
    normalized = normalize_source_path(workspace, raw_path)
    resolved = (workspace / normalized).resolve(strict=False) if not Path(normalized).is_absolute() else Path(normalized)
    kind = source_kind(resolved)
    if kind == "missing":
        raise UserError("missing_source", f"Source path does not exist: {raw_path}")
    new_id = source_id(normalized, label)
    existing_ids = {source.id for source in sources}
    if new_id in existing_ids:
        suffix = 2
        while f"{new_id}-{suffix}" in existing_ids:
            suffix += 1
        new_id = f"{new_id}-{suffix}"
    if any(source.path == normalized for source in sources):
        raise UserError("source_exists", f"Source is already registered: {normalized}")
    source = Source(new_id, normalized, label or Path(normalized).name or new_id, kind, iso_now())
    write_registry(workspace, [*sources, source])
    return {"source": source.__dict__, "warning": "source may be read and may be modified by executors/developers"}


def remove_source(workspace: Path, source_id_or_path: str) -> dict[str, Any]:
    sources = read_registry(workspace)
    kept = [source for source in sources if source.id != source_id_or_path and source.path != source_id_or_path]
    if len(kept) == len(sources):
        raise UserError("not_found", f"External source not found: {source_id_or_path}")
    write_registry(workspace, kept)
    return {"removed": source_id_or_path}


def entry_for_path(
    workspace: Path,
    source: Source,
    path: Path,
    root: Path | None = None,
    gitignore_rules: list[IgnoreRule] | None = None,
) -> dict[str, Any]:
    root = root or resolve_source_path(workspace, source)
    gitignore_rules = gitignore_rules or []
    kind = source_kind(path)
    status, reason = path_policy_status(root, path, kind, gitignore_rules)
    try:
        stat_value = path.stat()
        size = stat_value.st_size
        mtime = stat_value.st_mtime
    except OSError:
        size = None
        mtime = None
        status = "unreadable"
        reason = "stat-error"
    try:
        relative = "." if path == root else path.relative_to(root).as_posix()
    except ValueError:
        relative = path.as_posix()
    return {
        "source_id": source.id,
        "source_path": source.path,
        "path": path.as_posix(),
        "relative_path": relative,
        "kind": kind,
        "status": status,
        "reason": reason,
        "size": size,
        "mtime": mtime,
    }


def walk_entries(workspace: Path, source: Source) -> list[dict[str, Any]]:
    root = resolve_source_path(workspace, source)
    gitignore_rules = load_gitignore_rules(root)
    entries: list[dict[str, Any]] = []

    def visit(path: Path) -> None:
        entry = entry_for_path(workspace, source, path, root, gitignore_rules)
        if entry["status"] in {"forbidden", "ignored"}:
            return
        entries.append(entry)
        if entry["kind"] != "directory" or entry["status"] != "active":
            return
        try:
            children = sorted(path.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            entries.append({**entry, "status": "unreadable", "reason": "list-error"})
            return
        for child in children:
            visit(child)

    if root.exists():
        visit(root)
    else:
        entries.append(entry_for_path(workspace, source, root, root, gitignore_rules))
    return entries


def build_index(workspace: Path) -> dict[str, Any]:
    errors, warnings = validate_registry(workspace)
    entries: list[dict[str, Any]] = []
    for source in all_sources(workspace):
        entries.extend(walk_entries(workspace, source))
    index = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "registryStore": ".4dt/db.sqlite3:source_registry",
        "registrySha256": registry_sha256(workspace),
        "indexStore": ".4dt/db.sqlite3:source_inventory",
        "sourceCount": len(all_sources(workspace)),
        "entryCount": len(entries),
        "entries": entries,
        "issues": {"errors": errors, "warnings": warnings},
    }
    manifest = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": index["generatedAt"],
        "registryStore": index["registryStore"],
        "registrySha256": index["registrySha256"],
        "indexStore": index["indexStore"],
        "sourceCount": index["sourceCount"],
        "entryCount": index["entryCount"],
    }
    write_index(workspace, index, manifest, entries)
    return index


def entry_values(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (
        entry["source_id"],
        entry["path"],
        entry["relative_path"],
        entry["source_path"],
        entry["kind"],
        entry["status"],
        entry["reason"],
        entry["size"],
        entry["mtime"],
    )


def entry_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "source_id": row["source_id"],
        "source_path": row["source_path"],
        "path": row["path"],
        "relative_path": row["relative_path"],
        "kind": row["kind"],
        "status": row["status"],
        "reason": row["reason"],
        "size": row["size"],
        "mtime": row["mtime"],
    }


def write_index(workspace: Path, index: dict[str, Any], manifest: dict[str, Any], entries: list[dict[str, Any]]) -> None:
    connection = connect(workspace)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM source_inventory")
        connection.executemany(
            """
            INSERT INTO source_inventory (
              source_id, path, relative_path, source_path, kind, status, reason, size, mtime
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [entry_values(entry) for entry in entries],
        )
        connection.execute(
            """
            INSERT INTO source_index
            (id, index_json, manifest_json, generated_at, registry_sha256, source_count, entry_count)
            VALUES ('default', ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              index_json = excluded.index_json,
              manifest_json = excluded.manifest_json,
              generated_at = excluded.generated_at,
              registry_sha256 = excluded.registry_sha256,
              source_count = excluded.source_count,
              entry_count = excluded.entry_count
            """,
            (
                json.dumps(index, ensure_ascii=False, sort_keys=True),
                json.dumps(manifest, ensure_ascii=False, sort_keys=True),
                index["generatedAt"],
                index["registrySha256"],
                index["sourceCount"],
                index["entryCount"],
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def load_index(workspace: Path) -> dict[str, Any]:
    connection = connect(workspace)
    try:
        row = connection.execute("SELECT index_json FROM source_index WHERE id = 'default'").fetchone()
    finally:
        connection.close()
    if row is None:
        return build_index(workspace)
    try:
        value = json.loads(row["index_json"])
    except json.JSONDecodeError:
        return build_index(workspace)
    return value if isinstance(value, dict) else build_index(workspace)


def check_index(workspace: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    index = load_index(workspace)
    issues: list[dict[str, str]] = []
    if index.get("registrySha256") != registry_sha256(workspace):
        issues.append(issue("stale_index", "sources", "Source registry changed after index build."))
    errors, warnings = validate_registry(workspace)
    issues.extend(errors)
    issues.extend(warnings)
    return index, issues


def boundary_for_path(workspace: Path, raw_path: str) -> Source | None:
    target = Path(raw_path).expanduser()
    if not target.is_absolute():
        target = (workspace / target).resolve(strict=False)
    else:
        target = target.resolve(strict=False)
    for source in all_sources(workspace):
        root = resolve_source_path(workspace, source)
        try:
            target.relative_to(root)
            return source
        except ValueError:
            continue
    return None


def registry_list(workspace: Path) -> list[dict[str, Any]]:
    return [source.__dict__ for source in all_sources(workspace)]


def list_entries(workspace: Path, kind: str | None, limit: int) -> list[dict[str, Any]]:
    index = load_index(workspace)
    entries = index["entries"]
    if kind == "boundary":
        return registry_list(workspace)[:limit]
    if kind:
        entries = [entry for entry in entries if entry["kind"] == kind]
    return entries[:limit]


def search_entries(workspace: Path, query: str, limit: int) -> list[dict[str, Any]]:
    query_lower = query.lower()
    matches = []
    for entry in load_index(workspace)["entries"]:
        haystack = f"{entry['path']} {entry['relative_path']} {entry['source_id']}".lower()
        if query_lower in haystack:
            matches.append(entry)
    return matches[:limit]


def get_path(workspace: Path, raw_path: str, range_value: str | None) -> dict[str, Any]:
    source = boundary_for_path(workspace, raw_path)
    if not source:
        raise UserError("source_not_allowed", f"Path is outside allowed source boundaries: {raw_path}")
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = (workspace / path).resolve(strict=False)
    else:
        path = path.resolve(strict=False)
    root = resolve_source_path(workspace, source)
    status, reason = path_policy_status(root, path, source_kind(path), load_gitignore_rules(root))
    if status in {"forbidden", "ignored"}:
        raise UserError("source_path_excluded", f"Path is excluded from source access: {reason}.")
    if not path.is_file():
        raise UserError("not_file", f"Path is not a readable file: {raw_path}")
    size = path.stat().st_size
    start = 1
    end: int | None = None
    if range_value:
        match = re.match(r"^(\d+):(\d+)$", range_value)
        if not match:
            raise UserError("invalid_range", "Range must use start:end line numbers.")
        start = int(match.group(1))
        end = int(match.group(2))
    elif size > MAX_GET_BYTES:
        raise UserError("range_required", f"File is larger than {MAX_GET_BYTES} bytes; use --range.")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = lines[start - 1 : end]
    return {
        "path": path.as_posix(),
        "source_id": source.id,
        "range": {"start": start, "end": end or len(lines)},
        "content": "\n".join(selected),
    }


def stats(workspace: Path) -> dict[str, Any]:
    index = load_index(workspace)
    extensions: dict[str, int] = {}
    for entry in index["entries"]:
        if entry["kind"] == "file":
            suffix = Path(entry["path"]).suffix or "[none]"
            extensions[suffix] = extensions.get(suffix, 0) + 1
    return {
        "sourceCount": index["sourceCount"],
        "entryCount": index["entryCount"],
        "topExtensions": sorted(extensions.items(), key=lambda item: (-item[1], item[0]))[:10],
        "generatedAt": index["generatedAt"],
        "issues": index["issues"],
    }


def payload(ok: bool, status: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "status": status, **extra}


def print_result(value: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    print(json.dumps(value, indent=2, ensure_ascii=False))


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).resolve()
    if args.action == "registry-add":
        return 0, payload(True, "ready", **add_source(workspace, args.path, args.label, args.operator_approved))
    if args.action == "registry-remove":
        return 0, payload(True, "ready", **remove_source(workspace, args.source))
    if args.action == "registry-list":
        ensure_registry(workspace)
        return 0, payload(True, "ready", sources=registry_list(workspace))
    if args.action == "registry-validate":
        ensure_registry(workspace)
        errors, warnings = validate_registry(workspace)
        return (0 if not errors else 2), payload(True, "ready" if not errors else "issues", errors=errors, warnings=warnings)
    if args.action == "index-build":
        index = build_index(workspace)
        return 0, payload(True, "ready", index={key: index[key] for key in ("generatedAt", "sourceCount", "entryCount", "issues")})
    if args.action == "index-check":
        _index, issues = check_index(workspace)
        return (0 if not issues else 2), payload(True, "ready" if not issues else "issues", issues=issues)
    if args.action == "list":
        return 0, payload(True, "ready", items=list_entries(workspace, args.kind, args.limit))
    if args.action == "search":
        return 0, payload(True, "ready", matches=search_entries(workspace, args.query, args.limit), limit=args.limit)
    if args.action == "get":
        return 0, payload(True, "ready", file=get_path(workspace, args.path, args.range))
    if args.action == "stats":
        return 0, payload(True, "ready", stats=stats(workspace))
    raise UserError("unknown_command", f"Unknown command: {args.action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="4dt-sources",
        description="Manage approved source boundaries, source indexes, safe search, and exact snippet reads.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Agent workflow:
  - Use registry list/validate to confirm approved boundaries.
  - External paths require registry add --operator-approved.
  - Prefer get --range for focused reads instead of broad file dumps.""",
    )
    parser.add_argument("--workspace", default=".", help="Workspace path. Defaults to the current directory.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output for agents.")
    sub = parser.add_subparsers(dest="action", required=True)
    registry = sub.add_parser("registry", help="Manage approved source boundaries.")
    registry_sub = registry.add_subparsers(dest="registry_action", required=True)
    registry_add = registry_sub.add_parser(
        "add",
        help="Register an approved source boundary. External paths require explicit operator approval.",
        description="Register an approved source boundary. External paths require explicit operator approval.",
    )
    registry_add.add_argument("path", help="Source path to register.")
    registry_add.add_argument("--label", help="Optional source label.")
    registry_add.add_argument(
        "--operator-approved",
        action="store_true",
        help="Confirm the operator approved this source boundary, required for paths outside workspace sources/.",
    )
    registry_add.set_defaults(action="registry-add")
    registry_remove = registry_sub.add_parser("remove", help="Remove an approved source boundary.")
    registry_remove.add_argument("source")
    registry_remove.set_defaults(action="registry-remove")
    registry_list_parser = registry_sub.add_parser("list", help="List approved source boundaries.")
    registry_list_parser.set_defaults(action="registry-list")
    registry_validate = registry_sub.add_parser("validate", help="Validate source registry boundaries.")
    registry_validate.set_defaults(action="registry-validate")
    index = sub.add_parser("index", help="Build or check the approved source index.")
    index_sub = index.add_subparsers(dest="index_action", required=True)
    index_build = index_sub.add_parser("build")
    index_build.set_defaults(action="index-build")
    index_check = index_sub.add_parser("check")
    index_check.set_defaults(action="index-check")
    list_parser = sub.add_parser("list", help="List indexed boundaries, files, or directories.")
    list_parser.add_argument("--kind", choices=("boundary", "file", "directory"), help="Inventory item kind.")
    list_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum items to return.")
    search = sub.add_parser("search", help="Search approved source inventory. Prefer 4dt-search for cross-domain discovery.")
    search.add_argument("query", help="Plain text query.")
    search.add_argument("--limit", type=int, default=10, help="Maximum matches to return.")
    get = sub.add_parser("get", help="Read an approved source path, optionally constrained to a line range.")
    get.add_argument("path", help="Approved source path or indexed relative path.")
    get.add_argument("--range", help="Line range start:end. Recommended for focused agent reads.")
    sub.add_parser("stats", help="Show indexed source inventory statistics.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        exit_code, result = command(args)
    except UserError as error:
        result = payload(False, "error", error={"code": error.code, "message": error.message})
        print_result(result, args.json)
        return 1
    print_result(result, args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
