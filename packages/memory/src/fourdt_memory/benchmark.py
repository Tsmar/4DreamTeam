from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fourdt_search.records import SearchChunk, sha256_text
from fourdt_search.scoring import SearchOptions, rank_chunks


@dataclass(frozen=True)
class BenchmarkMemory:
    id: str
    category: str
    content: str
    source_type: str
    source_ref: str


@dataclass(frozen=True)
class BenchmarkQuery:
    id: str
    query: str
    expected_ids: tuple[str, ...]
    category: str


@dataclass(frozen=True)
class AgentProtocolQuery:
    id: str
    raw_query: str
    english_queries: tuple[str, ...]
    expected_ids: tuple[str, ...]
    category: str


MEMORY_FIXTURE: tuple[BenchmarkMemory, ...] = (
    BenchmarkMemory(
        "mem_storage_root",
        "accepted_decision",
        "Default 4DT Memory storage is the shared workspace SQLite database at .4dt/db.sqlite3.",
        "task",
        "tasks/done/EPIC-0007-TASK-0030-sqlite-store-paths-migrations-audit.md",
    ),
    BenchmarkMemory(
        "mem_sqlite_authority",
        "accepted_decision",
        "SQLite is the authoritative store for memory items, evidence, sessions, contract defaults, and audit logs.",
        "task",
        "tasks/done/EPIC-0007-TASK-0030-sqlite-store-paths-migrations-audit.md",
    ),
    BenchmarkMemory(
        "mem_runtime_search",
        "accepted_decision",
        "4DT Memory search ranks live SQLite memory rows at runtime through the shared 4dt-search backend.",
        "task",
        "tasks/developer/EPIC-0001-TASK-0013-replace-memory-search-backend.md",
    ),
    BenchmarkMemory(
        "mem_preview_get",
        "accepted_decision",
        "Memory search returns concise preview fields by default; use get by id to retrieve full memory content.",
        "task",
        "tasks/done/EPIC-0007-TASK-0033-memory-search-reindex.md",
    ),
    BenchmarkMemory(
        "mem_export_private",
        "accepted_decision",
        "JSONL export can contain sensitive accepted memory and should be handled as local private data.",
        "task",
        "tasks/done/EPIC-0007-TASK-0034-import-export-session-benchmark.md",
    ),
    BenchmarkMemory(
        "mem_import_apply",
        "accepted_decision",
        "JSONL import is dry-run by default and writes memory rows only when --apply is explicit.",
        "task",
        "tasks/done/EPIC-0007-TASK-0034-import-export-session-benchmark.md",
    ),
    BenchmarkMemory(
        "mem_no_sources_read",
        "source_boundary_rule",
        "Memory commands and benchmark behavior must not read workspace sources by default.",
        "task",
        "tasks/done/EPIC-0007-TASK-0036-end-to-end-quality-release-readiness.md",
    ),
    BenchmarkMemory(
        "mem_sources_first_touch",
        "source_boundary_rule",
        "Workspace sources require operator first-touch confirmation before listing, statting, resolving, indexing, or reading.",
        "task",
        "tasks/released/TASK-0021-sources-trust-boundary.md",
    ),
    BenchmarkMemory(
        "mem_no_secrets",
        "source_boundary_rule",
        "Do not store secrets, credentials, tokens, private keys, local secret files, dumps, production data, or personal data in memory.",
        "task",
        "tasks/done/EPIC-0007-TASK-0032-remember-forget-evidence-redaction.md",
    ),
    BenchmarkMemory(
        "mem_unaccepted_speculation",
        "source_boundary_rule",
        "Durable memory must not store unaccepted speculation, rejected assumptions, or unsupported claims.",
        "task",
        "tasks/done/EPIC-0007-TASK-0032-remember-forget-evidence-redaction.md",
    ),
    BenchmarkMemory(
        "mem_user_pref_russian",
        "user_preference",
        "The operator prefers Russian-language summaries in conversation while internal framework artifacts remain English.",
        "user",
        "operator preference",
    ),
    BenchmarkMemory(
        "mem_user_pref_commits",
        "user_preference",
        "The operator wants implementation tasks committed separately so individual tasks can be reverted independently.",
        "user",
        "operator preference",
    ),
    BenchmarkMemory(
        "mem_task_filename",
        "process_constraint",
        "Epic-owned task filenames should use EPIC-XXXX-TASK-XXXX-description.md when tasks belong to an epic.",
        "task",
        "tasks/backlog/EPIC-0006-epic-task-naming-and-closure-lifecycle.md",
    ),
    BenchmarkMemory(
        "mem_epic_handoff",
        "process_constraint",
        "When an epic is complete, create a handoff, move the epic to done, and move the previous handoff to done when applicable.",
        "task",
        "tasks/backlog/EPIC-0006-epic-task-naming-and-closure-lifecycle.md",
    ),
    BenchmarkMemory(
        "mem_start_handoff",
        "process_constraint",
        "At the start of continuation work, always look for a backlog handoff before broad task history.",
        "task",
        "tasks/backlog/EPIC-0006-epic-task-naming-and-closure-lifecycle.md",
    ),
    BenchmarkMemory(
        "mem_search_quality",
        "implementation_lesson",
        "Memory recall quality is improved by agent-authored precise English query variants plus field filters.",
        "quality",
        "reports/quality/accepted/EPIC-0001-TASK-0012-quality.md",
    ),
    BenchmarkMemory(
        "mem_pytest_optional",
        "implementation_lesson",
        "Memory tests use dependency-free unittest as the canonical runner; pytest is optional only when installed.",
        "task",
        "tasks/developer/EPIC-0007-TASK-0037-memory-retrieval-quality-benchmark-and-test-runner-contract.md",
    ),
    BenchmarkMemory(
        "mem_import_perf",
        "implementation_lesson",
        "Import --apply is the slowest local memory path because every row writes audited SQLite records.",
        "quality",
        "reports/quality/accepted/EPIC-0007-TASK-0036-quality.md",
    ),
    BenchmarkMemory(
        "mem_unavailable_ok",
        "implementation_lesson",
        "Memory unavailable or uninitialized must not fail the 4DreamTeam workflow.",
        "task",
        "tasks/done/EPIC-0007-TASK-0033-memory-search-reindex.md",
    ),
    BenchmarkMemory(
        "mem_session_ttl",
        "accepted_decision",
        "Session state is local continuation state and must be JSON-object data with a size limit and TTL.",
        "task",
        "tasks/done/EPIC-0007-TASK-0034-import-export-session-benchmark.md",
    ),
    BenchmarkMemory(
        "mem_release_no_push",
        "process_constraint",
        "Release readiness does not authorize staging, pushing, tagging, publishing, or release artifacts without explicit release workflow approval.",
        "task",
        "tasks/done/EPIC-0007-TASK-0036-end-to-end-quality-release-readiness.md",
    ),
    BenchmarkMemory(
        "mem_docs_no_legacy",
        "accepted_decision",
        "Primary memory docs should describe local 4DT Memory and should not keep the removed legacy memory page.",
        "task",
        "tasks/done/EPIC-0007-TASK-0035-skill-memory-policy-docs-version.md",
    ),
    BenchmarkMemory(
        "mem_redaction_blocking",
        "implementation_lesson",
        "Redaction is a blocking guard before storage, not a reversible masking layer.",
        "task",
        "tasks/done/EPIC-0007-TASK-0032-remember-forget-evidence-redaction.md",
    ),
)


QUERY_FIXTURE: tuple[BenchmarkQuery, ...] = (
    BenchmarkQuery("q_storage", "where does memory store its database", ("mem_storage_root",), "accepted_decision"),
    BenchmarkQuery("q_sqlite", "which store is authoritative", ("mem_sqlite_authority",), "accepted_decision"),
    BenchmarkQuery("q_runtime", "how does memory search rank sqlite rows", ("mem_runtime_search",), "accepted_decision"),
    BenchmarkQuery("q_preview", "why search does not return full content", ("mem_preview_get",), "accepted_decision"),
    BenchmarkQuery("q_export", "is exported jsonl private data", ("mem_export_private",), "accepted_decision"),
    BenchmarkQuery("q_import", "does import write by default", ("mem_import_apply",), "accepted_decision"),
    BenchmarkQuery("q_sources", "should benchmark read sources folder", ("mem_no_sources_read",), "source_boundary_rule"),
    BenchmarkQuery("q_first_touch", "when can sources be listed", ("mem_sources_first_touch",), "source_boundary_rule"),
    BenchmarkQuery("q_secrets", "can memory save tokens or private keys", ("mem_no_secrets",), "source_boundary_rule"),
    BenchmarkQuery("q_speculation", "can we remember unaccepted assumptions", ("mem_unaccepted_speculation",), "source_boundary_rule"),
    BenchmarkQuery("q_russian", "what language should user-facing summaries use", ("mem_user_pref_russian",), "user_preference"),
    BenchmarkQuery("q_commits", "why commit implementation tasks separately", ("mem_user_pref_commits",), "user_preference"),
    BenchmarkQuery("q_filename", "how name task files inside epic", ("mem_task_filename",), "process_constraint"),
    BenchmarkQuery("q_handoff", "what happens when an epic is complete", ("mem_epic_handoff",), "process_constraint"),
    BenchmarkQuery("q_start", "what to inspect when continuing work", ("mem_start_handoff",), "process_constraint"),
    BenchmarkQuery("q_quality", "how improve memory recall quality", ("mem_search_quality",), "implementation_lesson"),
    BenchmarkQuery("q_runner", "which test runner is required", ("mem_pytest_optional",), "implementation_lesson"),
    BenchmarkQuery("q_perf", "which operation is slowest in performance test", ("mem_import_perf",), "implementation_lesson"),
    BenchmarkQuery("q_unavailable", "should unavailable memory stop workflow", ("mem_unavailable_ok",), "implementation_lesson"),
    BenchmarkQuery("q_session", "what limits session state", ("mem_session_ttl",), "accepted_decision"),
    BenchmarkQuery("q_release", "does readiness allow push or tag", ("mem_release_no_push",), "process_constraint"),
    BenchmarkQuery("q_docs", "what happened to legacy memory docs", ("mem_docs_no_legacy",), "accepted_decision"),
    BenchmarkQuery("q_redaction", "is redaction reversible masking", ("mem_redaction_blocking",), "implementation_lesson"),
)


AGENT_PROTOCOL_QUERY_FIXTURE: tuple[AgentProtocolQuery, ...] = (
    AgentProtocolQuery(
        "ap_memory_architecture",
        "как работает память в dreamteam",
        (
            "4DreamTeam memory architecture SQLite authoritative runtime 4dt-search",
            "4DT Memory local storage search backend workflow",
            "memory policy tasks reports approved source boundary",
        ),
        ("mem_sqlite_authority", "mem_runtime_search", "mem_unavailable_ok"),
        "accepted_decision",
    ),
    AgentProtocolQuery(
        "ap_memory_storage",
        "где лежит база памяти",
        (
            "4DT Memory shared SQLite database",
            "default memory storage .4dt db.sqlite3",
            "SQLite memory tables shared workspace database",
        ),
        ("mem_storage_root",),
        "accepted_decision",
    ),
    AgentProtocolQuery(
        "ap_sources_boundary",
        "можно ли памяти читать sources",
        (
            "memory commands benchmark must not read workspace sources",
            "sources first-touch confirmation before listing reading indexing",
            "source boundary memory search approved sources verification",
        ),
        ("mem_no_sources_read", "mem_sources_first_touch"),
        "source_boundary_rule",
    ),
    AgentProtocolQuery(
        "ap_search_quality",
        "как сделать поиск памяти качественнее",
        (
            "memory recall quality agent-authored precise English query variants field filters",
            "4dt-search advanced controls match mode field max candidates",
            "agent translates operator intent into effective search queries",
        ),
        ("mem_search_quality",),
        "implementation_lesson",
    ),
    AgentProtocolQuery(
        "ap_cli_preview",
        "почему search не отдает полный текст",
        (
            "memory search returns concise preview fields by default",
            "use get by id retrieve full memory content",
            "preview-first search full content get command",
        ),
        ("mem_preview_get",),
        "accepted_decision",
    ),
    AgentProtocolQuery(
        "ap_unavailable",
        "если память сломалась работа должна падать",
        (
            "memory unavailable uninitialized must not fail 4DreamTeam workflow",
            "workflow continues with tasks reports wiki approved sources",
            "doctor init storage missing recovery guidance",
        ),
        ("mem_unavailable_ok",),
        "implementation_lesson",
    ),
    AgentProtocolQuery(
        "ap_runner",
        "какой тест раннер нужен для memory",
        (
            "memory tests dependency-free unittest canonical runner",
            "pytest optional only when installed",
            "python3 -m unittest discover memory tests",
        ),
        ("mem_pytest_optional",),
        "implementation_lesson",
    ),
    AgentProtocolQuery(
        "ap_release",
        "можно ли пушить после readiness",
        (
            "release readiness does not authorize push tag publish staging",
            "release workflow approval required before staging pushing tagging",
            "release process constraints no push without explicit approval",
        ),
        ("mem_release_no_push",),
        "process_constraint",
    ),
)


def _chunks(memories: tuple[BenchmarkMemory, ...]) -> list[SearchChunk]:
    return [
        SearchChunk(
            id=memory.id,
            domain="memory",
            kind=memory.category,
            authority="4dt-memory-benchmark",
            title=memory.content,
            path=memory.source_ref,
            item_id=memory.id,
            text=f"{memory.content}\n{memory.source_type}\n{memory.source_ref}",
            content_hash=sha256_text(memory.content),
        )
        for memory in memories
    ]


def _rank_search(query: str, memories: tuple[BenchmarkMemory, ...]) -> list[tuple[str, float]]:
    ranked, _explain = rank_chunks(
        query,
        _chunks(memories),
        limit=len(memories),
        options=SearchOptions(match="all", fields=("title", "path", "kind", "body")),
    )
    return [(chunk.id, score) for score, chunk in ranked]


def _rank_agent_protocol(queries: tuple[str, ...], memories: tuple[BenchmarkMemory, ...]) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    match_counts: dict[str, int] = {}
    for query in queries:
        for memory_id, score in _rank_search(query, memories):
            scores[memory_id] = max(scores.get(memory_id, 0.0), score)
            match_counts[memory_id] = match_counts.get(memory_id, 0) + 1
    scored = [
        (memory_id, score + min(match_counts.get(memory_id, 0), 3) * 0.01)
        for memory_id, score in scores.items()
    ]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored


def _metrics(mode: str, rankings: dict[str, list[tuple[str, float]]], queries: tuple[BenchmarkQuery, ...] = QUERY_FIXTURE) -> dict[str, Any]:
    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    reciprocal_rank_total = 0.0
    false_negatives = 0
    irrelevant_stale_recalls = 0
    query_results = []

    for query in queries:
        expected = set(query.expected_ids)
        ranked = rankings[query.id]
        ranked_ids = [memory_id for memory_id, _score in ranked]
        top5 = ranked_ids[:5]
        top1_hits += int(bool(expected & set(ranked_ids[:1])))
        top3_hits += int(bool(expected & set(ranked_ids[:3])))
        top5_has_expected = bool(expected & set(top5))
        top5_hits += int(top5_has_expected)
        if not top5_has_expected:
            false_negatives += 1
        irrelevant_stale_recalls += len([memory_id for memory_id in top5 if memory_id not in expected])

        reciprocal_rank = 0.0
        for index, memory_id in enumerate(ranked_ids, start=1):
            if memory_id in expected:
                reciprocal_rank = 1.0 / index
                break
        reciprocal_rank_total += reciprocal_rank
        query_results.append(
            {
                "id": query.id,
                "query": query.query,
                "category": query.category,
                "expectedIds": list(query.expected_ids),
                "top5": [
                    {"id": memory_id, "score": round(score, 6)}
                    for memory_id, score in ranked[:5]
                ],
                "reciprocalRank": round(reciprocal_rank, 6),
            }
        )

    total = len(queries)
    return {
        "mode": mode,
        "queryCount": total,
        "top1": round(top1_hits / total, 6),
        "top3": round(top3_hits / total, 6),
        "top5": round(top5_hits / total, 6),
        "mrr": round(reciprocal_rank_total / total, 6),
        "falseNegatives": false_negatives,
        "irrelevantStaleRecalls": irrelevant_stale_recalls,
        "queries": query_results,
    }


def _agent_protocol_metrics(
    mode: str,
    rankings: dict[str, list[tuple[str, float]]],
    queries: tuple[AgentProtocolQuery, ...] = AGENT_PROTOCOL_QUERY_FIXTURE,
) -> dict[str, Any]:
    benchmark_queries = tuple(
        BenchmarkQuery(query.id, query.raw_query, query.expected_ids, query.category)
        for query in queries
    )
    metrics = _metrics(mode, rankings, benchmark_queries)
    for query_result, query in zip(metrics["queries"], queries):
        query_result["rawQuery"] = query.raw_query
        query_result["englishQueries"] = list(query.english_queries)
    return metrics


def retrieval_quality_benchmark() -> dict[str, Any]:
    search_rankings = {query.id: _rank_search(query.query, MEMORY_FIXTURE) for query in QUERY_FIXTURE}
    raw_protocol_rankings = {
        query.id: _rank_search(query.raw_query, MEMORY_FIXTURE) for query in AGENT_PROTOCOL_QUERY_FIXTURE
    }
    agent_protocol_rankings = {
        query.id: _rank_agent_protocol(query.english_queries, MEMORY_FIXTURE)
        for query in AGENT_PROTOCOL_QUERY_FIXTURE
    }
    raw_protocol_metrics = _agent_protocol_metrics("raw-user-query", raw_protocol_rankings)
    agent_protocol_metrics = _agent_protocol_metrics("english-first-agent-protocol", agent_protocol_rankings)
    return {
        "profile": "retrieval-quality",
        "fixture": {
            "memoryCount": len(MEMORY_FIXTURE),
            "queryCount": len(QUERY_FIXTURE),
            "agentProtocolQueryCount": len(AGENT_PROTOCOL_QUERY_FIXTURE),
            "categories": sorted({memory.category for memory in MEMORY_FIXTURE}),
            "safeFixture": True,
            "sourceBoundary": "does_not_read_sources",
        },
        "modes": [
            _metrics("4dt-search-runtime", search_rankings),
        ],
        "agentProtocolComparison": {
            "purpose": "Compare a single raw user query against bounded English-first typed query variants.",
            "modes": [
                raw_protocol_metrics,
                agent_protocol_metrics,
            ],
            "result": {
                "top3Improved": agent_protocol_metrics["top3"] > raw_protocol_metrics["top3"],
                "mrrImproved": agent_protocol_metrics["mrr"] > raw_protocol_metrics["mrr"],
                "falseNegativesReduced": agent_protocol_metrics["falseNegatives"]
                < raw_protocol_metrics["falseNegatives"],
                "staleRecallDelta": agent_protocol_metrics["irrelevantStaleRecalls"]
                - raw_protocol_metrics["irrelevantStaleRecalls"],
            },
        },
        "interpretation": {
            "searchMode": "4dt-search ranks live memory rows at runtime from SQLite without a separate persisted retrieval index",
            "agentProtocol": "English-first typed query variants improve bilingual/conceptual recall without changing storage",
            "authority": "benchmark evaluates recall only; tasks, reports, wiki, approvals, and approved sources remain authoritative",
        },
    }
