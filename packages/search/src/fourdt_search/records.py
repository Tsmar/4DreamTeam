from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9а-яё_-]+", re.IGNORECASE)


@dataclass
class SearchChunk:
    id: str
    domain: str
    kind: str
    authority: str
    text: str
    title: str = ""
    path: str = ""
    source_id: str = ""
    page_id: str = ""
    item_id: str = ""
    line_start: int | None = None
    line_end: int | None = None
    section: str = ""
    entry_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchChunk":
        return cls(**data)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_chunk_id(
    *,
    domain: str,
    authority: str,
    locator: str,
    content: str,
) -> str:
    digest = sha256_text(f"{domain}\0{authority}\0{locator}\0{sha256_text(content)}")
    return f"{domain}-{digest[:24]}"


def result_payload(chunk: SearchChunk, score: float | None = None, *, include_text: bool = False, query: str = "") -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": chunk.id,
        "domain": chunk.domain,
        "kind": chunk.kind,
        "authority": chunk.authority,
        "score": score,
        "snippet": snippet(chunk.text, query=query),
        "locator": locator_payload(chunk),
        "getCommand": get_command(chunk),
        "freshness": {"contentHash": chunk.content_hash},
    }
    if chunk.path:
        payload["path"] = chunk.path
    if chunk.source_id:
        payload["sourceId"] = chunk.source_id
    if chunk.page_id:
        payload["pageId"] = chunk.page_id
    if chunk.item_id:
        payload["itemId"] = chunk.item_id
    if chunk.line_start is not None:
        payload["lineStart"] = chunk.line_start
    if chunk.line_end is not None:
        payload["lineEnd"] = chunk.line_end
    if chunk.section:
        payload["section"] = chunk.section
    if chunk.entry_id:
        payload["entryId"] = chunk.entry_id
    if chunk.title:
        payload["title"] = chunk.title
    if chunk.metadata:
        payload["metadata"] = chunk.metadata
    if include_text:
        payload["content"] = chunk.text
    return payload


def locator_payload(chunk: SearchChunk) -> dict[str, Any]:
    locator: dict[str, Any] = {"domain": chunk.domain}
    if chunk.path:
        locator["path"] = chunk.path
    if chunk.source_id:
        locator["sourceId"] = chunk.source_id
    if chunk.page_id:
        locator["pageId"] = chunk.page_id
    if chunk.item_id:
        locator["itemId"] = chunk.item_id
    if chunk.line_start is not None:
        locator["lineStart"] = chunk.line_start
    if chunk.line_end is not None:
        locator["lineEnd"] = chunk.line_end
    if chunk.section:
        locator["section"] = chunk.section
    if chunk.entry_id:
        locator["entryId"] = chunk.entry_id
    return locator


def get_command(chunk: SearchChunk) -> str:
    if chunk.domain == "wiki":
        target = chunk.page_id or chunk.path
        command = f"4dt-wiki --workspace . --json get {target}"
        if chunk.section:
            command += f" --section {chunk.section}"
        return command
    if chunk.domain == "sources":
        command = f"4dt-sources --workspace . --json get {chunk.path}"
        if chunk.line_start is not None and chunk.line_end is not None:
            command += f" --range {chunk.line_start}:{chunk.line_end}"
        return command
    if chunk.domain == "memory":
        return f"4dt-memory get {chunk.item_id or chunk.id} --workspace . --json"
    if chunk.domain == "board":
        return f"4dt-board --workspace . --json task show {chunk.item_id}"
    return ""


def snippet(value: str, *, limit: int = 240, query: str = "") -> str:
    text = " ".join(value.strip().split())
    if len(text) <= limit:
        return text
    query_tokens = [token.lower() for token in TOKEN_RE.findall(query) if len(token) > 2]
    start = 0
    lowered = text.lower()
    for token in sorted(query_tokens, key=len, reverse=True):
        index = lowered.find(token)
        if index >= 0:
            start = max(0, index - limit // 3)
            while start > 0 and not text[start - 1].isspace():
                start += 1
                if start >= index:
                    start = max(0, index - limit // 3)
                    break
            break
    end = min(len(text), start + limit)
    if end == len(text):
        start = max(0, end - limit)
    excerpt = text[start:end].strip()
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt.rstrip() + "..."
    return excerpt
