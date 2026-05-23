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


BOARD_COLUMNS = {
    "backlog",
    "analytic",
    "developer",
    "quality",
    "wiki",
    "release",
    "released",
    "done",
    "rejected",
}
EPIC_STATUSES = {
    "shaping",
    "ready_for_analytic",
    "ready_for_developer",
    "in_delivery",
    "blocked",
    "done",
    "rejected",
}
TASK_STATUSES = {
    "proposed",
    "ready",
    "in_progress",
    "blocked",
    "needs_input",
    "needs_rework",
    "accepted",
    "done",
    "rejected",
}
ROLES = {"product", "analytic", "developer", "quality", "wiki", "release", "lead"}
TIMELINE_TYPES = {
    "product_decision": "Product decision or acceptance intent.",
    "product_scope": "Product scope clarification.",
    "analytic_clarification": "Analytic implementation clarification.",
    "analytic_handoff": "Analytic developer handoff.",
    "developer_implementation": "Developer implementation report.",
    "developer_rework": "Developer rework report.",
    "quality_acceptance": "Quality acceptance review.",
    "quality_rejection": "Quality rejection review.",
    "wiki_update": "Wiki/documentation update record.",
    "release_packaging": "Release packaging record.",
    "lead_routing": "Lead routing or workflow decision.",
    "lead_summary": "Lead task or epic summary.",
}
SECTION_KEYS = {
    "frontmatter": "frontmatter",
    "product_baseline": "Product Baseline",
    "scope": "Scope",
    "acceptance_criteria": "Acceptance Criteria",
    "constraints": "Constraints",
    "assumptions": "Assumptions",
    "timeline": "Timeline",
    "reports": "Reports",
}
CONTROLLED_METADATA = {"board_column", "status", "updated_at", "title"}
INDEX_VERSION = 1


@dataclass
class BoardFile:
    path: Path
    relpath: str
    column: str
    content: str
    frontmatter: dict[str, str]
    body: str
    issues: list[dict[str, str]]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def kebab(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def task_number(value: str) -> int:
    match = re.search(r"(?:EPIC|TASK)-(\d{4})", value)
    return int(match.group(1)) if match else 0


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
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body, True


def dump_frontmatter(meta: dict[str, str]) -> str:
    order = ["id", "kind", "title", "epic", "board_column", "status", "created_at", "updated_at"]
    keys = [key for key in order if key in meta] + sorted(key for key in meta if key not in order)
    lines = ["---"]
    for key in keys:
        value = meta[key]
        if value == "":
            lines.append(f"{key}:")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def read_board_file(workspace: Path, path: Path) -> BoardFile:
    content = path.read_text(encoding="utf-8")
    meta, body, has_frontmatter = parse_frontmatter(content)
    relpath = path.relative_to(workspace).as_posix()
    column = path.parent.name
    issues: list[dict[str, str]] = []
    if not has_frontmatter:
        issues.append(issue("missing_frontmatter", "error", relpath, "Add required frontmatter using 4dt-board recovery."))
    kind = meta.get("kind", "")
    required = ["id", "kind", "title", "board_column", "status", "created_at", "updated_at"]
    if kind == "task":
        required.append("epic")
    for key in required:
        if key not in meta:
            issues.append(issue("missing_field", "error", relpath, f"Missing frontmatter field: {key}."))
    if "next_owner" in meta:
        issues.append(issue("deprecated_field", "warning", relpath, "Remove next_owner; routing is workflow controlled."))
    if re.search(r"^## Board State\s*$", body, re.MULTILINE):
        issues.append(issue("deprecated_section", "warning", relpath, "Remove Board State body section from new-format files."))
    if column in BOARD_COLUMNS and meta.get("board_column") and meta.get("board_column") != column:
        issues.append(issue("column_mismatch", "error", relpath, "board_column must match the file's board column."))
    if kind and kind not in {"task", "epic"}:
        issues.append(issue("invalid_kind", "error", relpath, "kind must be task or epic."))
    if kind == "epic" and not re.match(r"^EPIC-\d{4}-.+\.md$", path.name):
        issues.append(issue("invalid_filename", "error", relpath, "Epic filename must be EPIC-XXXX-short-kebab-title.md."))
    if kind == "task":
        standalone = re.match(r"^TASK-\d{4}-.+\.md$", path.name)
        epic_owned = re.match(r"^EPIC-\d{4}-TASK-\d{4}-.+\.md$", path.name)
        if not standalone and not epic_owned:
            issues.append(
                issue(
                    "invalid_filename",
                    "error",
                    relpath,
                    "Task filename must be TASK-XXXX-title.md or EPIC-XXXX-TASK-XXXX-title.md.",
                )
            )
    status = meta.get("status", "")
    if kind == "epic" and status and status not in EPIC_STATUSES:
        issues.append(issue("invalid_status", "error", relpath, f"Invalid epic status: {status}."))
    if kind == "task" and status and status not in TASK_STATUSES:
        issues.append(issue("invalid_status", "error", relpath, f"Invalid task status: {status}."))
    return BoardFile(path, relpath, column, content, meta, body, issues)


def issue(code: str, severity: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def tasks_dir(workspace: Path) -> Path:
    return workspace / "tasks"


def index_path(workspace: Path) -> Path:
    return tasks_dir(workspace) / ".index.json"


def ensure_board_dirs(workspace: Path) -> None:
    for column in BOARD_COLUMNS:
        (tasks_dir(workspace) / column).mkdir(parents=True, exist_ok=True)


def board_files(workspace: Path) -> list[BoardFile]:
    root = tasks_dir(workspace)
    if not root.exists():
        return []
    files: list[BoardFile] = []
    for column in sorted(BOARD_COLUMNS):
        directory = root / column
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            files.append(read_board_file(workspace, path))
    return files


def item_from_file(file: BoardFile) -> dict[str, Any]:
    meta = file.frontmatter
    return {
        "id": meta.get("id", ""),
        "kind": meta.get("kind", ""),
        "title": meta.get("title", ""),
        "epic": meta.get("epic", ""),
        "board_column": meta.get("board_column", file.column),
        "status": meta.get("status", ""),
        "path": file.relpath,
        "updated_at": meta.get("updated_at", ""),
        "issue_count": len(file.issues),
    }


def build_index(workspace: Path) -> dict[str, Any]:
    ensure_board_dirs(workspace)
    files = board_files(workspace)
    items = [item_from_file(file) for file in files]
    issues = [entry for file in files for entry in file.issues]
    last_epic = 0
    last_task = 0
    for item in items:
        item_id = item["id"]
        if item_id.startswith("EPIC-"):
            last_epic = max(last_epic, task_number(item_id))
        if item_id.startswith("TASK-") or "-TASK-" in item_id:
            match = re.search(r"TASK-(\d{4})", item_id)
            if match:
                last_task = max(last_task, int(match.group(1)))
    index = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "workspace": str(workspace),
        "numbering": {"lastEpicNumber": last_epic, "lastTaskNumber": last_task},
        "items": items,
        "issues": issues,
    }
    write_json(index_path(workspace), index)
    return index


def load_or_build_index(workspace: Path) -> dict[str, Any]:
    path = index_path(workspace)
    if not path.exists():
        return build_index(workspace)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return build_index(workspace)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find_item(workspace: Path, item_id: str) -> BoardFile | None:
    for file in board_files(workspace):
        if file.frontmatter.get("id") == item_id:
            return file
    return None


def require_item(workspace: Path, item_id: str) -> BoardFile:
    file = find_item(workspace, item_id)
    if not file:
        raise UserError("not_found", f"No board item found for id: {item_id}")
    return file


class UserError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def next_id(index: dict[str, Any], kind: str) -> str:
    if kind == "epic":
        return f"EPIC-{index['numbering']['lastEpicNumber'] + 1:04d}"
    if kind == "task":
        return f"TASK-{index['numbering']['lastTaskNumber'] + 1:04d}"
    raise UserError("invalid_kind", "next-id expects epic or task.")


def update_file(file: BoardFile, meta: dict[str, str] | None = None, body: str | None = None) -> None:
    new_meta = dict(file.frontmatter)
    if meta:
        new_meta.update(meta)
    new_body = file.body if body is None else body
    file.path.write_text(dump_frontmatter(new_meta) + new_body.rstrip() + "\n", encoding="utf-8")


def section_body(body: str, section_key: str) -> str:
    if section_key not in SECTION_KEYS:
        raise UserError("invalid_section", f"Unknown section key: {section_key}")
    heading = SECTION_KEYS[section_key]
    if section_key == "frontmatter":
        return ""
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(body)
    if not match:
        raise UserError("missing_section", f"Missing section: {heading}")
    start = match.end()
    next_match = re.search(r"^## .+$", body[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(body)
    return body[start:end].strip()


def standard_body(title: str, kind: str) -> str:
    if kind == "epic":
        return (
            f"# {title}\n\n"
            "## Product Baseline\n\n"
            "TBD\n\n"
            "## Scope\n\n"
            "In:\n\n- TBD\n\nOut:\n\n- TBD\n\n"
            "## Acceptance Criteria\n\n1. TBD\n\n"
            "## Assumptions\n\n- None.\n\n"
            "## Timeline\n\n<!-- Board tooling will append structured role comments here. -->\n"
        )
    return (
        f"# {title}\n\n"
        "## Product Baseline\n\n"
        "TBD\n\n"
        "## Scope\n\n"
        "In:\n\n- TBD\n\nOut:\n\n- TBD\n\n"
        "## Acceptance Criteria\n\n1. TBD\n\n"
        "## Constraints\n\n- None.\n\n"
        "## Assumptions\n\n- None.\n\n"
        "## Timeline\n\n<!-- Board tooling will append structured role comments here. -->\n"
    )


def create_item(workspace: Path, kind: str, title: str, epic: str | None = None, standalone: bool = False) -> dict[str, Any]:
    index = build_index(workspace)
    if kind == "epic":
        item_id = next_id(index, "epic")
        filename = f"{item_id}-{kebab(title)}.md"
        status = "shaping"
        meta = {
            "id": item_id,
            "kind": "epic",
            "title": title,
            "board_column": "backlog",
            "status": status,
            "created_at": iso_now(),
            "updated_at": iso_now(),
        }
    elif kind == "task":
        task_id = next_id(index, "task")
        if not standalone and not epic:
            raise UserError("missing_epic", "Task creation requires --epic or --standalone.")
        item_id = task_id if standalone else f"{epic}-{task_id}"
        filename = f"{item_id}-{kebab(title)}.md"
        meta = {
            "id": item_id,
            "kind": "task",
            "title": title,
            "epic": "" if standalone else str(epic),
            "board_column": "backlog",
            "status": "proposed",
            "created_at": iso_now(),
            "updated_at": iso_now(),
        }
    else:
        raise UserError("invalid_kind", f"Invalid kind: {kind}")
    path = tasks_dir(workspace) / "backlog" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise UserError("already_exists", f"File already exists: {path}")
    path.write_text(dump_frontmatter(meta) + standard_body(title, kind), encoding="utf-8")
    index = build_index(workspace)
    return {"item": item_from_file(read_board_file(workspace, path)), "index": index}


def move_item(workspace: Path, item_id: str, column: str, status: str | None) -> dict[str, Any]:
    if column not in BOARD_COLUMNS:
        raise UserError("invalid_column", f"Invalid board column: {column}")
    file = require_item(workspace, item_id)
    target = tasks_dir(workspace) / column / file.path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    meta = {"board_column": column, "updated_at": iso_now()}
    if status:
        meta["status"] = status
    update_file(file, meta)
    shutil.move(str(file.path), str(target))
    index = build_index(workspace)
    return {"item": item_from_file(read_board_file(workspace, target)), "index": index}


def add_comment(args: argparse.Namespace, workspace: Path) -> dict[str, Any]:
    file = require_item(workspace, args.id)
    if args.role not in ROLES:
        raise UserError("invalid_role", f"Invalid role: {args.role}")
    if args.type not in TIMELINE_TYPES:
        raise UserError("invalid_type", f"Invalid timeline entry type: {args.type}")
    expected_prefix = f"{args.role}_"
    if not args.type.startswith(expected_prefix):
        raise UserError("type_role_mismatch", f"Timeline type {args.type} must start with {expected_prefix}.")
    entry_id = args.entry_id or f"entry-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    summary = args.summary or args.type
    body = args.body or ""
    meta = {
        "entry_id": entry_id,
        "role": args.role,
        "type": args.type,
        "status": args.status,
        "created_at": iso_now(),
        "actor": args.actor,
        "task_id": args.id,
        "supersedes": args.supersedes or "null",
    }
    block = ["", f"### {args.type}: {summary}", "", "```yaml"]
    block.extend(f"{key}: {value}" for key, value in meta.items())
    block.extend(["```", "", body.strip(), ""])
    new_body = file.body.rstrip() + "\n" + "\n".join(block)
    update_file(file, {"updated_at": iso_now()}, new_body)
    build_index(workspace)
    return {"entry": meta}


def parse_comments(file: BoardFile) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    pattern = re.compile(r"^###\s+([^:\n]+):\s*(.*?)\n\n```yaml\n([\s\S]*?)\n```\n?([\s\S]*?)(?=^###\s+|\Z)", re.MULTILINE)
    for match in pattern.finditer(file.body):
        meta: dict[str, str] = {}
        for line in match.group(3).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        comments.append({"heading_type": match.group(1), "summary": match.group(2), "metadata": meta, "body": match.group(4).strip()})
    return comments


def payload(ok: bool, status: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "status": status, **extra}


def print_result(value: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    if "message" in value:
        print(value["message"])
    elif "item" in value:
        print(f"{value['item']['id']} {value['item']['path']}")
    else:
        print(json.dumps(value, indent=2, ensure_ascii=False))


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).resolve()
    action = args.action
    if action in {"scan", "rebuild-index", "status", "validate"}:
        index = build_index(workspace)
        status = "ready" if not any(item["severity"] == "error" for item in index["issues"]) else "issues"
        return (0 if status == "ready" else 2, payload(True, status, index=index, issues=index["issues"]))
    if action == "repair-index":
        index = build_index(workspace)
        return 0, payload(True, "ready", index=index)
    if action == "next-id":
        index = load_or_build_index(workspace)
        return 0, payload(True, "ready", id=next_id(index, args.kind))
    if action == "list":
        index = load_or_build_index(workspace)
        items = index["items"]
        if args.column:
            items = [item for item in items if item["board_column"] == args.column]
        if args.status_filter:
            items = [item for item in items if item["status"] == args.status_filter]
        return 0, payload(True, "ready", items=items, issues=index["issues"])
    if action in {"get", "task-show"}:
        file = require_item(workspace, args.id)
        return 0, payload(True, "ready", item=item_from_file(file), frontmatter=file.frontmatter, body=file.body, issues=file.issues)
    if action == "find":
        index = load_or_build_index(workspace)
        query = args.query.lower()
        items = [item for item in index["items"] if query in item["id"].lower() or query in item["title"].lower()]
        return 0, payload(True, "ready", items=items, issues=index["issues"])
    if action == "by-epic":
        index = load_or_build_index(workspace)
        items = [item for item in index["items"] if item.get("epic") == args.epic_id or item["id"] == args.epic_id]
        return 0, payload(True, "ready", items=items, issues=index["issues"])
    if action == "by-column":
        index = load_or_build_index(workspace)
        items = [item for item in index["items"] if item["board_column"] == args.column]
        return 0, payload(True, "ready", items=items, issues=index["issues"])
    if action == "create-epic":
        return 0, payload(True, "ready", **create_item(workspace, "epic", args.title))
    if action == "create-task":
        return 0, payload(True, "ready", **create_item(workspace, "task", args.title, args.epic, args.standalone))
    if action == "move":
        return 0, payload(True, "ready", **move_item(workspace, args.id, args.column, args.status_value))
    if action == "set-status":
        file = require_item(workspace, args.id)
        update_file(file, {"status": args.status_value, "updated_at": iso_now()})
        build_index(workspace)
        return 0, payload(True, "ready", item=item_from_file(read_board_file(workspace, file.path)))
    if action == "metadata-set":
        if args.field not in CONTROLLED_METADATA:
            raise UserError("invalid_field", f"Metadata field is not controlled by 4dt-board: {args.field}")
        file = require_item(workspace, args.id)
        update_file(file, {args.field: args.value, "updated_at": iso_now()})
        build_index(workspace)
        return 0, payload(True, "ready", item=item_from_file(read_board_file(workspace, file.path)))
    if action == "comment-add":
        return 0, payload(True, "ready", **add_comment(args, workspace))
    if action == "types-list":
        return 0, payload(True, "ready", types=[{"type": key, "description": value} for key, value in sorted(TIMELINE_TYPES.items())])
    if action in {"comments-list", "comments-latest"}:
        file = require_item(workspace, args.id)
        comments = parse_comments(file)
        if args.role:
            comments = [entry for entry in comments if entry["metadata"].get("role") == args.role]
        if args.type_filter:
            comments = [entry for entry in comments if entry["metadata"].get("type") == args.type_filter]
        if action == "comments-latest":
            comments = comments[-1:] if comments else []
        return 0, payload(True, "ready", comments=comments)
    if action == "section-get":
        file = require_item(workspace, args.id)
        if args.section == "frontmatter":
            return 0, payload(True, "ready", section=args.section, content=file.frontmatter)
        return 0, payload(True, "ready", section=args.section, content=section_body(file.body, args.section))
    if action == "task-summary":
        file = require_item(workspace, args.id)
        comments = parse_comments(file)
        return 0, payload(True, "ready", item=item_from_file(file), latest_comments=comments[-5:], issues=file.issues)
    if action == "recover":
        file = require_item(workspace, args.id)
        return 0, payload(True, "needs_operator", item=item_from_file(file), issues=file.issues)
    raise UserError("unknown_command", f"Unknown command: {action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="4dt-board")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("scan", "rebuild-index", "status", "validate", "repair-index"):
        sub.add_parser(name)
    types = sub.add_parser("types")
    types_sub = types.add_subparsers(dest="types_action", required=True)
    types_list = types_sub.add_parser("list")
    types_list.set_defaults(action="types-list")
    next_id_parser = sub.add_parser("next-id")
    next_id_parser.add_argument("kind", choices=("epic", "task"))
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--column")
    list_parser.add_argument("--status", dest="status_filter")
    get_parser = sub.add_parser("get")
    get_parser.add_argument("id")
    find_parser = sub.add_parser("find")
    find_parser.add_argument("query")
    by_epic = sub.add_parser("by-epic")
    by_epic.add_argument("epic_id")
    by_column = sub.add_parser("by-column")
    by_column.add_argument("column")
    create = sub.add_parser("create")
    create_sub = create.add_subparsers(dest="create_kind", required=True)
    create_epic = create_sub.add_parser("epic")
    create_epic.add_argument("title")
    create_epic.set_defaults(action="create-epic")
    create_task = create_sub.add_parser("task")
    create_task.add_argument("title")
    create_task.add_argument("--epic")
    create_task.add_argument("--standalone", action="store_true")
    create_task.set_defaults(action="create-task")
    move = sub.add_parser("move")
    move.add_argument("id")
    move.add_argument("column")
    move.add_argument("--status", dest="status_value")
    set_status = sub.add_parser("set-status")
    set_status.add_argument("id")
    set_status.add_argument("status_value")
    metadata = sub.add_parser("metadata")
    metadata_sub = metadata.add_subparsers(dest="metadata_action", required=True)
    metadata_set = metadata_sub.add_parser("set")
    metadata_set.add_argument("id")
    metadata_set.add_argument("field")
    metadata_set.add_argument("value")
    metadata_set.set_defaults(action="metadata-set")
    comment = sub.add_parser("comment")
    comment_sub = comment.add_subparsers(dest="comment_action", required=True)
    comment_add = comment_sub.add_parser("add")
    comment_add.add_argument("id")
    comment_add.add_argument("--role", required=True)
    comment_add.add_argument("--type", required=True)
    comment_add.add_argument("--summary")
    comment_add.add_argument("--body")
    comment_add.add_argument("--status", default="completed")
    comment_add.add_argument("--actor", default="codex")
    comment_add.add_argument("--entry-id")
    comment_add.add_argument("--supersedes")
    comment_add.set_defaults(action="comment-add")
    comments = sub.add_parser("comments")
    comments_sub = comments.add_subparsers(dest="comments_action", required=True)
    comments_list = comments_sub.add_parser("list")
    comments_list.add_argument("id")
    comments_list.add_argument("--role")
    comments_list.add_argument("--type", dest="type_filter")
    comments_list.set_defaults(action="comments-list")
    comments_latest = comments_sub.add_parser("latest")
    comments_latest.add_argument("id")
    comments_latest.add_argument("--role")
    comments_latest.add_argument("--type", dest="type_filter")
    comments_latest.set_defaults(action="comments-latest")
    section = sub.add_parser("section")
    section_sub = section.add_subparsers(dest="section_action", required=True)
    section_get = section_sub.add_parser("get")
    section_get.add_argument("id")
    section_get.add_argument("section")
    section_get.set_defaults(action="section-get")
    task = sub.add_parser("task")
    task_sub = task.add_subparsers(dest="task_action", required=True)
    task_show = task_sub.add_parser("show")
    task_show.add_argument("id")
    task_show.set_defaults(action="task-show")
    task_summary = task_sub.add_parser("summary")
    task_summary.add_argument("id")
    task_summary.set_defaults(action="task-summary")
    recover = sub.add_parser("recover")
    recover.add_argument("id")
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
