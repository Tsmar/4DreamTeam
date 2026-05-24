from __future__ import annotations

from pathlib import Path
from typing import Any

from fourdt_sources.cli import get_path, load_index

from ..chunking import line_chunks
from ..records import SearchChunk, sha256_text, stable_chunk_id

TEXT_EXTENSIONS = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
MAX_INDEX_BYTES = 200_000


def collect(workspace: Path) -> list[SearchChunk]:
    chunks: list[SearchChunk] = []
    for entry in load_index(workspace).get("entries", []):
        if entry.get("kind") != "file" or entry.get("status") != "active":
            continue
        path = Path(str(entry.get("path", "")))
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(text.encode("utf-8", errors="ignore")) > MAX_INDEX_BYTES:
            text = text[:MAX_INDEX_BYTES]
        title = str(entry.get("relative_path") or path.name)
        for start, end, body in line_chunks(text):
            locator = f"{path.as_posix()}:{start}:{end}"
            content_hash = sha256_text(body)
            chunks.append(
                SearchChunk(
                    id=stable_chunk_id(
                        domain="sources",
                        authority=str(entry.get("source_id", "")),
                        locator=locator,
                        content=body,
                    ),
                    domain="sources",
                    kind="file_chunk",
                    authority="4dt-sources",
                    source_id=str(entry.get("source_id", "")),
                    path=path.as_posix(),
                    title=title,
                    line_start=start,
                    line_end=end,
                    text=body,
                    content_hash=content_hash,
                    metadata={"relativePath": entry.get("relative_path", ""), "mtime": entry.get("mtime")},
                )
            )
    return chunks


def read(workspace: Path, chunk: SearchChunk) -> dict[str, Any]:
    if chunk.line_start is None or chunk.line_end is None:
        raise ValueError("source chunk is missing line range")
    file_payload = get_path(workspace, chunk.path, f"{chunk.line_start}:{chunk.line_end}")
    content = str(file_payload.get("content", ""))
    if sha256_text(content.strip()) != chunk.content_hash:
        raise RuntimeError("stale_result")
    return {
        "path": file_payload.get("path", chunk.path),
        "sourceId": file_payload.get("source_id", chunk.source_id),
        "range": file_payload.get("range"),
        "content": content,
    }
