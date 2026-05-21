#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


INDEX_VERSION = 1
SOURCE_INDEX_VERSION = 1
SOURCE_IGNORE_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "out",
    "coverage",
    ".cache",
    ".next",
    ".nuxt",
    ".vite",
    ".turbo",
    ".vercel",
    ".DS_Store",
    "vendor",
    "target",
    ".gradle",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
SOURCE_IGNORE_SUFFIXES = (
    ".log",
    ".tmp",
    ".bak",
    ".pem",
    ".key",
    ".p12",
    ".sqlite",
    ".db",
    ".dump",
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".7z",
    ".rar",
)
SOURCE_FORBIDDEN_NAMES = {
    ".env",
}
SOURCE_FORBIDDEN_PREFIXES = (
    ".env.",
)


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def kebab(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def camel_meta_key(value: str) -> str:
    return re.sub(r"_([a-z])", lambda match: match.group(1).upper(), value)


def parse_meta(raw: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.match(r"^\s*([a-zA-Z0-9_-]+)\s*:\s*(.*?)\s*$", line)
        if match:
            meta[camel_meta_key(match.group(1))] = match.group(2)
    return meta


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in next(csv.reader([value])) if part.strip()]


def section(body: str, label: str) -> str:
    lines = body.splitlines()
    start = -1
    for index, line in enumerate(lines):
        if line.strip() == f"{label}:":
            start = index
            break
    if start == -1:
        return ""

    out: list[str] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if re.match(r"^#{2,6}\s+", line):
            break
        if re.match(r"^[A-Z][A-Za-z ]+:\s*$", stripped):
            break
        if re.match(r"^<!--\s*source-", stripped):
            break
        out.append(line)
    return "\n".join(out).strip()


def parse_bullets(raw: str) -> list[str]:
    values: list[str] = []
    for line in raw.splitlines():
        match = re.match(r"^\s*-\s+(.*?)\s*$", line)
        if match:
            values.append(match.group(1))
    return values


def parse_file_refs(raw: str) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for line in parse_bullets(raw):
        match = re.match(r"^`([^`]+)`\s*(?:[-–—]\s*(.*))?$", line)
        if match:
            refs.append({"path": match.group(1), "description": (match.group(2) or "").strip()})
        else:
            refs.append({"path": line, "description": ""})
    return refs


def first_paragraph(raw: str) -> str:
    for part in re.split(r"\n\s*\n", raw):
        part = part.strip()
        if part:
            return part
    return ""


def parse_source_map(project_path: Path) -> dict[str, Any]:
    source_map_file = project_path / "source-map.md"
    if not source_map_file.exists():
        raise RuntimeError(f"Missing source map: {source_map_file}")

    markdown = source_map_file.read_text(encoding="utf-8")
    blocks = list(re.finditer(r"<!--\s*(source-root|source-group)\s*([\s\S]*?)-->", markdown))
    roots: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []

    for index, match in enumerate(blocks):
        kind = match.group(1)
        meta = parse_meta(match.group(2))
        body_start = match.end()
        body_end = blocks[index + 1].start() if index + 1 < len(blocks) else len(markdown)
        body = markdown[body_start:body_end]

        if kind == "source-root":
            roots.append(
                {
                    "id": meta.get("id") or kebab(meta.get("path", "source-root")),
                    "path": meta.get("path", ""),
                    "resolvedPath": meta.get("resolvedPath") or meta.get("resolved_path") or meta.get("path", ""),
                    "type": meta.get("type", "unknown"),
                    "purpose": meta.get("purpose"),
                    "writePolicy": meta.get("writePolicy"),
                    "changelogPolicy": meta.get("changelogPolicy"),
                }
            )
            continue

        title_match = re.search(r"^#{2,4}\s+(.+?)\s*$", body, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else meta.get("id", "Untitled group")
        groups.append(
            {
                "id": meta.get("id") or kebab(title),
                "area": meta.get("area", "unknown"),
                "root": meta.get("root", ""),
                "type": meta.get("type"),
                "title": title,
                "purpose": first_paragraph(section(body, "Purpose")) or meta.get("purpose", ""),
                "usedBy": split_csv(meta.get("usedBy")),
                "keywords": split_csv(meta.get("keywords")),
                "primaryQuestions": parse_bullets(section(body, "Primary Questions")),
                "primaryFiles": parse_file_refs(section(body, "Primary Files")),
                "supportingFiles": parse_file_refs(section(body, "Supporting Files")),
                "relatedWikiPages": [ref["path"] for ref in parse_file_refs(section(body, "Related Wiki Pages"))],
                "updateTriggers": parse_bullets(section(body, "Update Triggers")),
                "notes": parse_bullets(section(body, "Notes")),
            }
        )

    return {
        "project": project_path.name,
        "indexVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "sourceMapPath": os.path.relpath(source_map_file, Path.cwd()),
        "sourceMapSha256": sha256(markdown),
        "roots": roots,
        "groups": groups,
    }


def iso_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def index_dir(project_path: Path) -> Path:
    return project_path / ".index"


def source_index_dir(project_path: Path) -> Path:
    return index_dir(project_path) / "sources"


def write_json(file: Path, value: Any) -> None:
    file.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(project_path: Path) -> int:
    index = parse_source_map(project_path)
    directory = index_dir(project_path)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = {
        "project": index["project"],
        "indexVersion": index["indexVersion"],
        "generatedAt": index["generatedAt"],
        "sourceMapPath": index["sourceMapPath"],
        "sourceMapSha256": index["sourceMapSha256"],
        "groupCount": len(index["groups"]),
    }
    write_json(directory / "source-map.json", index)
    write_json(directory / "manifest.json", manifest)
    print(f"Built index for {index['project']}: {len(index['groups'])} groups")
    return 0


def source_path_id(path: Path) -> str:
    value = kebab(str(path))
    return value or "source"


def source_entry_status(path: Path) -> tuple[str, str]:
    name = path.name
    lower_name = name.lower()
    if name in SOURCE_FORBIDDEN_NAMES or any(name.startswith(prefix) for prefix in SOURCE_FORBIDDEN_PREFIXES):
        return ("forbidden", "forbidden-name")
    if name in SOURCE_IGNORE_NAMES or lower_name.endswith(SOURCE_IGNORE_SUFFIXES):
        return ("ignored", "ignore-list")
    return ("active", "")


def source_entry_type(path: Path) -> str:
    try:
        if path.is_symlink():
            return "symlink"
        if path.is_dir():
            return "directory"
        if path.is_file():
            return "file"
        return "unknown"
    except OSError:
        return "unknown"


def source_fingerprint(entry: dict[str, Any]) -> str:
    parts = [
        entry.get("path", ""),
        entry.get("resolvedPath", ""),
        entry.get("type", ""),
        entry.get("status", ""),
        str(entry.get("size", "")),
        str(entry.get("mtime", "")),
    ]
    return sha256("\n".join(parts))


def stat_source_entry(path: Path, root: Path) -> dict[str, Any]:
    path_type = "missing"
    status = "missing"
    reason = "path-missing"
    size: int | None = None
    mtime: float | None = None
    resolved_path = ""

    try:
        exists = path.exists() or path.is_symlink()
        if exists:
            path_type = source_entry_type(path)
            status, reason = source_entry_status(path)
            stat_value = path.lstat() if path.is_symlink() else path.stat()
            size = stat_value.st_size
            mtime = stat_value.st_mtime
            if path.is_symlink():
                resolved_path = str(path.resolve(strict=False))
    except OSError as error:
        status = "forbidden"
        reason = f"stat-error:{error.__class__.__name__}"

    entry = {
        "path": str(path),
        "relativePath": "." if path == root else os.path.relpath(path, root),
        "resolvedPath": resolved_path,
        "type": path_type,
        "status": status,
        "reason": reason,
        "size": size,
        "mtime": mtime,
    }
    entry["fingerprint"] = source_fingerprint(entry)
    return entry


def walk_source_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def visit(path: Path) -> None:
        entry = stat_source_entry(path, root)
        entries.append(entry)
        if entry["status"] != "active" or entry["type"] != "directory":
            return
        try:
            children = sorted(path.iterdir(), key=lambda child: child.name.lower())
        except OSError as error:
            error_entry = {
                "path": str(path),
                "relativePath": entry["relativePath"],
                "resolvedPath": "",
                "type": "directory",
                "status": "forbidden",
                "reason": f"list-error:{error.__class__.__name__}",
                "size": entry.get("size"),
                "mtime": entry.get("mtime"),
            }
            error_entry["fingerprint"] = source_fingerprint(error_entry)
            entries.append(error_entry)
            return
        for child in children:
            visit(child)

    visit(root)
    return entries


def build_source_inventory(project_path: Path, source_paths: list[Path]) -> int:
    if not source_paths:
        raise RuntimeError("sources build requires at least one source path")

    directory = source_index_dir(project_path)
    directory.mkdir(parents=True, exist_ok=True)

    sources: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for source_path in source_paths:
        source_id = source_path_id(source_path)
        if source_id in used_ids:
            suffix = 2
            while f"{source_id}-{suffix}" in used_ids:
                suffix += 1
            source_id = f"{source_id}-{suffix}"
        used_ids.add(source_id)

        entries = walk_source_entries(source_path)
        inventory = {
            "project": project_path.name,
            "sourceIndexVersion": SOURCE_INDEX_VERSION,
            "generatedAt": iso_now(),
            "sourceId": source_id,
            "sourcePath": str(source_path),
            "resolvedPath": str(source_path.resolve(strict=False)),
            "entryCount": len(entries),
            "entries": entries,
        }
        inventory_file = directory / f"{source_id}.json"
        write_json(inventory_file, inventory)
        sources.append(
            {
                "id": source_id,
                "path": str(source_path),
                "resolvedPath": inventory["resolvedPath"],
                "entryCount": len(entries),
                "inventoryPath": os.path.relpath(inventory_file, project_path),
            }
        )

    manifest = {
        "project": project_path.name,
        "sourceIndexVersion": SOURCE_INDEX_VERSION,
        "generatedAt": iso_now(),
        "sourceCount": len(sources),
        "sources": sources,
    }
    write_json(directory / "manifest.json", manifest)
    print(f"Built source inventory for {project_path.name}: {len(sources)} sources")
    return 0


def read_index(project_path: Path) -> dict[str, Any]:
    file = index_dir(project_path) / "source-map.json"
    if not file.exists():
        raise RuntimeError(f"Missing index: {file}")
    return json.loads(file.read_text(encoding="utf-8"))


def read_source_manifest(project_path: Path) -> dict[str, Any]:
    file = source_index_dir(project_path) / "manifest.json"
    if not file.exists():
        raise RuntimeError(f"Missing source inventory manifest: {file}")
    return json.loads(file.read_text(encoding="utf-8"))


def print_check(errors: list[str], warnings: list[str]) -> int:
    for warning in warnings:
        print(f"WARN {warning}")
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if not errors:
        print("OK wiki index check passed")
        return 0
    return 1


def print_source_check(errors: list[str], warnings: list[str]) -> int:
    for warning in warnings:
        print(f"WARN {warning}")
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if not errors:
        print("OK source inventory check passed")
        return 0
    return 1


def check(project_path: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    source_map_file = project_path / "source-map.md"
    index_file = index_dir(project_path) / "source-map.json"
    manifest_file = index_dir(project_path) / "manifest.json"

    if not source_map_file.exists():
        errors.append(f"Missing source-map.md: {source_map_file}")
    if not index_file.exists():
        errors.append(f"Missing generated index: {index_file}")
    if not manifest_file.exists():
        warnings.append(f"Missing manifest: {manifest_file}")
    if errors:
        return print_check(errors, warnings)

    index = read_index(project_path)
    source_hash = sha256(source_map_file.read_text(encoding="utf-8"))
    if index.get("sourceMapSha256") != source_hash:
        errors.append("Stale index: source-map.md hash does not match .index/source-map.json")

    ids: set[str] = set()
    for group in index.get("groups", []):
        group_id = group.get("id", "")
        if group_id in ids:
            errors.append(f"Duplicate source group id: {group_id}")
        ids.add(group_id)
        if not group.get("root"):
            errors.append(f"Group {group_id} is missing root")
        if not group.get("area"):
            errors.append(f"Group {group_id} is missing area")
        if not group.get("purpose"):
            warnings.append(f"Group {group_id} is missing purpose")
        if not group.get("primaryFiles") and not group.get("supportingFiles"):
            warnings.append(f"Group {group_id} has no file references")

        for ref in [*group.get("primaryFiles", []), *group.get("supportingFiles", [])]:
            resolved = Path.cwd() / ref.get("path", "")
            if not resolved.exists():
                errors.append(f"Missing source file for {group_id}: {ref.get('path', '')}")

        for page in group.get("relatedWikiPages", []):
            resolved = project_path / page
            if not resolved.exists():
                errors.append(f"Missing wiki page for {group_id}: {page}")

    try:
        if index_file.stat().st_mtime < source_map_file.stat().st_mtime:
            warnings.append("Index file is older than source-map.md")
    except OSError:
        warnings.append("Could not compare source-map.md and index mtimes")

    return print_check(errors, warnings)


def check_sources(project_path: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_file = source_index_dir(project_path) / "manifest.json"

    if not manifest_file.exists():
        errors.append(f"Missing source inventory manifest: {manifest_file}")
        return print_source_check(errors, warnings)

    manifest = read_source_manifest(project_path)
    if manifest.get("sourceIndexVersion") != SOURCE_INDEX_VERSION:
        warnings.append("Source inventory version differs from current script version")

    ids: set[str] = set()
    for source in manifest.get("sources", []):
        source_id = source.get("id", "")
        if not source_id:
            errors.append("Source manifest entry is missing id")
            continue
        if source_id in ids:
            errors.append(f"Duplicate source id: {source_id}")
        ids.add(source_id)

        inventory_file = project_path / source.get("inventoryPath", "")
        if not inventory_file.exists():
            errors.append(f"Missing source inventory file for {source_id}: {inventory_file}")
            continue
        inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
        if inventory.get("sourceId") != source_id:
            errors.append(f"Source inventory id mismatch: {source_id}")
        if inventory.get("entryCount") != len(inventory.get("entries", [])):
            errors.append(f"Source inventory entry count mismatch: {source_id}")
        if not Path(source.get("path", "")).exists():
            warnings.append(f"Source path no longer exists: {source.get('path', '')}")

    return print_source_check(errors, warnings)


def tokenize(query: str) -> list[str]:
    return [token.strip().lower() for token in re.split(r"[^a-z0-9а-яё_-]+", query, flags=re.I) if token.strip()]


def score_group(group: dict[str, Any], query_tokens: list[str]) -> int:
    primary_files = " ".join(f"{item.get('path', '')} {item.get('description', '')}" for item in group.get("primaryFiles", []))
    supporting_files = " ".join(f"{item.get('path', '')} {item.get('description', '')}" for item in group.get("supportingFiles", []))
    weighted = [
        (group.get("id", ""), 8),
        (group.get("title", ""), 6),
        (group.get("area", ""), 5),
        (" ".join(group.get("keywords", [])), 5),
        (group.get("purpose", ""), 4),
        (" ".join(group.get("primaryQuestions", [])), 3),
        (primary_files, 3),
        (supporting_files, 2),
        (" ".join(group.get("relatedWikiPages", [])), 2),
        (" ".join(group.get("usedBy", [])), 2),
    ]
    score = 0
    for text, weight in weighted:
        haystack = text.lower()
        for token in query_tokens:
            if token in haystack:
                score += weight
    return score


def search(project_path: Path, query: str) -> int:
    index = read_index(project_path)
    query_tokens = tokenize(query)
    matches = [
        {"group": group, "score": score_group(group, query_tokens)}
        for group in index.get("groups", [])
    ]
    matches = [item for item in matches if item["score"] > 0]
    matches.sort(key=lambda item: item["score"], reverse=True)
    matches = matches[:8]

    if not matches:
        print(f"No matches for: {query}")
        return 0

    print(f"Top matches for: {query}\n")
    for index_number, item in enumerate(matches, start=1):
        group = item["group"]
        print(f"{index_number}. {group.get('id', '')} score={item['score']}")
        print(f"   {group.get('title', '')}")
        if group.get("purpose"):
            print(f"   Purpose: {group['purpose']}")
        if group.get("primaryFiles"):
            print("   Files:")
            for file_ref in group["primaryFiles"][:5]:
                print(f"   - {file_ref.get('path', '')}")
        if group.get("relatedWikiPages"):
            print("   Wiki:")
            for page in group["relatedWikiPages"][:5]:
                print(f"   - {page}")
        print()
    return 0


def score_source_entry(entry: dict[str, Any], query_tokens: list[str]) -> int:
    weighted = [
        (entry.get("path", ""), 8),
        (entry.get("relativePath", ""), 7),
        (entry.get("resolvedPath", ""), 5),
        (entry.get("type", ""), 4),
        (entry.get("status", ""), 4),
        (entry.get("reason", ""), 2),
    ]
    score = 0
    for text, weight in weighted:
        haystack = str(text).lower()
        for token in query_tokens:
            if token in haystack:
                score += weight
    return score


def search_sources(project_path: Path, query: str) -> int:
    manifest = read_source_manifest(project_path)
    query_tokens = tokenize(query)
    matches: list[dict[str, Any]] = []
    for source in manifest.get("sources", []):
        inventory_file = project_path / source.get("inventoryPath", "")
        if not inventory_file.exists():
            continue
        inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
        for entry in inventory.get("entries", []):
            score = score_source_entry(entry, query_tokens)
            if score > 0:
                matches.append({"sourceId": source.get("id", ""), "entry": entry, "score": score})

    matches.sort(key=lambda item: item["score"], reverse=True)
    matches = matches[:12]

    if not matches:
        print(f"No source inventory matches for: {query}")
        return 0

    print(f"Top source inventory matches for: {query}\n")
    for index_number, item in enumerate(matches, start=1):
        entry = item["entry"]
        print(f"{index_number}. {item['sourceId']} score={item['score']}")
        print(f"   {entry.get('relativePath', entry.get('path', ''))}")
        print(f"   type={entry.get('type', '')} status={entry.get('status', '')}")
        if entry.get("resolvedPath"):
            print(f"   resolved={entry['resolvedPath']}")
        if entry.get("reason"):
            print(f"   reason={entry['reason']}")
        print()
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="wiki_index.py",
        description="Build, check, and search 4DreamTeam local wiki and source inventory indexes.",
    )
    subparsers = parser.add_subparsers(dest="command")

    index_parser = subparsers.add_parser("index")
    index_subparsers = index_parser.add_subparsers(dest="index_command")
    build_parser = index_subparsers.add_parser("build")
    build_parser.add_argument("project_path")
    check_parser = index_subparsers.add_parser("check")
    check_parser.add_argument("project_path")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("project_path")
    search_parser.add_argument("query", nargs=argparse.REMAINDER)

    sources_parser = subparsers.add_parser("sources")
    sources_subparsers = sources_parser.add_subparsers(dest="sources_command")
    sources_build_parser = sources_subparsers.add_parser("build")
    sources_build_parser.add_argument("project_path")
    sources_build_parser.add_argument("source_paths", nargs="+")
    sources_check_parser = sources_subparsers.add_parser("check")
    sources_check_parser.add_argument("project_path")
    sources_search_parser = sources_subparsers.add_parser("search")
    sources_search_parser.add_argument("project_path")
    sources_search_parser.add_argument("query", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    try:
        if args.command == "index" and args.index_command == "build":
            return build(Path(args.project_path).resolve())
        if args.command == "index" and args.index_command == "check":
            return check(Path(args.project_path).resolve())
        if args.command == "search":
            query = " ".join(args.query).strip()
            if not query:
                parser.error("search requires a query")
            return search(Path(args.project_path).resolve(), query)
        if args.command == "sources" and args.sources_command == "build":
            return build_source_inventory(
                Path(args.project_path).resolve(),
                [Path(source_path).resolve() for source_path in args.source_paths],
            )
        if args.command == "sources" and args.sources_command == "check":
            return check_sources(Path(args.project_path).resolve())
        if args.command == "sources" and args.sources_command == "search":
            query = " ".join(args.query).strip()
            if not query:
                parser.error("sources search requires a query")
            return search_sources(Path(args.project_path).resolve(), query)
        parser.print_usage(sys.stderr)
        return 1
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
