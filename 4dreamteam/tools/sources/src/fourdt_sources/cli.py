from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
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


def sources_runtime_dir(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "sources"


def registry_path(workspace: Path) -> Path:
    return sources_runtime_dir(workspace) / "registry.md"


def index_dir(workspace: Path) -> Path:
    return sources_runtime_dir(workspace) / "index"


def index_path(workspace: Path) -> Path:
    return index_dir(workspace) / "index.json"


def manifest_path(workspace: Path) -> Path:
    return index_dir(workspace) / "manifest.json"


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
    file = registry_path(workspace)
    if file.exists():
        return
    file.parent.mkdir(parents=True, exist_ok=True)
    write_registry(workspace, [])


def read_registry(workspace: Path) -> list[Source]:
    ensure_registry(workspace)
    text = registry_path(workspace).read_text(encoding="utf-8")
    sources: list[Source] = []
    for match in re.finditer(r"<!--\s*source\s+([\s\S]*?)-->", text):
        meta: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
        if meta.get("id") and meta.get("path"):
            sources.append(
                Source(
                    id=meta["id"],
                    path=meta["path"],
                    label=meta.get("label", meta["id"]),
                    kind=meta.get("kind", "unknown"),
                    added_at=meta.get("added_at", ""),
                )
            )
    return sources


def all_sources(workspace: Path) -> list[Source]:
    return [workspace_source(workspace), *read_registry(workspace)]


def write_registry(workspace: Path, sources: list[Source]) -> None:
    lines = [
        "# Source Registry",
        "",
        "This file is maintained by `4dt-sources`. Agents use `4dt-sources` commands instead of editing it directly.",
        "",
        "Workspace `sources/` is always an allowed source boundary. External file and directory boundaries are listed below.",
        "",
        "## External Sources",
        "",
    ]
    if not sources:
        lines.append("No external sources are registered.")
        lines.append("")
    for source in sources:
        lines.extend(
            [
                f"### {source.label}",
                "",
                "<!-- source",
                f"id: {source.id}",
                f"path: {source.path}",
                f"label: {source.label}",
                f"kind: {source.kind}",
                f"added_at: {source.added_at}",
                "-->",
                "",
            ]
        )
    registry_path(workspace).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


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


def entry_for_path(workspace: Path, source: Source, path: Path) -> dict[str, Any]:
    status, reason = source_status(path)
    try:
        stat_value = path.stat()
        size = stat_value.st_size
        mtime = stat_value.st_mtime
    except OSError:
        size = None
        mtime = None
        status = "unreadable"
        reason = "stat-error"
    root = resolve_source_path(workspace, source)
    try:
        relative = "." if path == root else path.relative_to(root).as_posix()
    except ValueError:
        relative = path.as_posix()
    return {
        "source_id": source.id,
        "source_path": source.path,
        "path": path.as_posix(),
        "relative_path": relative,
        "kind": source_kind(path),
        "status": status,
        "reason": reason,
        "size": size,
        "mtime": mtime,
    }


def walk_entries(workspace: Path, source: Source) -> list[dict[str, Any]]:
    root = resolve_source_path(workspace, source)
    entries: list[dict[str, Any]] = []

    def visit(path: Path) -> None:
        entry = entry_for_path(workspace, source, path)
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
        entries.append(entry_for_path(workspace, source, root))
    return entries


def build_index(workspace: Path) -> dict[str, Any]:
    errors, warnings = validate_registry(workspace)
    entries: list[dict[str, Any]] = []
    for source in all_sources(workspace):
        entries.extend(walk_entries(workspace, source))
    registry_text = registry_path(workspace).read_text(encoding="utf-8") if registry_path(workspace).exists() else ""
    index = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "registryPath": "sources",
        "registrySha256": sha256(registry_text),
        "sourceCount": len(all_sources(workspace)),
        "entryCount": len(entries),
        "entries": entries,
        "issues": {"errors": errors, "warnings": warnings},
    }
    index_dir(workspace).mkdir(parents=True, exist_ok=True)
    write_json(index_path(workspace), index)
    manifest = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": index["generatedAt"],
        "registryPath": "sources",
        "registrySha256": index["registrySha256"],
        "sourceCount": index["sourceCount"],
        "entryCount": index["entryCount"],
    }
    write_json(manifest_path(workspace), manifest)
    return index


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_index(workspace: Path) -> dict[str, Any]:
    if not index_path(workspace).exists():
        return build_index(workspace)
    try:
        return json.loads(index_path(workspace).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return build_index(workspace)


def check_index(workspace: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    index = load_index(workspace)
    issues: list[dict[str, str]] = []
    registry_text = registry_path(workspace).read_text(encoding="utf-8") if registry_path(workspace).exists() else ""
    if index.get("registrySha256") != sha256(registry_text):
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
    parser = argparse.ArgumentParser(prog="4dt-sources")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="action", required=True)
    registry = sub.add_parser("registry")
    registry_sub = registry.add_subparsers(dest="registry_action", required=True)
    registry_add = registry_sub.add_parser("add")
    registry_add.add_argument("path")
    registry_add.add_argument("--label")
    registry_add.add_argument("--operator-approved", action="store_true")
    registry_add.set_defaults(action="registry-add")
    registry_remove = registry_sub.add_parser("remove")
    registry_remove.add_argument("source")
    registry_remove.set_defaults(action="registry-remove")
    registry_list_parser = registry_sub.add_parser("list")
    registry_list_parser.set_defaults(action="registry-list")
    registry_validate = registry_sub.add_parser("validate")
    registry_validate.set_defaults(action="registry-validate")
    index = sub.add_parser("index")
    index_sub = index.add_subparsers(dest="index_action", required=True)
    index_build = index_sub.add_parser("build")
    index_build.set_defaults(action="index-build")
    index_check = index_sub.add_parser("check")
    index_check.set_defaults(action="index-check")
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--kind", choices=("boundary", "file", "directory"))
    list_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    get = sub.add_parser("get")
    get.add_argument("path")
    get.add_argument("--range")
    sub.add_parser("stats")
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
