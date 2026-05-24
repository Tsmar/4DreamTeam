from __future__ import annotations

import json
from typing import Any

from fourdt_search.records import SearchChunk, sha256_text
from fourdt_search.scoring import SearchOptions, normalize_fields, rank_chunks


FIELD_ALIASES = {
    "summary": "title",
    "content": "body",
    "scope": "section",
    "type": "kind",
    "sourceType": "body",
    "sourceRef": "path",
    "tags": "body",
}


def normalize_memory_fields(raw_fields: list[str] | None) -> tuple[str, ...]:
    if not raw_fields:
        return normalize_fields(None)
    mapped: list[str] = []
    for raw in raw_fields:
        parts = [part.strip() for part in raw.split(",") if part.strip()]
        for part in parts:
            mapped.append(FIELD_ALIASES.get(part, part))
    return normalize_fields(mapped)


def memory_text(row: dict[str, Any]) -> str:
    metadata = row.get("metadata_json") or "{}"
    try:
        metadata_value = json.loads(metadata)
    except json.JSONDecodeError:
        metadata_value = {}
    metadata_text = json.dumps(metadata_value, ensure_ascii=False, sort_keys=True)
    parts = [
        row.get("summary") or "",
        row.get("content") or "",
        row.get("scope") or "",
        row.get("type") or "",
        row.get("role") or "",
        row.get("source_type") or "",
        row.get("source_ref") or "",
        metadata_text,
    ]
    return "\n".join(part for part in parts if part)


def chunk_from_memory(row: dict[str, Any]) -> SearchChunk:
    text = memory_text(row)
    metadata = {
        "scope": row.get("scope"),
        "type": row.get("type"),
        "role": row.get("role"),
        "sourceType": row.get("source_type"),
        "sourceRef": row.get("source_ref"),
        "confidence": row.get("confidence"),
        "createdAt": row.get("created_at"),
        "updatedAt": row.get("updated_at"),
    }
    return SearchChunk(
        id=row["id"],
        domain="memory",
        kind=row.get("type") or "memory",
        authority="4dt-memory",
        title=row.get("summary") or row.get("content") or row["id"],
        path=row.get("source_ref") or "",
        item_id=row["id"],
        section=row.get("scope") or "",
        text=text,
        metadata={key: value for key, value in metadata.items() if value is not None},
        content_hash=sha256_text(text),
    )


def search_memory_rows(
    query: str | dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    limit: int,
    options: SearchOptions,
) -> tuple[list[tuple[float, dict[str, Any]]], dict[str, Any]]:
    chunks = [chunk_from_memory(row) for row in rows]
    row_by_id = {row["id"]: row for row in rows}
    ranked, explain = rank_chunks(query, chunks, limit=limit, options=options)
    return [(score, row_by_id[chunk.item_id or chunk.id]) for score, chunk in ranked], explain
