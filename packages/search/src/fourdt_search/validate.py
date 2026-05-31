from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, TypeVar

from .indexer import build_index, check_index, get, normalize_domains, search, stats
from .scoring import SearchOptions, normalize_fields
from .storage import index_bytes

T = TypeVar("T")


QUALITY_CASES = [
    {
        "name": "exact_board_task",
        "query": "Develop 4dt-search universal search CLI",
        "domains": "board",
        "expectedDomain": "board",
        "expectedAny": ["EPIC-0001-TASK-0008", "4dt-search"],
    },
    {
        "name": "fuzzy_board_task",
        "query": "Develop 4dt serch unversal CLI",
        "domains": "board",
        "expectedDomain": "board",
        "expectedAny": ["4dt-search", "search"],
    },
    {
        "name": "source_contract_content",
        "query": "quality_accepted quality_rejected Acceptance Matrix",
        "domains": "sources",
        "expectedDomain": "sources",
        "expectedAny": ["Acceptance Matrix", "Quality Agent Rules"],
    },
    {
        "name": "wiki_contract_section",
        "query": "Workspace Tools Contract",
        "domains": "wiki",
        "expectedDomain": "wiki",
        "expectedAny": ["Workspace Tools", "Contract"],
    },
    {
        "name": "board_timeline",
        "query": "Implementation-ready handoff for 4dt-search validation",
        "domains": "board",
        "expectedDomain": "board",
        "expectedAny": ["validation", "4dt-search"],
    },
    {
        "name": "low_signal_noise",
        "query": "zzzz-unlikely-4dt-search-noise-token",
        "domains": "sources,wiki,board",
        "expectedDomain": "",
        "expectedAny": [],
    },
    {
        "name": "plain_any_workflow_terms",
        "query": "workflow configuration lifecycle transitions",
        "domains": "sources",
        "match": "any",
        "fields": "title,path,body",
        "expectedDomain": "sources",
        "expectedAny": ["lifecycle", "workflow"],
    },
    {
        "name": "extended_or_wiki_concepts",
        "query": "Workspace Tools | Source Boundaries",
        "domains": "wiki",
        "mode": "extended",
        "fields": "title,body,path",
        "expectedDomain": "wiki",
        "expectedAny": ["Workspace Tools", "Source Boundaries"],
    },
    {
        "name": "json_task_lifecycle_decision",
        "query": {"$and": [{"title": "Task Lifecycle Flow"}, {"body": "Role transitions"}]},
        "domains": "wiki",
        "mode": "json",
        "fields": "title,body,path",
        "expectedDomain": "wiki",
        "expectedAny": ["Role transitions", "Task Lifecycle"],
    },
]


def timed(fn: Callable[[], T]) -> tuple[T, float]:
    started = time.perf_counter()
    value = fn()
    return value, round((time.perf_counter() - started) * 1000, 3)


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def result_text(match: dict[str, Any]) -> str:
    values = [
        match.get("id", ""),
        match.get("domain", ""),
        match.get("kind", ""),
        match.get("path", ""),
        match.get("title", ""),
        match.get("snippet", ""),
        match.get("itemId", ""),
        match.get("pageId", ""),
        match.get("sourceId", ""),
        match.get("section", ""),
    ]
    return " ".join(str(value) for value in values if value)


def content_text(payload: Any) -> str:
    if isinstance(payload, dict):
        return " ".join(content_text(value) for value in payload.values())
    if isinstance(payload, list):
        return " ".join(content_text(value) for value in payload)
    return str(payload)


def evaluate_case(workspace: Path, case: dict[str, Any], limit: int) -> dict[str, Any]:
    domains = normalize_domains(str(case["domains"]))
    options = SearchOptions(
        mode=str(case.get("mode", "plain")),
        match=str(case.get("match", "all")),
        fields=normalize_fields([str(case["fields"])]) if case.get("fields") else normalize_fields(None),
    )
    matches, elapsed_ms = timed(lambda: search(workspace, case["query"], domains=domains, limit=limit, options=options))
    top = matches[0] if matches else None
    expected_domain = str(case.get("expectedDomain", ""))
    expected_any = [str(item).lower() for item in case.get("expectedAny", [])]
    top_text = result_text(top).lower() if top else ""
    domain_pass = not expected_domain or bool(top and top.get("domain") == expected_domain)
    get_elapsed_ms: float | None = None
    get_status = "skipped"
    get_text = ""
    if top:
        try:
            get_payload, get_elapsed_ms = timed(lambda: get(workspace, str(top["id"])))
            get_text = content_text(get_payload).lower()
            get_status = "ready"
        except Exception as exc:  # pragma: no cover - reported as validation evidence
            get_status = f"error:{getattr(exc, 'code', type(exc).__name__)}"
    combined_text = f"{top_text} {get_text}"
    text_pass = not expected_any or any(item in combined_text for item in expected_any)
    return {
        "name": case["name"],
        "query": case["query"],
        "domains": case["domains"],
        "mode": options.mode,
        "match": options.match,
        "fields": list(options.fields),
        "elapsedMs": elapsed_ms,
        "matchCount": len(matches),
        "top": top,
        "getElapsedMs": get_elapsed_ms,
        "getStatus": get_status,
        "quality": "pass" if domain_pass and text_pass else "needs_improvement",
        "checks": {
            "expectedDomain": expected_domain,
            "domainPass": domain_pass,
            "expectedAny": case.get("expectedAny", []),
            "textPass": text_pass,
        },
    }


def validate_workspace(workspace: Path, *, limit: int) -> dict[str, Any]:
    manifest, build_ms = timed(lambda: build_index(workspace))
    (check_status, check_issues, check_manifest), check_ms = timed(lambda: check_index(workspace))
    stats_payload, stats_ms = timed(lambda: stats(workspace))
    cases = [evaluate_case(workspace, case, limit) for case in QUALITY_CASES]
    issue_count = sum(1 for case in cases if case["quality"] != "pass")
    return {
        "ok": issue_count == 0 and check_status == "ready",
        "status": "ready" if issue_count == 0 and check_status == "ready" else "needs_improvement",
        "workspace": str(workspace),
        "timingsMs": {
            "indexBuild": build_ms,
            "indexCheck": check_ms,
            "stats": stats_ms,
        },
        "index": {
            "manifest": manifest,
            "checkStatus": check_status,
            "checkIssues": check_issues,
            "checkManifest": check_manifest,
            "indexBytes": index_bytes(workspace),
        },
        "stats": stats_payload,
        "qualityCases": cases,
        "summary": {
            "caseCount": len(cases),
            "passCount": len(cases) - issue_count,
            "needsImprovementCount": issue_count,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="4dt-search-validate")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.limit < 1:
        print(json.dumps({"ok": False, "status": "error", "error": {"code": "invalid_limit"}}, indent=2))
        return 1
    payload = validate_workspace(Path(args.workspace).resolve(), limit=args.limit)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
