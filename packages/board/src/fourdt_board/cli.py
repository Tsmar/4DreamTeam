from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
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
EPIC_STATUS_HELP = ", ".join(sorted(EPIC_STATUSES))
TASK_STATUS_HELP = ", ".join(sorted(TASK_STATUSES))
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
SCHEMA_VERSION = 1
SCHEMA_DOMAIN = "board"
TOOL_VERSION = "0.5.8"
RUNTIME_ROOT = Path(".4dt")


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


def schema_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ensure_schema_registry(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tool_schema_versions (
          domain TEXT PRIMARY KEY,
          schema_version INTEGER NOT NULL,
          schema_hash TEXT NOT NULL,
          tool_version TEXT NOT NULL DEFAULT '',
          applied_at TEXT NOT NULL
        )
        """
    )


def record_schema_version(connection: sqlite3.Connection, schema_text: str) -> None:
    ensure_schema_registry(connection)
    connection.execute(
        """
        INSERT INTO tool_schema_versions (domain, schema_version, schema_hash, tool_version, applied_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(domain) DO UPDATE SET
          schema_version = excluded.schema_version,
          schema_hash = excluded.schema_hash,
          tool_version = excluded.tool_version,
          applied_at = excluded.applied_at
        """,
        (SCHEMA_DOMAIN, SCHEMA_VERSION, schema_hash(schema_text), TOOL_VERSION, iso_now()),
    )


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
    relpath = path.relative_to(tasks_dir(workspace)).as_posix()
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
    return workspace / RUNTIME_ROOT / "board" / "tasks"


def board_dir(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "board"


def sqlite_path(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "db.sqlite3"


def connect(workspace: Path) -> sqlite3.Connection:
    (workspace / RUNTIME_ROOT).mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path(workspace))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    ensure_schema(connection)
    return connection


def ensure_schema(connection: sqlite3.Connection) -> None:
    schema_text = """
        CREATE TABLE IF NOT EXISTS board_items (
          id TEXT PRIMARY KEY,
          kind TEXT NOT NULL,
          title TEXT NOT NULL,
          epic TEXT NOT NULL DEFAULT '',
          board_column TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          filename TEXT NOT NULL,
          body TEXT NOT NULL,
          extra_frontmatter_json TEXT NOT NULL DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_board_items_column ON board_items(board_column);
        CREATE INDEX IF NOT EXISTS idx_board_items_epic ON board_items(epic);
        CREATE TABLE IF NOT EXISTS board_comments (
          entry_id TEXT PRIMARY KEY,
          item_id TEXT NOT NULL,
          role TEXT NOT NULL,
          type TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          actor TEXT NOT NULL,
          task_id TEXT NOT NULL,
          supersedes TEXT NOT NULL,
          summary TEXT NOT NULL,
          body TEXT NOT NULL,
          sequence INTEGER NOT NULL,
          FOREIGN KEY (item_id) REFERENCES board_items(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_board_comments_item ON board_comments(item_id, sequence);
        CREATE TABLE IF NOT EXISTS board_index (
          id TEXT PRIMARY KEY,
          index_json TEXT NOT NULL,
          generated_at TEXT NOT NULL
        );
        """
    connection.executescript(schema_text)
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(board_items)").fetchall()}
    if "extra_frontmatter_json" not in columns:
        connection.execute("ALTER TABLE board_items ADD COLUMN extra_frontmatter_json TEXT NOT NULL DEFAULT '{}'")
    record_schema_version(connection, schema_text)
    connection.commit()


def board_item_count(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT COUNT(*) AS count FROM board_items").fetchone()
    return int(row["count"])


def frontmatter_from_row(row: sqlite3.Row) -> dict[str, str]:
    meta = {
        "id": row["id"],
        "kind": row["kind"],
        "title": row["title"],
        "board_column": row["board_column"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    if row["kind"] == "task":
        meta["epic"] = row["epic"]
    try:
        extra = json.loads(row["extra_frontmatter_json"])
    except (KeyError, json.JSONDecodeError):
        extra = {}
    if isinstance(extra, dict):
        meta.update({str(key): str(value) for key, value in extra.items()})
    return meta


def comment_block(row: sqlite3.Row) -> str:
    meta = {
        "entry_id": row["entry_id"],
        "role": row["role"],
        "type": row["type"],
        "status": row["status"],
        "created_at": row["created_at"],
        "actor": row["actor"],
        "task_id": row["task_id"],
        "supersedes": row["supersedes"],
    }
    block = ["", f"### {row['type']}: {row['summary']}", "", "```yaml"]
    block.extend(f"{key}: {value}" for key, value in meta.items())
    block.extend(["```", "", row["body"].strip(), ""])
    return "\n".join(block)


def body_with_comments(connection: sqlite3.Connection, item_id: str, base_body: str) -> str:
    rows = connection.execute("SELECT * FROM board_comments WHERE item_id = ? ORDER BY sequence, created_at", (item_id,)).fetchall()
    body = base_body.rstrip()
    if rows:
        body += "\n" + "\n".join(comment_block(row) for row in rows)
    return body.rstrip() + "\n"


def row_to_board_file(workspace: Path, connection: sqlite3.Connection, row: sqlite3.Row) -> BoardFile:
    relpath = f"{row['board_column']}/{row['filename']}"
    body = body_with_comments(connection, row["id"], row["body"])
    meta = frontmatter_from_row(row)
    content = dump_frontmatter(meta) + body.rstrip() + "\n"
    path = tasks_dir(workspace) / relpath
    return validate_board_file(BoardFile(path, relpath, row["board_column"], content, meta, body, []))


def validate_board_file(file: BoardFile, *, has_frontmatter: bool = True) -> BoardFile:
    meta = file.frontmatter
    body = file.body
    relpath = file.relpath
    column = file.column
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
        issues.append(issue("column_mismatch", "error", relpath, "board_column must match the item's board column."))
    if kind and kind not in {"task", "epic"}:
        issues.append(issue("invalid_kind", "error", relpath, "kind must be task or epic."))
    filename = Path(relpath).name
    if kind == "epic" and not re.match(r"^EPIC-\d{4}-.+\.md$", filename):
        issues.append(issue("invalid_filename", "error", relpath, "Epic filename must be EPIC-XXXX-short-kebab-title.md."))
    if kind == "task":
        standalone = re.match(r"^TASK-\d{4}-.+\.md$", filename)
        epic_owned = re.match(r"^EPIC-\d{4}-TASK-\d{4}-.+\.md$", filename)
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
    return BoardFile(file.path, relpath, column, file.content, meta, body, issues)


def board_files(workspace: Path) -> list[BoardFile]:
    connection = connect(workspace)
    try:
        migrate_legacy_board_files(workspace, connection)
        rows = connection.execute("SELECT * FROM board_items ORDER BY board_column, filename").fetchall()
        return [row_to_board_file(workspace, connection, row) for row in rows]
    finally:
        connection.close()


def migrate_legacy_board_files(workspace: Path, connection: sqlite3.Connection) -> None:
    root = tasks_dir(workspace)
    if board_item_count(connection) > 0 or not root.exists():
        return
    for column in sorted(BOARD_COLUMNS):
        directory = root / column
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            file = read_board_file(workspace, path)
            meta = file.frontmatter
            if not meta.get("id"):
                continue
            base_body = re.split(r"^###\s+[^:\n]+:\s*.*$", file.body, maxsplit=1, flags=re.MULTILINE)[0].rstrip() + "\n"
            connection.execute(
                """
                INSERT OR REPLACE INTO board_items
                (id, kind, title, epic, board_column, status, created_at, updated_at, filename, body, extra_frontmatter_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meta.get("id", ""),
                    meta.get("kind", ""),
                    meta.get("title", ""),
                    meta.get("epic", ""),
                    meta.get("board_column", column),
                    meta.get("status", ""),
                    meta.get("created_at", iso_now()),
                    meta.get("updated_at", iso_now()),
                    path.name,
                    base_body,
                    json.dumps({key: value for key, value in meta.items() if key not in {"id", "kind", "title", "epic", "board_column", "status", "created_at", "updated_at"}}, ensure_ascii=False),
                ),
            )
            for index, comment in enumerate(parse_comments(file), start=1):
                comment_meta = comment.get("metadata", {})
                entry_id = comment_meta.get("entry_id") or f"{meta.get('id')}-entry-{index:04d}"
                connection.execute(
                    """
                    INSERT OR REPLACE INTO board_comments
                    (entry_id, item_id, role, type, status, created_at, actor, task_id, supersedes, summary, body, sequence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry_id,
                        meta.get("id", ""),
                        comment_meta.get("role", ""),
                        comment_meta.get("type", comment.get("heading_type", "")),
                        comment_meta.get("status", ""),
                        comment_meta.get("created_at", iso_now()),
                        comment_meta.get("actor", ""),
                        comment_meta.get("task_id", meta.get("id", "")),
                        comment_meta.get("supersedes", "null"),
                        comment.get("summary", ""),
                        comment.get("body", ""),
                        index,
                    ),
                )
    connection.commit()


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
        "indexStore": ".4dt/db.sqlite3:board_index",
        "numbering": {"lastEpicNumber": last_epic, "lastTaskNumber": last_task},
        "items": items,
        "issues": issues,
    }
    connection = connect(workspace)
    try:
        connection.execute(
            """
            INSERT INTO board_index (id, index_json, generated_at)
            VALUES ('default', ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              index_json = excluded.index_json,
              generated_at = excluded.generated_at
            """,
            (json.dumps(index, ensure_ascii=False, sort_keys=True), index["generatedAt"]),
        )
        connection.commit()
    finally:
        connection.close()
    return index


def load_or_build_index(workspace: Path) -> dict[str, Any]:
    connection = connect(workspace)
    try:
        row = connection.execute("SELECT index_json FROM board_index WHERE id = 'default'").fetchone()
    finally:
        connection.close()
    if row is None:
        return build_index(workspace)
    try:
        value = json.loads(row["index_json"])
    except json.JSONDecodeError:
        return build_index(workspace)
    return value if isinstance(value, dict) else build_index(workspace)


def find_item(workspace: Path, item_id: str) -> BoardFile | None:
    connection = connect(workspace)
    try:
        migrate_legacy_board_files(workspace, connection)
        row = connection.execute("SELECT * FROM board_items WHERE id = ?", (item_id,)).fetchone()
        return row_to_board_file(workspace, connection, row) if row else None
    finally:
        connection.close()


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


def validate_item_status(kind: str, status: str) -> None:
    if kind == "epic" and status not in EPIC_STATUSES:
        raise UserError("invalid_status", f"Invalid epic status: {status}. Supported statuses: {EPIC_STATUS_HELP}.")
    if kind == "task" and status not in TASK_STATUSES:
        raise UserError("invalid_status", f"Invalid task status: {status}. Supported statuses: {TASK_STATUS_HELP}.")


def update_item_row(
    connection: sqlite3.Connection,
    item_id: str,
    *,
    meta: dict[str, str] | None = None,
    body: str | None = None,
) -> None:
    row = connection.execute("SELECT * FROM board_items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        raise UserError("not_found", f"No board item found for id: {item_id}")
    current = frontmatter_from_row(row)
    if meta:
        current.update(meta)
    validate_item_status(str(current.get("kind", "")), str(current.get("status", "")))
    updated_at = current.get("updated_at") or iso_now()
    current["updated_at"] = updated_at
    filename = row["filename"]
    if "title" in current and current["title"] != row["title"]:
        filename = f"{item_id}-{kebab(current['title'])}.md"
    connection.execute(
        """
        UPDATE board_items
        SET kind = ?, title = ?, epic = ?, board_column = ?, status = ?, updated_at = ?, filename = ?, body = ?, extra_frontmatter_json = ?
        WHERE id = ?
        """,
        (
            current.get("kind", row["kind"]),
            current.get("title", row["title"]),
            current.get("epic", row["epic"]),
            current.get("board_column", row["board_column"]),
            current.get("status", row["status"]),
            updated_at,
            filename,
            body if body is not None else row["body"],
            row["extra_frontmatter_json"],
            item_id,
        ),
    )


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
    connection = connect(workspace)
    try:
        migrate_legacy_board_files(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute("SELECT 1 FROM board_items WHERE id = ?", (item_id,)).fetchone():
            raise UserError("already_exists", f"Board item already exists: {item_id}")
        connection.execute(
            """
            INSERT INTO board_items
            (id, kind, title, epic, board_column, status, created_at, updated_at, filename, body, extra_frontmatter_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                meta["kind"],
                meta["title"],
                meta.get("epic", ""),
                meta["board_column"],
                meta["status"],
                meta["created_at"],
                meta["updated_at"],
                filename,
                standard_body(title, kind),
                "{}",
            ),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    index = build_index(workspace)
    return {"item": item_from_file(require_item(workspace, item_id)), "index": index}


def move_item(workspace: Path, item_id: str, column: str, status: str | None) -> dict[str, Any]:
    if column not in BOARD_COLUMNS:
        raise UserError("invalid_column", f"Invalid board column: {column}")
    meta = {"board_column": column, "updated_at": iso_now()}
    if status:
        meta["status"] = status
    connection = connect(workspace)
    try:
        migrate_legacy_board_files(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        update_item_row(connection, item_id, meta=meta)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    index = build_index(workspace)
    return {"item": item_from_file(require_item(workspace, item_id)), "index": index}


def add_comment(args: argparse.Namespace, workspace: Path) -> dict[str, Any]:
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
    connection = connect(workspace)
    try:
        migrate_legacy_board_files(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        if not connection.execute("SELECT 1 FROM board_items WHERE id = ?", (args.id,)).fetchone():
            raise UserError("not_found", f"No board item found for id: {args.id}")
        next_sequence = connection.execute(
            "SELECT COALESCE(MAX(sequence), 0) + 1 AS next_sequence FROM board_comments WHERE item_id = ?",
            (args.id,),
        ).fetchone()["next_sequence"]
        connection.execute(
            """
            INSERT INTO board_comments
            (entry_id, item_id, role, type, status, created_at, actor, task_id, supersedes, summary, body, sequence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                args.id,
                args.role,
                args.type,
                args.status,
                meta["created_at"],
                args.actor,
                args.id,
                args.supersedes or "null",
                summary,
                body.strip(),
                next_sequence,
            ),
        )
        update_item_row(connection, args.id, meta={"updated_at": iso_now()})
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
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


def export_board_json(workspace: Path, output: str | None) -> dict[str, Any]:
    build_index(workspace)
    connection = connect(workspace)
    try:
        items = [dict(row) for row in connection.execute("SELECT * FROM board_items ORDER BY id").fetchall()]
        comments = [dict(row) for row in connection.execute("SELECT * FROM board_comments ORDER BY item_id, sequence, created_at").fetchall()]
    finally:
        connection.close()
    data = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "items": items,
        "comments": comments,
    }
    if output:
        path = Path(output).expanduser()
        if not path.is_absolute():
            path = (workspace / path).resolve(strict=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        output = path.as_posix()
    return {"format": "json", "output": output, "itemCount": len(items), "commentCount": len(comments), "data": None if output else data}


def load_board_import(path_value: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path_value).expanduser().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UserError("invalid_import", "Board import input must be a readable JSON export.") from exc
    if not isinstance(value, dict) or not isinstance(value.get("items"), list) or not isinstance(value.get("comments"), list):
        raise UserError("invalid_import", "Board import input must contain items and comments arrays.")
    return value


def import_board_json(workspace: Path, input_path: str, apply: bool) -> dict[str, Any]:
    data = load_board_import(input_path)
    items = data["items"]
    comments = data["comments"]
    if not apply:
        return {"format": "json", "apply": False, "itemCount": len(items), "commentCount": len(comments), "written": 0}
    connection = connect(workspace)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM board_comments")
        connection.execute("DELETE FROM board_items")
        for item in items:
            connection.execute(
                """
                INSERT INTO board_items
                (id, kind, title, epic, board_column, status, created_at, updated_at, filename, body, extra_frontmatter_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item["kind"],
                    item["title"],
                    item.get("epic", ""),
                    item["board_column"],
                    item["status"],
                    item["created_at"],
                    item["updated_at"],
                    item["filename"],
                    item["body"],
                    item.get("extra_frontmatter_json", "{}"),
                ),
            )
        for comment in comments:
            connection.execute(
                """
                INSERT INTO board_comments
                (entry_id, item_id, role, type, status, created_at, actor, task_id, supersedes, summary, body, sequence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    comment["entry_id"],
                    comment["item_id"],
                    comment["role"],
                    comment["type"],
                    comment["status"],
                    comment["created_at"],
                    comment["actor"],
                    comment["task_id"],
                    comment["supersedes"],
                    comment["summary"],
                    comment["body"],
                    comment["sequence"],
                ),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    build_index(workspace)
    return {"format": "json", "apply": True, "itemCount": len(items), "commentCount": len(comments), "written": len(items)}


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
        connection = connect(workspace)
        try:
            migrate_legacy_board_files(workspace, connection)
            connection.execute("BEGIN IMMEDIATE")
            update_item_row(connection, args.id, meta={"status": args.status_value, "updated_at": iso_now()})
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        build_index(workspace)
        return 0, payload(True, "ready", item=item_from_file(require_item(workspace, args.id)))
    if action == "metadata-set":
        if args.field not in CONTROLLED_METADATA:
            raise UserError("invalid_field", f"Metadata field is not controlled by 4dt-board: {args.field}")
        connection = connect(workspace)
        try:
            migrate_legacy_board_files(workspace, connection)
            connection.execute("BEGIN IMMEDIATE")
            update_item_row(connection, args.id, meta={args.field: args.value, "updated_at": iso_now()})
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        build_index(workspace)
        return 0, payload(True, "ready", item=item_from_file(require_item(workspace, args.id)))
    if action == "comment-add":
        return 0, payload(True, "ready", **add_comment(args, workspace))
    if action == "types-list":
        return 0, payload(
            True,
            "ready",
            board_columns=sorted(BOARD_COLUMNS),
            epic_statuses=sorted(EPIC_STATUSES),
            task_statuses=sorted(TASK_STATUSES),
            types=[{"type": key, "description": value} for key, value in sorted(TIMELINE_TYPES.items())],
        )
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
    if action == "export":
        return 0, payload(True, "ready", export=export_board_json(workspace, args.output))
    if action == "import":
        result = import_board_json(workspace, args.input, args.apply)
        return 0, payload(True, "imported" if args.apply else "dry_run", **{"import": result})
    raise UserError("unknown_command", f"Unknown command: {action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="4dt-board",
        description="Manage 4DreamTeam epics, tasks, board movement, sections, and timeline entries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Agent workflow:
  - Use task summary/get/comments before role work.
  - Use types list before adding a new timeline entry type.
  - Use explicit --entry-id for important or scripted comment writes.""",
    )
    parser.add_argument("--workspace", default=".", help="Workspace path. Defaults to the current directory.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output for agents.")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("scan", help="Scan board storage and rebuild the board index.")
    sub.add_parser("rebuild-index", help="Rebuild the board index from managed storage.")
    sub.add_parser("status", help="Show board readiness and issue summary.")
    sub.add_parser("validate", help="Validate board item shape, columns, and metadata.")
    sub.add_parser("repair-index", help="Repair the board index from managed storage.")
    types = sub.add_parser("types", help="List board contract values such as statuses and timeline entry types.")
    types_sub = types.add_subparsers(dest="types_action", required=True)
    types_list = types_sub.add_parser("list")
    types_list.set_defaults(action="types-list")
    next_id_parser = sub.add_parser("next-id")
    next_id_parser.add_argument("kind", choices=("epic", "task"), help="Item kind to allocate.")
    list_parser = sub.add_parser("list", help="List board items, optionally filtered by column or status.")
    list_parser.add_argument("--column", choices=sorted(BOARD_COLUMNS), help="Filter by board column.")
    list_parser.add_argument("--status", dest="status_filter", help="Filter by task or epic status.")
    get_parser = sub.add_parser("get", help="Read one task or epic with full body and parsed metadata.")
    get_parser.add_argument("id", help="Task or epic id.")
    find_parser = sub.add_parser("find", help="Find board items by text.")
    find_parser.add_argument("query", help="Plain text query.")
    by_epic = sub.add_parser("by-epic", help="List tasks for an epic.")
    by_epic.add_argument("epic_id", help="Epic id.")
    by_column = sub.add_parser("by-column", help="List items in a board column.")
    by_column.add_argument("column", choices=sorted(BOARD_COLUMNS), help="Board column.")
    create = sub.add_parser("create", help="Create managed epics or tasks.")
    create_sub = create.add_subparsers(dest="create_kind", required=True)
    create_epic = create_sub.add_parser("epic")
    create_epic.add_argument("title", help="Epic title.")
    create_epic.set_defaults(action="create-epic")
    create_task = create_sub.add_parser("task")
    create_task.add_argument("title", help="Task title.")
    create_task.add_argument("--epic", help="Parent epic id. Omit with --standalone for standalone tasks.")
    create_task.add_argument("--standalone", action="store_true", help="Create a standalone task without an epic.")
    create_task.set_defaults(action="create-task")
    move = sub.add_parser("move", help="Move an item to a board column and optionally update status.")
    move.add_argument("id", help="Task or epic id.")
    move.add_argument("column", choices=sorted(BOARD_COLUMNS), help="Target board column.")
    move.add_argument(
        "--status",
        dest="status_value",
        help=f"New status. Task statuses: {TASK_STATUS_HELP}. Epic statuses: {EPIC_STATUS_HELP}.",
    )
    set_status = sub.add_parser("set-status", help="Update only the item status.")
    set_status.add_argument("id", help="Task or epic id.")
    set_status.add_argument(
        "status_value",
        help=f"New status. Task statuses: {TASK_STATUS_HELP}. Epic statuses: {EPIC_STATUS_HELP}.",
    )
    metadata = sub.add_parser("metadata", help="Update controlled item metadata.")
    metadata_sub = metadata.add_subparsers(dest="metadata_action", required=True)
    metadata_set = metadata_sub.add_parser("set")
    metadata_set.add_argument("id", help="Task or epic id.")
    metadata_set.add_argument("field", help=f"Controlled metadata field: {', '.join(sorted(CONTROLLED_METADATA))}.")
    metadata_set.add_argument("value", help="New metadata value.")
    metadata_set.set_defaults(action="metadata-set")
    comment = sub.add_parser("comment", help="Append role-scoped task or epic timeline entries.")
    comment_sub = comment.add_subparsers(dest="comment_action", required=True)
    comment_add = comment_sub.add_parser(
        "add",
        help="Append a role-scoped timeline entry. Use --entry-id for deterministic scripted writes.",
        description="Append a role-scoped timeline entry. Use --entry-id for deterministic scripted writes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Common entry types:
  developer_implementation, quality_acceptance, wiki_update, release_packaging

Run `4dt-board types list --json` for the authoritative list.""",
    )
    comment_add.add_argument("id", help="Task or epic id.")
    comment_add.add_argument("--role", required=True, help=f"Timeline role: {', '.join(sorted(ROLES))}.")
    comment_add.add_argument("--type", required=True, help="Timeline entry type. Use types list before adding a new type.")
    comment_add.add_argument("--summary", help="Short timeline heading summary.")
    comment_add.add_argument("--body", help="Entry body. Keep role evidence here instead of standalone report files.")
    comment_add.add_argument("--status", default="completed", help="Entry status, defaults to completed.")
    comment_add.add_argument("--actor", default="codex", help="Entry actor, defaults to codex.")
    comment_add.add_argument("--entry-id", help="Stable unique id. Recommended for scripted or sequential comment writes.")
    comment_add.add_argument("--supersedes", help="Entry id superseded by this entry.")
    comment_add.set_defaults(action="comment-add")
    comments = sub.add_parser("comments", help="List or read latest timeline entries.")
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
    section = sub.add_parser("section", help="Read stable board item sections.")
    section_sub = section.add_subparsers(dest="section_action", required=True)
    section_get = section_sub.add_parser("get")
    section_get.add_argument("id")
    section_get.add_argument("section")
    section_get.set_defaults(action="section-get")
    task = sub.add_parser("task", help="Show full task details or concise task summaries.")
    task_sub = task.add_subparsers(dest="task_action", required=True)
    task_show = task_sub.add_parser("show")
    task_show.add_argument("id")
    task_show.set_defaults(action="task-show")
    task_summary = task_sub.add_parser("summary")
    task_summary.add_argument("id")
    task_summary.set_defaults(action="task-summary")
    recover = sub.add_parser("recover", help="Inspect an invalid item that needs operator-guided recovery.")
    recover.add_argument("id")
    export = sub.add_parser("export", help="Export full board state as JSON.")
    export.add_argument("--output", help="Output JSON file. If omitted, JSON is included in the response.")
    export.set_defaults(action="export")
    import_parser = sub.add_parser("import", help="Import full board JSON. Dry-run by default; add --apply to replace board state.")
    import_parser.add_argument("input", help="Board JSON export file.")
    import_parser.add_argument("--apply", action="store_true", help="Replace current board state with the import.")
    import_parser.set_defaults(action="import")
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
