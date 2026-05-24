from __future__ import annotations

from pathlib import Path
from typing import Any

from fourdt_wiki.cli import SECTION_KEYS, find_page, section_body, wiki_pages

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
                    text=body,
                    content_hash=sha256_text(body.strip()),
                    metadata={"pageKind": page.frontmatter.get("kind", ""), "status": page.frontmatter.get("status", "")},
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
