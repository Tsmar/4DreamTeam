from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INDEX_VERSION = 1
RUNTIME_ROOT = Path(".4dt")
PAGE_STATUSES = {"draft", "actual", "accepted", "superseded", "deprecated", "unknown"}
PAGE_KINDS = {
    "overview",
    "product",
    "architecture",
    "domain",
    "flow",
    "contract",
    "schema",
    "decision",
    "devops",
    "changelog",
    "runbook",
    "source_registry",
}
SECTION_KEYS = {
    "summary": "Summary",
    "content": "Content",
    "evidence": "Evidence",
    "decisions": "Decisions",
    "open_questions": "Open Questions",
    "related": "Related",
}
REQUIRED_FRONTMATTER = {"id", "kind", "title", "status", "created_at", "updated_at", "owner", "source_refs", "task_refs"}
BASELINE_DIRS = [
    "product",
    "architecture",
    "domains",
    "flows",
    "contracts",
    "schemas",
    "decisions",
    "devops",
]


@dataclass
class WikiPage:
    path: Path
    relpath: str
    frontmatter: dict[str, str]
    body: str
    issues: list[dict[str, str]]


class UserError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def kebab(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "page"


def docs_dir(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "wiki" / "pages"


def index_path(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "wiki" / "index.json"


def parse_frontmatter(content: str) -> tuple[dict[str, str], str, bool]:
    if not content.startswith("---\n"):
        return {}, content, False
    end = content.find("\n---", 4)
    if end == -1:
        return {}, content, False
    raw = content[4:end]
    body = content[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body, True


def dump_frontmatter(meta: dict[str, str]) -> str:
    order = ["id", "kind", "title", "status", "created_at", "updated_at", "owner", "source_refs", "task_refs"]
    keys = [key for key in order if key in meta] + sorted(key for key in meta if key not in order)
    lines = ["---"]
    for key in keys:
        lines.append(f"{key}: {meta[key]}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def page_id_for(relpath: str) -> str:
    if relpath.endswith(".md"):
        relpath = relpath[:-3]
    return kebab(relpath)


def issue(code: str, severity: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def section_template() -> str:
    return (
        "## Summary\n\n"
        "TBD\n\n"
        "## Content\n\n"
        "TBD\n\n"
        "## Evidence\n\n"
        "- None.\n\n"
        "## Decisions\n\n"
        "- None.\n\n"
        "## Open Questions\n\n"
        "- None.\n\n"
        "## Related\n\n"
        "- None.\n"
    )


def page_template(title: str) -> str:
    return f"# {title}\n\n" + section_template()


def meta_for(relpath: str, title: str, kind: str, status: str = "draft") -> dict[str, str]:
    now = iso_now()
    return {
        "id": page_id_for(relpath),
        "kind": kind,
        "title": title,
        "status": status,
        "created_at": now,
        "updated_at": now,
        "owner": "wiki",
        "source_refs": "[]",
        "task_refs": "[]",
    }


def init_wiki(workspace: Path) -> dict[str, Any]:
    root = docs_dir(workspace)
    root.mkdir(parents=True, exist_ok=True)
    for directory in BASELINE_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)
    pages = {
        "overview.md": ("Workspace Overview", "overview"),
        "product/overview.md": ("Product Overview", "product"),
        "architecture/overview.md": ("Architecture Overview", "architecture"),
        "changelog.md": ("Changelog", "changelog"),
    }
    created: list[str] = []
    for relpath, (title, kind) in pages.items():
        path = root / relpath
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dump_frontmatter(meta_for(relpath, title, kind, "draft")) + page_template(title), encoding="utf-8")
        created.append(relpath)
    return {"created": created, "root": "wiki"}


def read_page(workspace: Path, path: Path) -> WikiPage:
    content = path.read_text(encoding="utf-8")
    meta, body, has_frontmatter = parse_frontmatter(content)
    relpath = path.relative_to(docs_dir(workspace)).as_posix()
    issues: list[dict[str, str]] = []
    if relpath == "index.md":
        issues.append(issue("removed_registry", "error", relpath, "index.md is removed from the single-workspace wiki model."))
    if not has_frontmatter:
        issues.append(issue("missing_frontmatter", "error", relpath, "Wiki page requires frontmatter."))
    for key in sorted(REQUIRED_FRONTMATTER):
        if key not in meta:
            issues.append(issue("missing_field", "error", relpath, f"Missing frontmatter field: {key}."))
    if meta.get("status") and meta["status"] not in PAGE_STATUSES:
        issues.append(issue("invalid_status", "error", relpath, f"Invalid status: {meta['status']}."))
    if meta.get("kind") and meta["kind"] not in PAGE_KINDS:
        issues.append(issue("invalid_kind", "error", relpath, f"Invalid kind: {meta['kind']}."))
    expected_id = page_id_for(relpath)
    if meta.get("id") and meta["id"] != expected_id:
        issues.append(issue("id_mismatch", "warning", relpath, f"Expected id: {expected_id}."))
    for key, heading in SECTION_KEYS.items():
        if not re.search(rf"^## {re.escape(heading)}\s*$", body, re.MULTILINE):
            issues.append(issue("missing_section", "error", relpath, f"Missing section: {key}."))
    return WikiPage(path, relpath, meta, body, issues)


def wiki_pages(workspace: Path) -> list[WikiPage]:
    root = docs_dir(workspace)
    if not root.exists():
        return []
    pages: list[WikiPage] = []
    for path in sorted(root.rglob("*.md")):
        if "/.index/" in path.as_posix():
            continue
        if path.relative_to(root).as_posix() == "sources.md":
            continue
        pages.append(read_page(workspace, path))
    return pages


def item_from_page(page: WikiPage) -> dict[str, Any]:
    return {
        "id": page.frontmatter.get("id", ""),
        "kind": page.frontmatter.get("kind", ""),
        "title": page.frontmatter.get("title", ""),
        "status": page.frontmatter.get("status", ""),
        "path": page.relpath,
        "updated_at": page.frontmatter.get("updated_at", ""),
        "issue_count": len(page.issues),
    }


def build_index(workspace: Path) -> dict[str, Any]:
    pages = wiki_pages(workspace)
    index = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "root": "wiki",
        "pageCount": len(pages),
        "pages": [item_from_page(page) for page in pages],
        "issues": [entry for page in pages for entry in page.issues],
    }
    index_path(workspace).parent.mkdir(parents=True, exist_ok=True)
    index_path(workspace).write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index


def load_index(workspace: Path) -> dict[str, Any]:
    if not index_path(workspace).exists():
        return build_index(workspace)
    try:
        return json.loads(index_path(workspace).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return build_index(workspace)


def find_page(workspace: Path, page_or_id: str) -> WikiPage:
    normalized = page_or_id
    if normalized.startswith("docs/"):
        normalized = normalized[5:]
    if normalized.startswith("wiki/"):
        normalized = normalized[5:]
    candidate = docs_dir(workspace) / normalized
    if candidate.exists() and candidate.is_file():
        return read_page(workspace, candidate)
    for page in wiki_pages(workspace):
        if page.frontmatter.get("id") == page_or_id or page.relpath == page_or_id:
            return page
    raise UserError("not_found", f"Wiki page not found: {page_or_id}")


def section_body(page: WikiPage, section_key: str) -> str:
    if section_key not in SECTION_KEYS:
        raise UserError("invalid_section", f"Unknown section key: {section_key}")
    heading = SECTION_KEYS[section_key]
    match = re.search(rf"^## {re.escape(heading)}\s*$", page.body, re.MULTILINE)
    if not match:
        raise UserError("missing_section", f"Missing section: {section_key}")
    start = match.end()
    next_match = re.search(r"^## .+$", page.body[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(page.body)
    return page.body[start:end].strip()


def normalized_refs(raw: str | None, *, field: str) -> str | None:
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UserError("invalid_refs", f"{field} must be a JSON array of strings.") from exc
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise UserError("invalid_refs", f"{field} must be a JSON array of strings.")
    return json.dumps(value, ensure_ascii=False)


def replace_section_body(body: str, section_key: str, content: str) -> str:
    if section_key not in SECTION_KEYS:
        raise UserError("invalid_section", f"Unknown section key: {section_key}")
    heading = SECTION_KEYS[section_key]
    match = re.search(rf"^## {re.escape(heading)}\s*$", body, re.MULTILINE)
    if not match:
        raise UserError("missing_section", f"Missing section: {section_key}")
    start = match.end()
    next_match = re.search(r"^## .+$", body[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(body)
    replacement = "\n\n" + content.strip() + "\n\n"
    return body[:start] + replacement + body[end:].lstrip("\n")


def create_page(workspace: Path, relpath: str, title: str, kind: str) -> dict[str, Any]:
    if kind not in PAGE_KINDS:
        raise UserError("invalid_kind", f"Invalid page kind: {kind}")
    if relpath.startswith("docs/"):
        relpath = relpath[5:]
    if relpath.startswith("wiki/"):
        relpath = relpath[5:]
    if relpath == "index.md":
        raise UserError("removed_registry", "index.md is removed from the new wiki model.")
    if not relpath.endswith(".md"):
        relpath += ".md"
    path = docs_dir(workspace) / relpath
    if path.exists():
        raise UserError("already_exists", f"Wiki page already exists: {relpath}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_frontmatter(meta_for(relpath, title, kind)) + page_template(title), encoding="utf-8")
    index = build_index(workspace)
    return {"page": item_from_page(read_page(workspace, path)), "index": {"pageCount": index["pageCount"], "issues": index["issues"]}}


def write_page(page: WikiPage, meta: dict[str, str], body: str) -> None:
    meta["updated_at"] = iso_now()
    page.path.write_text(dump_frontmatter(meta) + body.rstrip() + "\n", encoding="utf-8")


def update_page(
    workspace: Path,
    page_or_id: str,
    status: str | None,
    source_refs: str | None,
    task_refs: str | None,
) -> dict[str, Any]:
    page = find_page(workspace, page_or_id)
    if status and status not in PAGE_STATUSES:
        raise UserError("invalid_status", f"Invalid status: {status}")
    meta = dict(page.frontmatter)
    if status:
        meta["status"] = status
    normalized_source_refs = normalized_refs(source_refs, field="source_refs")
    normalized_task_refs = normalized_refs(task_refs, field="task_refs")
    if normalized_source_refs is not None:
        meta["source_refs"] = normalized_source_refs
    if normalized_task_refs is not None:
        meta["task_refs"] = normalized_task_refs
    write_page(page, meta, page.body)
    build_index(workspace)
    return {"page": item_from_page(read_page(workspace, page.path))}


def update_page_section(workspace: Path, page_or_id: str, section_key: str, content: str) -> dict[str, Any]:
    page = find_page(workspace, page_or_id)
    body = replace_section_body(page.body, section_key, content)
    write_page(page, dict(page.frontmatter), body)
    build_index(workspace)
    updated = read_page(workspace, page.path)
    return {"page": item_from_page(updated), "section": section_key, "content": section_body(updated, section_key)}


def page_payload_refs(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise UserError("invalid_refs", f"{field} must be a JSON array of strings.")
    return json.dumps(value, ensure_ascii=False)


def apply_page_payload(workspace: Path, page_or_id: str, raw_payload: str) -> dict[str, Any]:
    try:
        value = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise UserError("invalid_payload", "Page payload must be a JSON object.") from exc
    if not isinstance(value, dict):
        raise UserError("invalid_payload", "Page payload must be a JSON object.")

    page = find_page(workspace, page_or_id)
    meta = dict(page.frontmatter)
    status = value.get("status")
    if status is not None:
        if not isinstance(status, str) or status not in PAGE_STATUSES:
            raise UserError("invalid_status", f"Invalid status: {status}.")
        meta["status"] = status
    source_refs = page_payload_refs(value.get("source_refs"), field="source_refs")
    task_refs = page_payload_refs(value.get("task_refs"), field="task_refs")
    if source_refs is not None:
        meta["source_refs"] = source_refs
    if task_refs is not None:
        meta["task_refs"] = task_refs

    body = page.body
    sections = value.get("sections", {})
    if not isinstance(sections, dict):
        raise UserError("invalid_sections", "sections must be a JSON object.")
    for section_key, content in sections.items():
        if section_key not in SECTION_KEYS:
            raise UserError("invalid_section", f"Unknown section key: {section_key}")
        if isinstance(content, list) and all(isinstance(item, str) for item in content):
            section_content = "\n".join(content)
        elif isinstance(content, str):
            section_content = content
        else:
            raise UserError("invalid_section", f"Section content must be a string or string array: {section_key}")
        body = replace_section_body(body, section_key, section_content)

    write_page(page, meta, body)
    build_index(workspace)
    return {"page": item_from_page(read_page(workspace, page.path))}


def search_pages(workspace: Path, query: str, limit: int) -> list[dict[str, Any]]:
    query_lower = query.lower()
    matches = []
    for page in wiki_pages(workspace):
        haystack = f"{page.relpath} {page.frontmatter.get('title', '')} {page.body}".lower()
        if query_lower in haystack:
            matches.append(item_from_page(page))
    return matches[:limit]


def status_payload(workspace: Path) -> dict[str, Any]:
    index = build_index(workspace)
    status = "ready" if not any(issue["severity"] == "error" for issue in index["issues"]) else "issues"
    return {"wiki": {"root": "docs", "pageCount": index["pageCount"]}, "issues": index["issues"], "status": status}


def resolve_export_target(workspace: Path, raw_target: str | None) -> Path:
    if not raw_target:
        raise UserError("target_required", "Export target is required.")
    target = Path(raw_target).expanduser()
    if not target.is_absolute():
        target = (workspace / target).resolve(strict=False)
    else:
        target = target.resolve(strict=False)
    sources_root = (workspace / "sources").resolve(strict=False)
    try:
        target.relative_to(sources_root)
    except ValueError as exc:
        raise UserError("target_not_allowed", "Export target must be inside workspace sources/.") from exc
    return target


def export_wiki_pages(workspace: Path, raw_target: str | None) -> dict[str, Any]:
    result = status_payload(workspace)
    if result["status"] != "ready":
        return {"target": raw_target or "", "exported_count": 0, "exported": [], "issues": result["issues"]}

    source_root = docs_dir(workspace)
    target_root = resolve_export_target(workspace, raw_target)
    exported: list[str] = []
    for source_path in sorted(source_root.rglob("*")):
        if not source_path.is_file():
            continue
        if source_path.suffix.lower() != ".md":
            continue
        relpath = source_path.relative_to(source_root)
        target_path = target_root / relpath
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)
        exported.append(relpath.as_posix())
    return {"target": target_root.as_posix(), "exported_count": len(exported), "exported": exported, "issues": []}


def payload(ok: bool, status: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "status": status, **extra}


def print_result(value: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    print(json.dumps(value, indent=2, ensure_ascii=False))


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).resolve()
    if args.action == "init":
        result = init_wiki(workspace)
        index = build_index(workspace)
        return 0, payload(True, "ready", **result, index={"pageCount": index["pageCount"], "issues": index["issues"]})
    if args.action in {"status", "validate"}:
        result = status_payload(workspace)
        return (0 if result["status"] == "ready" else 2), payload(True, result["status"], wiki=result["wiki"], issues=result["issues"])
    if args.action == "index-build":
        index = build_index(workspace)
        return 0, payload(True, "ready", index={"pageCount": index["pageCount"], "issues": index["issues"]})
    if args.action == "index-check":
        index = load_index(workspace)
        status = "ready" if not any(issue["severity"] == "error" for issue in index["issues"]) else "issues"
        return (0 if status == "ready" else 2), payload(True, status, issues=index["issues"])
    if args.action == "export":
        result = export_wiki_pages(workspace, args.target)
        status = "ready" if not result["issues"] else "issues"
        return (0 if status == "ready" else 2), payload(True, status, export=result)
    if args.action == "search":
        return 0, payload(True, "ready", matches=search_pages(workspace, args.query, args.limit), limit=args.limit)
    if args.action == "get":
        page = find_page(workspace, args.page)
        if args.section:
            return 0, payload(True, "ready", page=item_from_page(page), section=args.section, content=section_body(page, args.section))
        return 0, payload(True, "ready", page=item_from_page(page), frontmatter=page.frontmatter, body=page.body, issues=page.issues)
    if args.action == "page-create":
        return 0, payload(True, "ready", **create_page(workspace, args.path, args.title, args.type))
    if args.action == "page-update":
        return 0, payload(
            True,
            "ready",
            **update_page(workspace, args.page, args.status_value, args.source_refs_json, args.task_refs_json),
        )
    if args.action == "page-section-set":
        content = args.content if args.content is not None else sys.stdin.read()
        return 0, payload(True, "ready", **update_page_section(workspace, args.page, args.section, content))
    if args.action == "page-apply":
        raw_payload = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
        return 0, payload(True, "ready", **apply_page_payload(workspace, args.page, raw_payload))
    if args.action == "adr-create":
        relpath = f"decisions/{datetime.now(timezone.utc).strftime('%Y%m%d')}-{kebab(args.title)}.md"
        return 0, payload(True, "ready", **create_page(workspace, relpath, args.title, "decision"))
    raise UserError("unknown_command", f"Unknown command: {args.action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="4dt-wiki")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("validate")
    export = sub.add_parser("export")
    export.add_argument("--target")
    export.set_defaults(action="export")
    index = sub.add_parser("index")
    index_sub = index.add_subparsers(dest="index_action", required=True)
    index_build = index_sub.add_parser("build")
    index_build.set_defaults(action="index-build")
    index_check = index_sub.add_parser("check")
    index_check.set_defaults(action="index-check")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    get = sub.add_parser("get")
    get.add_argument("page")
    get.add_argument("--section", choices=sorted(SECTION_KEYS))
    page = sub.add_parser("page")
    page_sub = page.add_subparsers(dest="page_action", required=True)
    page_create = page_sub.add_parser("create")
    page_create.add_argument("path")
    page_create.add_argument("--title", required=True)
    page_create.add_argument("--type", required=True, choices=sorted(PAGE_KINDS))
    page_create.set_defaults(action="page-create")
    page_update = page_sub.add_parser("update")
    page_update.add_argument("page")
    page_update.add_argument("--status", dest="status_value", choices=sorted(PAGE_STATUSES))
    page_update.add_argument("--source-refs-json")
    page_update.add_argument("--task-refs-json")
    page_update.set_defaults(action="page-update")
    page_section_set = page_sub.add_parser("section-set")
    page_section_set.add_argument("page")
    page_section_set.add_argument("section", choices=sorted(SECTION_KEYS))
    page_section_set.add_argument("--content")
    page_section_set.set_defaults(action="page-section-set")
    page_apply = page_sub.add_parser("apply")
    page_apply.add_argument("page")
    page_apply.add_argument("--file")
    page_apply.set_defaults(action="page-apply")
    adr = sub.add_parser("adr")
    adr_sub = adr.add_subparsers(dest="adr_action", required=True)
    adr_create = adr_sub.add_parser("create")
    adr_create.add_argument("title")
    adr_create.set_defaults(action="adr-create")
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
