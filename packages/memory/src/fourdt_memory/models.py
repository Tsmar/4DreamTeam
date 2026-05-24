from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryItem:
    id: str
    workspace_id: str
    scope: str
    type: str
    role: str | None
    content: str
    summary: str | None
    metadata_json: str
    confidence: float
    source_type: str | None
    source_ref: str | None
    evidence_hash: str | None
    ttl_at: str | None
    created_at: str
    updated_at: str
    deleted_at: str | None
