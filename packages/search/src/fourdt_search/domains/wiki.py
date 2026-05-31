from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fourdt_wiki.cli import SECTION_KEYS, connect, find_page, fts_query_for, migrate_legacy_pages, section_body, wiki_pages

from ..records import SearchChunk, sha256_text, stable_chunk_id


def collect(workspace: Path) -> list[SearchChunk]:
    chunks: list[SearchChunk] = []
    for page in wiki_pages(workspace):
        page_id = page.frontmatter.get("id", "")
        title = page.frontmatter.get("title", page.relpath)
        for section_key in SECTION_KEYS:
            try:
                body = section_body(page, section_key)
            except Exception:
                continue
            if not body.strip():
                continue
            tags = page.tags or []
            locator = f"{page_id}:{section_key}"
            chunks.append(
                SearchChunk(
                    id=stable_chunk_id(domain="wiki", authority=page_id, locator=locator, content=body),
                    domain="wiki",
                    kind="wiki_section",
                    authority="4dt-wiki",
                    page_id=page_id,
                    path=page.relpath,
                    title=title,
                    section=section_key,
                    text=f"{' '.join(tags)}\n{body}" if tags else body,
                    content_hash=sha256_text(body.strip()),
                    metadata={"pageKind": page.frontmatter.get("kind", ""), "status": page.frontmatter.get("status", ""), "tags": tags},
                )
            )
    return chunks


def read(workspace: Path, chunk: SearchChunk) -> dict[str, Any]:
    page = find_page(workspace, chunk.page_id or chunk.path)
    content = section_body(page, chunk.section) if chunk.section else page.body
    if sha256_text(content.strip()) != chunk.content_hash:
        raise RuntimeError("stale_result")
    return {
        "page": {
            "id": page.frontmatter.get("id", ""),
            "path": page.relpath,
            "title": page.frontmatter.get("title", ""),
        },
        "section": chunk.section,
        "content": content,
    }


def fts_candidate_keys(workspace: Path, query: str, limit: int) -> set[tuple[str, str]] | None:
    fts_query = fts_query_for(query)
    if not fts_query:
        return None
    connection = connect(workspace)
    try:
        migrate_legacy_pages(workspace, connection)
        if not connection.execute("SELECT 1 FROM sqlite_master WHERE name = 'wiki_fts'").fetchone():
            return None
        rows = connection.execute(
            """
            SELECT page_id, section_key
            FROM wiki_fts
            WHERE wiki_fts MATCH ?
            LIMIT ?
            """,
            (fts_query, limit),
        ).fetchall()
        return {(row["page_id"], row["section_key"]) for row in rows}
    except sqlite3.OperationalError:
        return None
    finally:
        connection.close()
