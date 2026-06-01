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


INDEX_VERSION = 1
SCHEMA_VERSION = 1
SCHEMA_DOMAIN = "wiki"
TOOL_VERSION = "0.5.8"
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
MAX_SECTION_BYTES = 32_000
MAX_SECTION_BYTES_LABEL = f"{MAX_SECTION_BYTES:,}"
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
    tags: list[str] | None = None


class UserError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


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
        (
            SCHEMA_DOMAIN,
            SCHEMA_VERSION,
            hashlib.sha256(schema_text.encode("utf-8")).hexdigest(),
            TOOL_VERSION,
            iso_now(),
        ),
    )


def kebab(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "page"


def docs_dir(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "wiki" / "pages"


def wiki_dir(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "wiki"


def sqlite_path(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "db.sqlite3"


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


def frontmatter_value(key: str, value: Any) -> str:
    if key in {"source_refs", "task_refs", "tags"}:
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value
            value = parsed
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = str(value)
    if not text or text[0].isspace() or text[-1:].isspace() or any(char in text for char in [":", "#", "[", "]", "{", "}"]):
        return json.dumps(text, ensure_ascii=False)
    return text


def dump_frontmatter(meta: dict[str, Any]) -> str:
    order = ["id", "kind", "title", "status", "created_at", "updated_at", "owner", "source_refs", "task_refs", "tags"]
    keys = [key for key in order if key in meta] + sorted(key for key in meta if key not in order)
    lines = ["---"]
    for key in keys:
        lines.append(f"{key}: {frontmatter_value(key, meta[key])}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def page_id_for(relpath: str) -> str:
    if relpath.endswith(".md"):
        relpath = relpath[:-3]
    return kebab(relpath)


def issue(code: str, severity: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "path": path, "message": message}


def section_template() -> str:
    return sections_to_body(default_sections())


def page_template(title: str) -> str:
    return f"# {title}\n\n" + section_template()


def default_sections() -> dict[str, str]:
    return {
        "summary": "TBD",
        "content": "TBD",
        "evidence": "- None.",
        "decisions": "- None.",
        "open_questions": "- None.",
        "related": "- None.",
    }


def page_markdown(page: WikiPage) -> str:
    frontmatter: dict[str, Any] = dict(page.frontmatter)
    if page.tags:
        frontmatter["tags"] = page.tags
    return dump_frontmatter(frontmatter) + page.body.rstrip() + "\n"


def sections_to_body(sections: dict[str, str], title: str | None = None) -> str:
    lines: list[str] = []
    if title is not None:
        lines.extend([f"# {title}", ""])
    for section_key, heading in SECTION_KEYS.items():
        lines.extend([f"## {heading}", "", sections.get(section_key, "").strip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    for section_key, heading in SECTION_KEYS.items():
        match = re.search(rf"^## {re.escape(heading)}\s*$", body, re.MULTILINE)
        if not match:
            continue
        start = match.end()
        next_match = re.search(r"^## .+$", body[start:], re.MULTILINE)
        end = start + next_match.start() if next_match else len(body)
        sections[section_key] = body[start:end].strip()
    return sections


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


def connect(workspace: Path) -> sqlite3.Connection:
    (workspace / RUNTIME_ROOT).mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path(workspace))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    ensure_schema(connection)
    return connection


def create_wiki_pages_table(connection: sqlite3.Connection, table_name: str = "wiki_pages") -> None:
    if table_name not in {"wiki_pages", "wiki_pages_new"}:
        raise ValueError(f"Unsupported wiki pages table name: {table_name}")
    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
          relpath TEXT PRIMARY KEY,
          id TEXT NOT NULL UNIQUE,
          kind TEXT NOT NULL,
          title TEXT NOT NULL,
          status TEXT NOT NULL,
          owner TEXT NOT NULL,
          source_refs_json TEXT NOT NULL,
          task_refs_json TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          extra_frontmatter_json TEXT NOT NULL DEFAULT '{{}}'
        )
        """
    )


def wiki_pages_columns(connection: sqlite3.Connection) -> set[str]:
    return {str(row["name"]) for row in connection.execute("PRAGMA table_info(wiki_pages)").fetchall()}


def migrate_frontmatter_json_pages(connection: sqlite3.Connection) -> None:
    columns = wiki_pages_columns(connection)
    if "frontmatter_json" not in columns:
        return
    rows = connection.execute(
        """
        SELECT relpath, frontmatter_json, created_at, updated_at
        FROM wiki_pages
        ORDER BY relpath
        """
    ).fetchall()
    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        create_wiki_pages_table(connection, "wiki_pages_new")
        for row in rows:
            try:
                raw_meta = json.loads(row["frontmatter_json"])
            except json.JSONDecodeError:
                raw_meta = {}
            meta = raw_meta if isinstance(raw_meta, dict) else {}
            fallback_title = Path(row["relpath"]).stem.replace("-", " ").replace("_", " ").title()
            default_meta = meta_for(row["relpath"], fallback_title, str(meta.get("kind", "overview")))
            normalized_meta = {**default_meta, **{str(key): str(value) for key, value in meta.items()}}
            normalized_meta["created_at"] = str(meta.get("created_at") or row["created_at"])
            normalized_meta["updated_at"] = str(meta.get("updated_at") or row["updated_at"])
            connection.execute(
                """
                INSERT INTO wiki_pages_new
                (relpath, id, kind, title, status, owner, source_refs_json, task_refs_json, created_at, updated_at, extra_frontmatter_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (row["relpath"], *wiki_page_values(normalized_meta)),
            )
        connection.execute("DROP TABLE wiki_pages")
        connection.execute("ALTER TABLE wiki_pages_new RENAME TO wiki_pages")
        connection.commit()
    finally:
        connection.execute("PRAGMA foreign_keys = ON")


def ensure_schema(connection: sqlite3.Connection) -> None:
    schema_text = """
    wiki_pages(relpath,id,kind,title,status,owner,source_refs_json,task_refs_json,created_at,updated_at,extra_frontmatter_json)
    wiki_sections(page_relpath,section_key,content,updated_at)
    wiki_tags(name,created_at,updated_at)
    wiki_page_tags(page_relpath,tag_name,created_at)
    wiki_index(id,index_json,generated_at)
    wiki_fts(relpath,page_id,section_key,title,tags,content)
    """
    create_wiki_pages_table(connection)
    migrate_frontmatter_json_pages(connection)
    connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_wiki_pages_id ON wiki_pages(id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_kind ON wiki_pages(kind)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_status ON wiki_pages(status)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_updated_at ON wiki_pages(updated_at)")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS wiki_sections (
          page_relpath TEXT NOT NULL,
          section_key TEXT NOT NULL,
          content TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          PRIMARY KEY (page_relpath, section_key),
          FOREIGN KEY (page_relpath) REFERENCES wiki_pages(relpath) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS wiki_tags (
          name TEXT PRIMARY KEY,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS wiki_page_tags (
          page_relpath TEXT NOT NULL,
          tag_name TEXT NOT NULL,
          created_at TEXT NOT NULL,
          PRIMARY KEY (page_relpath, tag_name),
          FOREIGN KEY (page_relpath) REFERENCES wiki_pages(relpath) ON DELETE CASCADE,
          FOREIGN KEY (tag_name) REFERENCES wiki_tags(name) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS wiki_index (
          id TEXT PRIMARY KEY,
          index_json TEXT NOT NULL,
          generated_at TEXT NOT NULL
        )
        """
    )
    try:
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
              relpath UNINDEXED,
              page_id UNINDEXED,
              section_key UNINDEXED,
              title,
              tags,
              content,
              tokenize='unicode61'
            )
            """
        )
    except sqlite3.OperationalError:
        pass
    record_schema_version(connection, schema_text)
    connection.commit()


def row_to_page(row: sqlite3.Row) -> WikiPage:
    meta = frontmatter_from_row(row)
    body = sections_to_body(json.loads(row["sections_json"]), meta.get("title", row["relpath"]))
    tags = json.loads(row["tags_json"]) if "tags_json" in row.keys() else []
    page = WikiPage(Path(row["relpath"]), row["relpath"], meta, body, [], tags)
    return validate_page_shape(page)


def read_markdown_page(workspace: Path, path: Path) -> WikiPage:
    content = path.read_text(encoding="utf-8")
    meta, body, has_frontmatter = parse_frontmatter(content)
    relpath = path.relative_to(docs_dir(workspace)).as_posix()
    page = WikiPage(path, relpath, meta, body, [])
    return validate_page_shape(page, has_frontmatter=has_frontmatter)


def validate_page_shape(page: WikiPage, *, has_frontmatter: bool = True) -> WikiPage:
    issues: list[dict[str, str]] = []
    if page.relpath == "index.md":
        issues.append(issue("removed_registry", "error", page.relpath, "index.md is removed from the single-workspace wiki model."))
    if not has_frontmatter:
        issues.append(issue("missing_frontmatter", "error", page.relpath, "Wiki page requires frontmatter."))
    for key in sorted(REQUIRED_FRONTMATTER):
        if key not in page.frontmatter:
            issues.append(issue("missing_field", "error", page.relpath, f"Missing frontmatter field: {key}."))
    if page.frontmatter.get("status") and page.frontmatter["status"] not in PAGE_STATUSES:
        issues.append(issue("invalid_status", "error", page.relpath, f"Invalid status: {page.frontmatter['status']}."))
    if page.frontmatter.get("kind") and page.frontmatter["kind"] not in PAGE_KINDS:
        issues.append(issue("invalid_kind", "error", page.relpath, f"Invalid kind: {page.frontmatter['kind']}."))
    expected_id = page_id_for(page.relpath)
    if page.frontmatter.get("id") and page.frontmatter["id"] != expected_id:
        issues.append(issue("id_mismatch", "warning", page.relpath, f"Expected id: {expected_id}."))
    for key, heading in SECTION_KEYS.items():
        if not re.search(rf"^## {re.escape(heading)}\s*$", page.body, re.MULTILINE):
            issues.append(issue("missing_section", "error", page.relpath, f"Missing section: {key}."))
    return WikiPage(page.path, page.relpath, page.frontmatter, page.body, issues, page.tags or [])


def page_count(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT COUNT(*) AS count FROM wiki_pages").fetchone()
    return int(row["count"])


def frontmatter_from_row(row: sqlite3.Row) -> dict[str, str]:
    meta = {
        "id": row["id"],
        "kind": row["kind"],
        "title": row["title"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "owner": row["owner"],
        "source_refs": row["source_refs_json"],
        "task_refs": row["task_refs_json"],
    }
    try:
        extra = json.loads(row["extra_frontmatter_json"])
    except (KeyError, json.JSONDecodeError):
        extra = {}
    if isinstance(extra, dict):
        meta.update({str(key): str(value) for key, value in extra.items()})
    return meta


WIKI_PAGE_COLUMNS = """
          p.relpath,
          p.id,
          p.kind,
          p.title,
          p.status,
          p.owner,
          p.source_refs_json,
          p.task_refs_json,
          p.created_at,
          p.updated_at,
          p.extra_frontmatter_json
"""


def wiki_page_values(meta: dict[str, str]) -> tuple[str, str, str, str, str, str, str, str, str]:
    extra = {
        key: value
        for key, value in meta.items()
        if key not in {"id", "kind", "title", "status", "created_at", "updated_at", "owner", "source_refs", "task_refs", "tags"}
    }
    return (
        meta.get("id", ""),
        meta.get("kind", ""),
        meta.get("title", ""),
        meta.get("status", ""),
        meta.get("owner", "wiki"),
        meta.get("source_refs", "[]"),
        meta.get("task_refs", "[]"),
        meta.get("created_at", ""),
        meta.get("updated_at", ""),
        json.dumps(extra, ensure_ascii=False),
    )


def save_page_row(connection: sqlite3.Connection, relpath: str, meta: dict[str, str], body: str) -> None:
    now = meta.get("updated_at") or iso_now()
    created_at = meta.get("created_at") or now
    meta = {**meta, "created_at": created_at, "updated_at": now}
    connection.execute(
        """
        INSERT INTO wiki_pages
        (relpath, id, kind, title, status, owner, source_refs_json, task_refs_json, created_at, updated_at, extra_frontmatter_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(relpath) DO UPDATE SET
          id=excluded.id,
          kind=excluded.kind,
          title=excluded.title,
          status=excluded.status,
          owner=excluded.owner,
          source_refs_json=excluded.source_refs_json,
          task_refs_json=excluded.task_refs_json,
          updated_at=excluded.updated_at,
          extra_frontmatter_json=excluded.extra_frontmatter_json
        """,
        (relpath, *wiki_page_values(meta)),
    )
    sections = split_sections(body)
    for section_key in SECTION_KEYS:
        section_content = sections.get(section_key, "")
        validate_section_size(section_key, section_content)
        connection.execute(
            """
            INSERT INTO wiki_sections (page_relpath, section_key, content, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(page_relpath, section_key) DO UPDATE SET
              content=excluded.content,
              updated_at=excluded.updated_at
            """,
            (relpath, section_key, section_content, now),
        )


def raw_tags_from_meta(meta: dict[str, str]) -> list[str]:
    raw = meta.get("tags")
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = [item.strip() for item in raw.split(",")]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return []
    return [item for item in value if item.strip()]


def migrate_legacy_pages(workspace: Path, connection: sqlite3.Connection) -> None:
    if page_count(connection) > 0 or not docs_dir(workspace).exists():
        return
    for path in sorted(docs_dir(workspace).rglob("*.md")):
        if "/.index/" in path.as_posix():
            continue
        page = read_markdown_page(workspace, path)
        save_page_row(connection, page.relpath, page.frontmatter, page.body)
        set_page_tags(connection, page.relpath, raw_tags_from_meta(page.frontmatter))
    rebuild_fts(connection)
    connection.commit()


def unmanaged_file_issues(workspace: Path, managed_relpaths: set[str]) -> list[dict[str, str]]:
    if not docs_dir(workspace).exists():
        return []
    issues: list[dict[str, str]] = []
    for path in sorted(docs_dir(workspace).rglob("*.md")):
        if "/.index/" in path.as_posix():
            continue
        relpath = path.relative_to(docs_dir(workspace)).as_posix()
        if relpath in managed_relpaths:
            continue
        issues.extend(read_markdown_page(workspace, path).issues)
        if relpath != "index.md":
            issues.append(issue("unmanaged_legacy_file", "warning", relpath, "File is not part of the SQLite-backed managed wiki."))
    return issues


def init_wiki(workspace: Path) -> dict[str, Any]:
    connection = connect(workspace)
    migrate_legacy_pages(workspace, connection)
    pages = {
        "start/overview.md": ("Overview", "overview"),
        "product/overview.md": ("Overview", "product"),
        "architecture/overview.md": ("Overview", "architecture"),
        "changelog.md": ("Changelog", "changelog"),
    }
    created: list[str] = []
    try:
        connection.execute("BEGIN IMMEDIATE")
        for relpath, (title, kind) in pages.items():
            existing = connection.execute("SELECT 1 FROM wiki_pages WHERE relpath = ?", (relpath,)).fetchone()
            if existing:
                continue
            save_page_row(connection, relpath, meta_for(relpath, title, kind, "draft"), page_template(title))
            created.append(relpath)
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"created": created, "root": "wiki", "storage": "sqlite"}


def wiki_pages(workspace: Path) -> list[WikiPage]:
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        rows = page_rows(connection)
        return [row_to_page(row) for row in rows]
    finally:
        connection.close()


def page_rows(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT
""" + WIKI_PAGE_COLUMNS + """,
          COALESCE(
            (SELECT json_group_object(section_key, content) FROM wiki_sections WHERE page_relpath = p.relpath),
            '{}'
          ) AS sections_json,
          COALESCE(
            (SELECT json_group_array(tag_name) FROM wiki_page_tags WHERE page_relpath = p.relpath ORDER BY tag_name),
            '[]'
          ) AS tags_json
        FROM wiki_pages p
        ORDER BY p.relpath
        """
    ).fetchall()


def find_page_row(connection: sqlite3.Connection, page_or_id: str) -> sqlite3.Row | None:
    normalized = page_or_id
    if normalized.startswith("docs/"):
        normalized = normalized[5:]
    if normalized.startswith("wiki/"):
        normalized = normalized[5:]
    normalized_md = normalized if normalized.endswith(".md") else normalized + ".md"
    return connection.execute(
        """
        SELECT
""" + WIKI_PAGE_COLUMNS + """,
          COALESCE(
            (SELECT json_group_object(section_key, content) FROM wiki_sections WHERE page_relpath = p.relpath),
            '{}'
          ) AS sections_json,
          COALESCE(
            (SELECT json_group_array(tag_name) FROM wiki_page_tags WHERE page_relpath = p.relpath ORDER BY tag_name),
            '[]'
          ) AS tags_json
        FROM wiki_pages p
        WHERE p.relpath = ? OR p.id = ?
        """,
        (normalized_md, page_or_id),
    ).fetchone()


def require_page_row(connection: sqlite3.Connection, page_or_id: str) -> WikiPage:
    row = find_page_row(connection, page_or_id)
    if not row:
        raise UserError("not_found", f"Wiki page not found: {page_or_id}")
    return row_to_page(row)


def item_from_page(page: WikiPage) -> dict[str, Any]:
    return {
        "id": page.frontmatter.get("id", ""),
        "kind": page.frontmatter.get("kind", ""),
        "title": page.frontmatter.get("title", ""),
        "status": page.frontmatter.get("status", ""),
        "path": page.relpath,
        "updated_at": page.frontmatter.get("updated_at", ""),
        "issue_count": len(page.issues),
        "tags": page.tags or [],
    }


def build_index(workspace: Path) -> dict[str, Any]:
    pages = wiki_pages(workspace)
    managed_relpaths = {page.relpath for page in pages}
    index = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "root": "wiki",
        "pageCount": len(pages),
        "pages": [item_from_page(page) for page in pages],
        "issues": [entry for page in pages for entry in page.issues] + unmanaged_file_issues(workspace, managed_relpaths),
        "indexStore": ".4dt/db.sqlite3:wiki_index",
    }
    connection = connect(workspace)
    try:
        connection.execute(
            """
            INSERT INTO wiki_index (id, index_json, generated_at)
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


def load_index(workspace: Path) -> dict[str, Any]:
    connection = connect(workspace)
    try:
        row = connection.execute("SELECT index_json FROM wiki_index WHERE id = 'default'").fetchone()
    finally:
        connection.close()
    if row is None:
        return build_index(workspace)
    try:
        value = json.loads(row["index_json"])
    except json.JSONDecodeError:
        return build_index(workspace)
    return value if isinstance(value, dict) else build_index(workspace)


def find_page(workspace: Path, page_or_id: str) -> WikiPage:
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        row = find_page_row(connection, page_or_id)
        if row:
            return row_to_page(row)
    finally:
        connection.close()
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
    validate_section_size(section_key, content)
    heading = SECTION_KEYS[section_key]
    match = re.search(rf"^## {re.escape(heading)}\s*$", body, re.MULTILINE)
    if not match:
        raise UserError("missing_section", f"Missing section: {section_key}")
    start = match.end()
    next_match = re.search(r"^## .+$", body[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(body)
    replacement = "\n\n" + content.strip() + "\n\n"
    return body[:start] + replacement + body[end:].lstrip("\n")


def validate_section_size(section_key: str, content: str) -> None:
    size = len(content.encode("utf-8"))
    if size > MAX_SECTION_BYTES:
        raise UserError(
            "section_too_large",
            (
                f"Section content is larger than {MAX_SECTION_BYTES_LABEL} bytes: "
                f"{section_key} ({size} bytes). Split the material across multiple wiki pages."
            ),
        )


def create_page(workspace: Path, relpath: str, title: str, kind: str, tags: list[str] | None = None) -> dict[str, Any]:
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
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute("SELECT 1 FROM wiki_pages WHERE relpath = ?", (relpath,)).fetchone():
            raise UserError("already_exists", f"Wiki page already exists: {relpath}")
        meta = meta_for(relpath, title, kind)
        save_page_row(connection, relpath, meta, page_template(title))
        set_page_tags(connection, relpath, tags or [])
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    index = build_index(workspace)
    return {"page": item_from_page(find_page(workspace, relpath)), "index": {"pageCount": index["pageCount"], "issues": index["issues"]}}


def write_page_row(connection: sqlite3.Connection, page: WikiPage, meta: dict[str, str], body: str) -> None:
    meta["updated_at"] = iso_now()
    save_page_row(connection, page.relpath, meta, body)


def update_page_meta(connection: sqlite3.Connection, page: WikiPage, meta: dict[str, str]) -> None:
    meta["updated_at"] = iso_now()
    connection.execute(
        """
        UPDATE wiki_pages
        SET id = ?,
            kind = ?,
            title = ?,
            status = ?,
            owner = ?,
            source_refs_json = ?,
            task_refs_json = ?,
            created_at = ?,
            updated_at = ?,
            extra_frontmatter_json = ?
        WHERE relpath = ?
        """,
        (*wiki_page_values(meta), page.relpath),
    )


def update_page_section_row(connection: sqlite3.Connection, page: WikiPage, section_key: str, content: str, updated_at: str) -> None:
    validate_section_size(section_key, content)
    connection.execute(
        """
        INSERT INTO wiki_sections (page_relpath, section_key, content, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(page_relpath, section_key) DO UPDATE SET
          content=excluded.content,
          updated_at=excluded.updated_at
        """,
        (page.relpath, section_key, content.strip(), updated_at),
    )


def normalize_tag(value: str) -> str:
    tag = value.strip().lower()
    tag = re.sub(r"\s+", "-", tag)
    tag = re.sub(r"[^a-z0-9а-яё._:/-]+", "-", tag)
    tag = tag.strip("-")
    if not tag:
        raise UserError("invalid_tag", "Tag must contain letters or numbers.")
    return tag


def set_page_tags(connection: sqlite3.Connection, relpath: str, raw_tags: list[str]) -> list[str]:
    tags = sorted({normalize_tag(tag) for tag in raw_tags})
    now = iso_now()
    connection.execute("DELETE FROM wiki_page_tags WHERE page_relpath = ?", (relpath,))
    for tag in tags:
        connection.execute(
            """
            INSERT INTO wiki_tags (name, created_at, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET updated_at=excluded.updated_at
            """,
            (tag, now, now),
        )
        connection.execute(
            """
            INSERT INTO wiki_page_tags (page_relpath, tag_name, created_at)
            VALUES (?, ?, ?)
            """,
            (relpath, tag, now),
        )
    return tags


def rebuild_fts(connection: sqlite3.Connection) -> None:
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'wiki_fts'").fetchone():
        return
    connection.execute("DELETE FROM wiki_fts")
    rows = connection.execute(
        """
        SELECT
          p.relpath,
          p.id,
          p.title,
          s.section_key,
          s.content,
          COALESCE(
            (SELECT json_group_array(tag_name) FROM wiki_page_tags WHERE page_relpath = p.relpath ORDER BY tag_name),
            '[]'
          ) AS tags_json
        FROM wiki_pages p
        JOIN wiki_sections s ON s.page_relpath = p.relpath
        ORDER BY p.relpath, s.section_key
        """
    ).fetchall()
    for row in rows:
        connection.execute(
            """
            INSERT INTO wiki_fts (relpath, page_id, section_key, title, tags, content)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["relpath"],
                row["id"],
                row["section_key"],
                row["title"],
                " ".join(json.loads(row["tags_json"])),
                row["content"],
            ),
        )


def fts_query_for(query: str) -> str:
    terms = re.findall(r"[\wа-яёА-ЯЁ]+", query, flags=re.UNICODE)
    return " OR ".join(f'"{term}"' for term in terms if term.strip())


def list_tags(workspace: Path) -> list[dict[str, Any]]:
    connection = connect(workspace)
    try:
        return [
            {
                "name": row["name"],
                "pageCount": row["page_count"],
                "updatedAt": row["updated_at"],
            }
            for row in connection.execute(
                """
                SELECT t.name, t.updated_at, COUNT(pt.page_relpath) AS page_count
                FROM wiki_tags t
                LEFT JOIN wiki_page_tags pt ON pt.tag_name = t.name
                GROUP BY t.name
                ORDER BY t.name
                """
            ).fetchall()
        ]
    finally:
        connection.close()


def update_page_tags(workspace: Path, page_or_id: str, action: str, raw_tags: list[str]) -> dict[str, Any]:
    tags = sorted({normalize_tag(tag) for tag in raw_tags})
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        page = require_page_row(connection, page_or_id)
        if action == "set":
            set_page_tags(connection, page.relpath, tags)
        elif action == "remove":
            for tag in tags:
                connection.execute("DELETE FROM wiki_page_tags WHERE page_relpath = ? AND tag_name = ?", (page.relpath, tag))
        else:
            current_tags = page.tags or []
            set_page_tags(connection, page.relpath, current_tags + tags)
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"page": item_from_page(find_page(workspace, page_or_id))}


def update_page(
    workspace: Path,
    page_or_id: str,
    status: str | None,
    source_refs: str | None,
    task_refs: str | None,
) -> dict[str, Any]:
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        page = require_page_row(connection, page_or_id)
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
        update_page_meta(connection, page, meta)
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    build_index(workspace)
    return {"page": item_from_page(find_page(workspace, page_or_id))}


def update_page_section(workspace: Path, page_or_id: str, section_key: str, content: str) -> dict[str, Any]:
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        page = require_page_row(connection, page_or_id)
        if section_key not in SECTION_KEYS:
            raise UserError("invalid_section", f"Unknown section key: {section_key}")
        now = iso_now()
        meta = dict(page.frontmatter)
        meta["updated_at"] = now
        update_page_meta(connection, page, meta)
        update_page_section_row(connection, page, section_key, content, now)
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    build_index(workspace)
    updated = find_page(workspace, page_or_id)
    return {"page": item_from_page(updated), "section": section_key}


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

    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        connection.execute("BEGIN IMMEDIATE")
        page = require_page_row(connection, page_or_id)
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

        raw_tags = value.get("tags")
        tag_updates: list[str] | None = None
        if raw_tags is not None:
            if not isinstance(raw_tags, list) or not all(isinstance(tag, str) for tag in raw_tags):
                raise UserError("invalid_tags", "tags must be a JSON array of strings.")
            tag_updates = raw_tags

        sections = value.get("sections", {})
        if not isinstance(sections, dict):
            raise UserError("invalid_sections", "sections must be a JSON object.")
        section_updates: dict[str, str] = {}
        for section_key, content in sections.items():
            if section_key not in SECTION_KEYS:
                raise UserError("invalid_section", f"Unknown section key: {section_key}")
            if isinstance(content, list) and all(isinstance(item, str) for item in content):
                section_content = "\n".join(content)
            elif isinstance(content, str):
                section_content = content
            else:
                raise UserError("invalid_section", f"Section content must be a string or string array: {section_key}")
            validate_section_size(section_key, section_content)
            section_updates[section_key] = section_content

        now = iso_now()
        meta["updated_at"] = now
        update_page_meta(connection, page, meta)
        for section_key, section_content in section_updates.items():
            update_page_section_row(connection, page, section_key, section_content, now)
        if tag_updates is not None:
            set_page_tags(connection, page.relpath, tag_updates)
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    build_index(workspace)
    return {"page": item_from_page(find_page(workspace, page_or_id))}


def fallback_search_pages(workspace: Path, query: str, limit: int) -> list[dict[str, Any]]:
    query_lower = query.lower()
    matches = []
    for page in wiki_pages(workspace):
        haystack = f"{page.relpath} {page.frontmatter.get('title', '')} {' '.join(page.tags or [])} {page.body}".lower()
        if query_lower in haystack:
            matches.append(item_from_page(page))
    return matches[:limit]


def search_pages(workspace: Path, query: str, limit: int) -> list[dict[str, Any]]:
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        fts_query = fts_query_for(query)
        if not fts_query:
            return []
        rows = connection.execute(
            """
            SELECT
              relpath,
              page_id,
              group_concat(DISTINCT section_key) AS sections
            FROM wiki_fts
            WHERE wiki_fts MATCH ?
            GROUP BY relpath, page_id
            ORDER BY relpath
            LIMIT ?
            """,
            (fts_query, limit),
        ).fetchall()
        matches: list[dict[str, Any]] = []
        for row in rows:
            page = require_page_row(connection, row["page_id"])
            item = item_from_page(page)
            item["match_sections"] = sorted(section for section in (row["sections"] or "").split(",") if section)
            matches.append(item)
        return matches
    except sqlite3.OperationalError:
        return fallback_search_pages(workspace, query, limit)
    finally:
        connection.close()


def status_payload(workspace: Path) -> dict[str, Any]:
    index = build_index(workspace)
    status = "ready" if not any(issue["severity"] == "error" for issue in index["issues"]) else "issues"
    return {"wiki": {"root": "wiki", "storage": "sqlite", "pageCount": index["pageCount"]}, "issues": index["issues"], "status": status}


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

    target_root = resolve_export_target(workspace, raw_target)
    exported: list[str] = []
    for page in wiki_pages(workspace):
        target_path = target_root / page.relpath
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(page_markdown(page), encoding="utf-8")
        exported.append(page.relpath)
    return {"target": target_root.as_posix(), "exported_count": len(exported), "exported": exported, "issues": []}


def export_wiki_json(workspace: Path, output: str | None) -> dict[str, Any]:
    result = status_payload(workspace)
    if result["status"] != "ready":
        return {"format": "json", "output": output, "pageCount": 0, "issues": result["issues"], "data": None}
    pages = []
    for page in wiki_pages(workspace):
        pages.append(
            {
                "relpath": page.relpath,
                "frontmatter": page.frontmatter,
                "sections": {key: section_body(page, key) for key in sorted(SECTION_KEYS)},
                "tags": page.tags,
            }
        )
    data = {"schemaVersion": INDEX_VERSION, "generatedAt": iso_now(), "pages": pages}
    resolved_output = output
    if output:
        path = Path(output).expanduser()
        if not path.is_absolute():
            path = (workspace / path).resolve(strict=False)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        resolved_output = path.as_posix()
    return {"format": "json", "output": resolved_output, "pageCount": len(pages), "issues": [], "data": None if output else data}


def load_wiki_import(path_value: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path_value).expanduser().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UserError("invalid_import", "Wiki import input must be a readable JSON export.") from exc
    if not isinstance(value, dict) or not isinstance(value.get("pages"), list):
        raise UserError("invalid_import", "Wiki import input must contain a pages array.")
    return value


def import_wiki_json(workspace: Path, input_path: str, apply: bool) -> dict[str, Any]:
    data = load_wiki_import(input_path)
    pages = data["pages"]
    if not apply:
        return {"format": "json", "apply": False, "pageCount": len(pages), "written": 0}
    connection = connect(workspace)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM wiki_page_tags")
        connection.execute("DELETE FROM wiki_tags")
        connection.execute("DELETE FROM wiki_sections")
        connection.execute("DELETE FROM wiki_pages")
        for page in pages:
            relpath = str(page.get("relpath") or "")
            frontmatter = page.get("frontmatter")
            sections = page.get("sections")
            tags = page.get("tags") or []
            if not relpath or not isinstance(frontmatter, dict) or not isinstance(sections, dict):
                raise UserError("invalid_import", "Each wiki page import row requires relpath, frontmatter, and sections.")
            body = sections_to_body({key: str(sections.get(key, "")) for key in SECTION_KEYS}, str(frontmatter.get("title", relpath)))
            save_page_row(connection, relpath, {str(key): str(value) for key, value in frontmatter.items()}, body)
            if not isinstance(tags, list):
                tags = []
            set_page_tags(connection, relpath, [str(tag) for tag in tags])
        rebuild_fts(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    build_index(workspace)
    return {"format": "json", "apply": True, "pageCount": len(pages), "written": len(pages)}


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
        result = export_wiki_json(workspace, args.output) if args.format == "json" else export_wiki_pages(workspace, args.target)
        status = "ready" if not result["issues"] else "issues"
        return (0 if status == "ready" else 2), payload(True, status, export=result)
    if args.action == "import":
        result = import_wiki_json(workspace, args.input, args.apply)
        return 0, payload(True, "imported" if args.apply else "dry_run", **{"import": result})
    if args.action == "search":
        return 0, payload(True, "ready", matches=search_pages(workspace, args.query, args.limit), limit=args.limit)
    if args.action == "tags-list":
        return 0, payload(True, "ready", tags=list_tags(workspace))
    if args.action == "get":
        page = find_page(workspace, args.page)
        if args.section:
            return 0, payload(True, "ready", page=item_from_page(page), section=args.section, content=section_body(page, args.section))
        return 0, payload(True, "ready", page=item_from_page(page), frontmatter=page.frontmatter, body=page.body, issues=page.issues)
    if args.action == "page-create":
        return 0, payload(True, "ready", **create_page(workspace, args.path, args.title, args.type, args.tags))
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
    if args.action in {"page-tags-add", "page-tags-remove", "page-tags-set"}:
        tag_action = args.action.removeprefix("page-tags-")
        return 0, payload(True, "ready", **update_page_tags(workspace, args.page, tag_action, args.tags))
    if args.action == "adr-create":
        relpath = f"decisions/{datetime.now(timezone.utc).strftime('%Y%m%d')}-{kebab(args.title)}.md"
        return 0, payload(True, "ready", **create_page(workspace, relpath, args.title, "decision", args.tags))
    raise UserError("unknown_command", f"Unknown command: {args.action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="4dt-wiki",
        description="Manage the single 4DreamTeam workspace wiki through stable page and section contracts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--workspace", default=".", help="Workspace path. Defaults to the current directory.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output for agents.")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init", help="Initialize managed wiki storage and baseline pages.")
    sub.add_parser("status", help="Show managed wiki readiness and issue summary.")
    sub.add_parser("validate", help="Validate managed wiki page shape and index health.")
    export = sub.add_parser("export", help="Render managed wiki pages to Markdown or export full wiki JSON.")
    export.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Export format. Markdown requires --target; JSON may use --output.")
    export.add_argument("--target", help="Export target under workspace sources/, for example sources/4DreamTeam/docs.")
    export.add_argument("--output", help="Output JSON file for --format json. If omitted, JSON is included in the response.")
    export.set_defaults(action="export")
    import_parser = sub.add_parser("import", help="Import full wiki JSON. Dry-run by default; add --apply to replace wiki state.")
    import_parser.add_argument("input", help="Wiki JSON export file.")
    import_parser.add_argument("--format", choices=("json",), default="json")
    import_parser.add_argument("--apply", action="store_true", help="Replace current wiki pages with the import.")
    import_parser.set_defaults(action="import")
    index = sub.add_parser("index", help="Build or check the managed wiki index.")
    index_sub = index.add_subparsers(dest="index_action", required=True)
    index_build = index_sub.add_parser("build")
    index_build.set_defaults(action="index-build")
    index_check = index_sub.add_parser("check")
    index_check.set_defaults(action="index-check")
    search = sub.add_parser("search", help="Search managed wiki pages. Prefer 4dt-search for cross-domain discovery.")
    search.add_argument("query", help="Plain text query.")
    search.add_argument("--limit", type=int, default=10, help="Maximum matches to return.")
    tags = sub.add_parser("tags", help="List managed wiki tags.")
    tags_sub = tags.add_subparsers(dest="tags_action", required=True)
    tags_list = tags_sub.add_parser("list")
    tags_list.set_defaults(action="tags-list")
    get = sub.add_parser("get", help="Read a whole page or one stable section.")
    get.add_argument("page", help="Page id or path.")
    get.add_argument("--section", choices=sorted(SECTION_KEYS), help="Read only one stable section.")
    page = sub.add_parser("page", help="Create, update, section-edit, or apply combined page changes.")
    page_sub = page.add_subparsers(dest="page_action", required=True)
    page_create = page_sub.add_parser("create", help="Create a managed wiki page with required frontmatter and sections.")
    page_create.add_argument("path", help="Workspace-wiki page path such as domains/payments.md.")
    page_create.add_argument("--title", required=True, help="Human-readable page title.")
    page_create.add_argument("--type", required=True, choices=sorted(PAGE_KINDS), help="Managed page kind.")
    page_create.add_argument("--tag", dest="tags", action="append", default=[], help="Semantic page tag. Repeat for multiple tags.")
    page_create.set_defaults(action="page-create")
    page_update = page_sub.add_parser("update", help="Update page metadata without rewriting section content.")
    page_update.add_argument("page", help="Page id or path.")
    page_update.add_argument("--status", dest="status_value", choices=sorted(PAGE_STATUSES), help="Page status.")
    page_update.add_argument("--source-refs-json", help="JSON array of source refs.")
    page_update.add_argument("--task-refs-json", help="JSON array of task refs.")
    page_update.set_defaults(action="page-update")
    page_tags = page_sub.add_parser("tags", help="Add, remove, or replace tags on one managed page.")
    page_tags_sub = page_tags.add_subparsers(dest="page_tags_action", required=True)
    page_tags_add = page_tags_sub.add_parser("add", help="Add one or more normalized tags to a page.")
    page_tags_add.add_argument("page", help="Page id or path.")
    page_tags_add.add_argument("tags", nargs="+", help="Tags to add.")
    page_tags_add.set_defaults(action="page-tags-add")
    page_tags_remove = page_tags_sub.add_parser("remove", help="Remove one or more tags from a page.")
    page_tags_remove.add_argument("page", help="Page id or path.")
    page_tags_remove.add_argument("tags", nargs="+", help="Tags to remove.")
    page_tags_remove.set_defaults(action="page-tags-remove")
    page_tags_set = page_tags_sub.add_parser("set", help="Replace page tags with the provided tag set.")
    page_tags_set.add_argument("page", help="Page id or path.")
    page_tags_set.add_argument("tags", nargs="*", help="Complete replacement tag set.")
    page_tags_set.set_defaults(action="page-tags-set")
    page_section_set = page_sub.add_parser(
        "section-set",
        help="Replace one stable section. Omit --content to read generated content from stdin.",
        epilog=(
            "Agent default: pipe generated Markdown through stdin. Use --content for short inline text. "
            f"Section content must be {MAX_SECTION_BYTES_LABEL} bytes or smaller."
        ),
    )
    page_section_set.add_argument("page", help="Page id or path.")
    page_section_set.add_argument("section", choices=sorted(SECTION_KEYS), help="Stable section key to replace.")
    page_section_set.add_argument("--content", help="Inline section content. If omitted, content is read from stdin.")
    page_section_set.set_defaults(action="page-section-set")
    page_apply = page_sub.add_parser(
        "apply",
        help="Apply metadata and multiple section updates from one JSON payload.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Agent default: omit --file and pass generated JSON on stdin.

Example:
  4dt-wiki page apply domains-payments <<'JSON'
  {"status":"accepted","sections":{"summary":"Updated summary."}}
  JSON

Use --file only when the payload already exists as a reusable or reviewed artifact.
Each section value must be 32,000 bytes or smaller.""",
    )
    page_apply.add_argument("page", help="Page id or path.")
    page_apply.add_argument("--file", help="Optional JSON payload file. If omitted, payload is read from stdin.")
    page_apply.set_defaults(action="page-apply")
    adr = sub.add_parser("adr", help="Create managed architecture decision records.")
    adr_sub = adr.add_subparsers(dest="adr_action", required=True)
    adr_create = adr_sub.add_parser("create")
    adr_create.add_argument("title")
    adr_create.add_argument("--tag", dest="tags", action="append", default=[], help="Semantic page tag. Repeat for multiple tags.")
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
