from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .domains import board, memory, sources, wiki
from .records import SearchChunk, result_payload
from .scoring import SearchOptions, filter_domains, rank_chunks
from .storage import chunks_path, find_chunk, manifest_path, read_chunks, read_json, write_chunks, write_json

INDEX_VERSION = 1
PERSISTENT_DOMAINS = {"sources", "wiki", "board"}
DEFAULT_DOMAINS = {"sources", "wiki", "board", "memory"}


class SearchError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_domains(raw: str | None) -> set[str]:
    if not raw:
        return set(DEFAULT_DOMAINS)
    domains = {item.strip() for item in raw.split(",") if item.strip()}
    invalid = domains - DEFAULT_DOMAINS
    if invalid:
        raise SearchError("invalid_domain", f"Unsupported search domain: {', '.join(sorted(invalid))}")
    return domains or set(DEFAULT_DOMAINS)


def collect_chunks(workspace: Path, domains: set[str] | None = None) -> list[SearchChunk]:
    selected = domains or set(DEFAULT_DOMAINS)
    chunks: list[SearchChunk] = []
    if "sources" in selected:
        chunks.extend(sources.collect(workspace))
    if "wiki" in selected:
        chunks.extend(wiki.collect(workspace))
    if "board" in selected:
        chunks.extend(board.collect(workspace))
    if "memory" in selected:
        chunks.extend(memory.collect(workspace))
    return chunks


def build_index(workspace: Path) -> dict[str, Any]:
    chunks = collect_chunks(workspace, PERSISTENT_DOMAINS)
    write_chunks(workspace, chunks)
    counts: dict[str, int] = {}
    for chunk in chunks:
        counts[chunk.domain] = counts.get(chunk.domain, 0) + 1
    manifest = {
        "schemaVersion": INDEX_VERSION,
        "generatedAt": iso_now(),
        "chunkCount": len(chunks),
        "domainCounts": counts,
        "domains": sorted(PERSISTENT_DOMAINS),
        "chunksPath": ".4dt/search/chunks.jsonl",
    }
    write_json(manifest_path(workspace), manifest)
    return manifest


def check_index(workspace: Path) -> tuple[str, list[dict[str, str]], dict[str, Any]]:
    issues: list[dict[str, str]] = []
    manifest = read_json(manifest_path(workspace))
    if not manifest:
        issues.append({"code": "missing_manifest", "severity": "error", "message": "Search manifest is missing or unreadable."})
    elif manifest.get("schemaVersion") != INDEX_VERSION:
        issues.append({"code": "schema_mismatch", "severity": "error", "message": "Search manifest schema version is unsupported."})
    if not chunks_path(workspace).exists():
        issues.append({"code": "missing_chunks", "severity": "error", "message": "Search chunks file is missing."})
    else:
        chunks = read_chunks(workspace)
        if manifest and manifest.get("chunkCount") != len(chunks):
            issues.append({"code": "chunk_count_mismatch", "severity": "warning", "message": "Manifest chunk count differs from chunks file."})
    return ("ready" if not any(issue["severity"] == "error" for issue in issues) else "issues", issues, manifest)


def freshness_issues(workspace: Path, domains: set[str]) -> list[dict[str, str]]:
    selected = domains & PERSISTENT_DOMAINS
    if not selected:
        return []
    status, issues, _manifest = check_index(workspace)
    if status != "ready":
        return issues
    stored = [chunk for chunk in read_chunks(workspace) if chunk.domain in selected]
    current = collect_chunks(workspace, selected)
    stored_keys = {(chunk.domain, chunk.id, chunk.content_hash) for chunk in stored}
    current_keys = {(chunk.domain, chunk.id, chunk.content_hash) for chunk in current}
    if stored_keys != current_keys:
        return [
            {
                "code": "stale_chunks",
                "severity": "error",
                "message": "Search chunks differ from current workspace content.",
            }
        ]
    return []


def stats(workspace: Path) -> dict[str, Any]:
    status, issues, manifest = check_index(workspace)
    chunks = read_chunks(workspace) if chunks_path(workspace).exists() else []
    domain_counts: dict[str, int] = {}
    for chunk in chunks:
        domain_counts[chunk.domain] = domain_counts.get(chunk.domain, 0) + 1
    return {
        "status": status,
        "chunkCount": len(chunks),
        "domainCounts": domain_counts,
        "generatedAt": manifest.get("generatedAt"),
        "issues": issues,
    }


def search(
    workspace: Path,
    query: str | dict[str, Any],
    *,
    domains: set[str],
    limit: int,
    options: SearchOptions | None = None,
    index_mode: str = "auto",
) -> list[dict[str, Any]]:
    return search_with_explain(workspace, query, domains=domains, limit=limit, options=options, index_mode=index_mode)[0]


def search_with_explain(
    workspace: Path,
    query: str | dict[str, Any],
    *,
    domains: set[str],
    limit: int,
    options: SearchOptions | None = None,
    index_mode: str = "auto",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if index_mode not in {"auto", "readonly", "rebuild"}:
        raise SearchError("invalid_index_mode", f"Unsupported index mode: {index_mode}")
    rebuilt = False
    rebuild_reason = ""
    if index_mode == "rebuild":
        build_index(workspace)
        rebuilt = True
        rebuild_reason = "forced"
    issues = freshness_issues(workspace, domains)
    if issues and index_mode == "readonly":
        raise SearchError("index_not_ready", "; ".join(issue["code"] for issue in issues))
    if issues and index_mode == "auto":
        build_index(workspace)
        rebuilt = True
        rebuild_reason = issues[0]["code"]
    chunks = read_chunks(workspace)
    if "memory" in domains:
        chunks.extend(memory.collect(workspace))
    selected = filter_domains(chunks, domains)
    ranked, explain = rank_chunks(query, selected, limit=limit, options=options)
    snippet_query = query if isinstance(query, str) else ""
    explain["domains"] = sorted(domains)
    explain["index"] = {
        "mode": index_mode,
        "rebuilt": rebuilt,
        "reason": rebuild_reason or None,
        "persistentDomains": sorted(domains & PERSISTENT_DOMAINS),
        "liveDomains": sorted(domains - PERSISTENT_DOMAINS),
    }
    return [result_payload(chunk, score=score, query=snippet_query) for score, chunk in ranked], explain


def get(workspace: Path, result_id: str) -> dict[str, Any]:
    chunk = find_chunk(workspace, result_id)
    if chunk is None:
        if result_id.startswith("mem_"):
            try:
                return {
                    **result_payload(SearchChunk(id=result_id, domain="memory", kind="memory", authority="4dt-memory", item_id=result_id, text="")),
                    "content": memory.read_by_id(workspace, result_id),
                }
            except RuntimeError as exc:
                raise SearchError("not_found", f"Search result not found: {result_id}") from exc
        raise SearchError("not_found", f"Search result not found: {result_id}")
    try:
        if chunk.domain == "sources":
            content = sources.read(workspace, chunk)
        elif chunk.domain == "wiki":
            content = wiki.read(workspace, chunk)
        elif chunk.domain == "board":
            content = board.read(workspace, chunk)
        elif chunk.domain == "memory":
            content = memory.read(workspace, chunk)
        else:
            raise SearchError("invalid_domain", f"Unsupported result domain: {chunk.domain}")
    except SearchError:
        raise
    except RuntimeError as exc:
        code = str(exc) or "stale_result"
        raise SearchError(code, f"Unable to read current content for result {result_id}: {code}") from exc
    except Exception as exc:
        code = getattr(exc, "code", "read_failed")
        message = getattr(exc, "message", str(exc))
        raise SearchError(str(code), str(message)) from exc
    return {**result_payload(chunk, include_text=False), "content": content}
