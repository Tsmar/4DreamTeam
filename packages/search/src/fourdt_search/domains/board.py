from __future__ import annotations

from pathlib import Path
from typing import Any

from fourdt_board.cli import SECTION_KEYS, board_files, parse_comments, require_item, section_body

from ..records import SearchChunk, sha256_text, stable_chunk_id

INDEX_SECTIONS = ("product_baseline", "scope", "acceptance_criteria", "constraints", "assumptions")


def collect(workspace: Path) -> list[SearchChunk]:
    chunks: list[SearchChunk] = []
    for item in board_files(workspace):
        item_id = item.frontmatter.get("id", "")
        title = item.frontmatter.get("title", item_id)
        meta_text = "\n".join(f"{key}: {value}" for key, value in sorted(item.frontmatter.items()))
        if meta_text.strip():
            chunks.append(_chunk(item_id, title, item.relpath, "board_metadata", "frontmatter", meta_text, item.frontmatter))
        for section_key in INDEX_SECTIONS:
            try:
                body = section_body(item.body, section_key)
            except Exception:
                continue
            if body.strip() and body.strip() != "TBD":
                chunks.append(_chunk(item_id, title, item.relpath, "board_section", section_key, body, item.frontmatter))
        for comment in parse_comments(item):
            entry_id = comment.get("metadata", {}).get("entry_id", "")
            body = "\n\n".join([comment.get("summary", ""), comment.get("body", "")]).strip()
            if not body:
                continue
            chunks.append(
                _chunk(
                    item_id,
                    title,
                    item.relpath,
                    "board_timeline",
                    "timeline",
                    body,
                    item.frontmatter,
                    entry_id=entry_id,
                    extra={"timelineType": comment.get("metadata", {}).get("type", ""), "role": comment.get("metadata", {}).get("role", "")},
                )
            )
    return chunks


def _chunk(
    item_id: str,
    title: str,
    relpath: str,
    kind: str,
    section: str,
    body: str,
    frontmatter: dict[str, str],
    *,
    entry_id: str = "",
    extra: dict[str, Any] | None = None,
) -> SearchChunk:
    locator = f"{item_id}:{kind}:{section}:{entry_id}"
    metadata = {
        "boardColumn": frontmatter.get("board_column", ""),
        "status": frontmatter.get("status", ""),
        "itemKind": frontmatter.get("kind", ""),
        **(extra or {}),
    }
    return SearchChunk(
        id=stable_chunk_id(domain="board", authority=item_id, locator=locator, content=body),
        domain="board",
        kind=kind,
        authority="4dt-board",
        item_id=item_id,
        path=relpath,
        title=title,
        section=section,
        entry_id=entry_id,
        text=body,
        content_hash=sha256_text(body.strip()),
        metadata=metadata,
    )


def read(workspace: Path, chunk: SearchChunk) -> dict[str, Any]:
    item = require_item(workspace, chunk.item_id)
    content = ""
    if chunk.kind == "board_metadata":
        content = "\n".join(f"{key}: {value}" for key, value in sorted(item.frontmatter.items()))
    elif chunk.kind == "board_section":
        content = section_body(item.body, chunk.section)
    elif chunk.kind == "board_timeline":
        for comment in parse_comments(item):
            if comment.get("metadata", {}).get("entry_id", "") == chunk.entry_id:
                content = "\n\n".join([comment.get("summary", ""), comment.get("body", "")]).strip()
                break
    if not content:
        raise RuntimeError("not_found")
    if sha256_text(content.strip()) != chunk.content_hash:
        raise RuntimeError("stale_result")
    return {
        "item": {
            "id": item.frontmatter.get("id", ""),
            "path": item.relpath,
            "title": item.frontmatter.get("title", ""),
        },
        "section": chunk.section,
        "entryId": chunk.entry_id,
        "content": content,
    }
