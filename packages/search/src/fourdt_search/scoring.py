from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from .engine import SearchEngine
from .records import SearchChunk

TOKEN_RE = re.compile(r"[a-z0-9а-яё]+", re.IGNORECASE)
DEFAULT_FIELDS = ("title", "path", "domain", "kind", "body")
FIELD_WEIGHTS = {
    "title": 4,
    "path": 3,
    "domain": 2,
    "kind": 2,
    "body": 1,
    "id": 2,
    "sourceId": 2,
    "pageId": 2,
    "itemId": 2,
    "section": 2,
}
ALL_FIELDS = tuple(FIELD_WEIGHTS.keys())


@dataclass(frozen=True)
class SearchOptions:
    mode: str = "plain"
    match: str = "all"
    fields: tuple[str, ...] = DEFAULT_FIELDS
    max_candidates: int | None = None
    explain: bool = False


def tokens(value: str) -> list[str]:
    return [item.lower() for item in TOKEN_RE.findall(value)]


def grams(value: str) -> list[str]:
    output: list[str] = []
    for token in tokens(value):
        if len(token) <= 3:
            output.append(token)
        else:
            output.extend(token[index : index + 3] for index in range(len(token) - 2))
    return output


def normalize_fields(raw_fields: Iterable[str] | None) -> tuple[str, ...]:
    if not raw_fields:
        return DEFAULT_FIELDS
    fields: list[str] = []
    for raw in raw_fields:
        for item in raw.split(","):
            field = item.strip()
            if not field:
                continue
            if field == "all":
                return ALL_FIELDS
            if field not in FIELD_WEIGHTS:
                raise ValueError(f"Unsupported search field: {field}")
            if field not in fields:
                fields.append(field)
    return tuple(fields) or DEFAULT_FIELDS


def query_text(query: str | dict) -> str:
    if isinstance(query, str):
        return query
    return json.dumps(query, ensure_ascii=False, sort_keys=True)


def doc_for_chunk(chunk: SearchChunk) -> dict[str, str]:
    return {
        "id": chunk.id,
        "title": chunk.title,
        "path": chunk.path,
        "body": chunk.text,
        "domain": chunk.domain,
        "kind": chunk.kind,
        "sourceId": chunk.source_id,
        "pageId": chunk.page_id,
        "itemId": chunk.item_id,
        "section": chunk.section,
    }


def searchable_text(chunk: SearchChunk, fields: tuple[str, ...] = DEFAULT_FIELDS) -> str:
    doc = doc_for_chunk(chunk)
    return " ".join(doc[field] for field in fields if doc.get(field))


def candidate_chunks(query: str | dict, chunks: list[SearchChunk], *, fields: tuple[str, ...] = DEFAULT_FIELDS, limit: int = 120) -> list[SearchChunk]:
    query_grams = grams(query_text(query))
    if not query_grams:
        return chunks[:limit]
    inverted: dict[str, set[int]] = defaultdict(set)
    for index, chunk in enumerate(chunks):
        for gram in set(grams(searchable_text(chunk, fields))):
            inverted[gram].add(index)
    counts: Counter[int] = Counter()
    for gram in query_grams:
        for index in inverted.get(gram, set()):
            counts[index] += 1
    if not counts:
        return chunks[:limit]
    return [chunks[index] for index, _count in counts.most_common(limit)]


def rank_chunks(query: str | dict, chunks: list[SearchChunk], *, limit: int, options: SearchOptions | None = None) -> tuple[list[tuple[float, SearchChunk]], dict]:
    opts = options or SearchOptions()
    started = time.perf_counter()
    candidate_limit = opts.max_candidates or max(limit * 12, 60)
    candidates = candidate_chunks(query, chunks, fields=opts.fields, limit=candidate_limit)
    candidate_ms = round((time.perf_counter() - started) * 1000, 3)
    docs = [doc_for_chunk(chunk) for chunk in candidates]
    engine_keys = [{"name": field, "weight": FIELD_WEIGHTS[field]} for field in opts.fields]
    use_extended = opts.mode == "extended"
    use_token = opts.mode == "plain"
    engine = SearchEngine(
        docs,
        {
            "keys": engine_keys,
            "includeScore": True,
            "includeMatches": False,
            "useExtendedSearch": use_extended,
            "useTokenSearch": use_token,
            "tokenMatch": opts.match,
            "threshold": 0.35,
            "ignoreLocation": True,
        },
    )
    by_id = {chunk.id: chunk for chunk in candidates}
    ranked: list[tuple[float, SearchChunk]] = []
    rank_started = time.perf_counter()
    for result in engine.search(query, {"limit": limit}):
        item = result["item"]
        score = float(result.get("score", 1.0))
        chunk = by_id.get(item["id"])
        if chunk is not None:
            ranked.append((score, chunk))
    explain = {
        "mode": opts.mode,
        "match": opts.match,
        "fields": list(opts.fields),
        "limit": limit,
        "maxCandidates": candidate_limit,
        "totalChunks": len(chunks),
        "candidateCount": len(candidates),
        "rankedCount": len(ranked),
        "timingsMs": {
            "candidateSelection": candidate_ms,
            "ranking": round((time.perf_counter() - rank_started) * 1000, 3),
        },
    }
    return ranked, explain


def filter_domains(chunks: Iterable[SearchChunk], domains: set[str]) -> list[SearchChunk]:
    return [chunk for chunk in chunks if chunk.domain in domains]
