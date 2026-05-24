from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .indexer import SearchError, build_index, check_index, get, normalize_domains, search_with_explain, stats
from .scoring import SearchOptions, normalize_fields


def payload(ok: bool, status: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "status": status, **extra}


def error_payload(code: str, message: str) -> dict[str, Any]:
    return payload(False, "error", error={"code": code, "message": message})


def print_result(value: dict[str, Any], json_output: bool) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def load_query(args: argparse.Namespace) -> str | dict[str, Any]:
    sources = [bool(args.query), bool(args.query_json), bool(args.query_file)]
    if sum(1 for item in sources if item) != 1:
        raise SearchError("invalid_query", "Provide exactly one query source: query text, --query-json, or --query-file.")
    if args.query_json:
        try:
            value = json.loads(args.query_json)
        except json.JSONDecodeError as exc:
            raise SearchError("invalid_query_json", str(exc)) from exc
        if not isinstance(value, dict):
            raise SearchError("invalid_query_json", "JSON query must be an object.")
        return value
    if args.query_file:
        try:
            value = json.loads(Path(args.query_file).read_text(encoding="utf-8"))
        except OSError as exc:
            raise SearchError("query_file_read_failed", str(exc)) from exc
        except json.JSONDecodeError as exc:
            raise SearchError("invalid_query_json", str(exc)) from exc
        if not isinstance(value, dict):
            raise SearchError("invalid_query_json", "JSON query file must contain an object.")
        return value
    return str(args.query)


def search_options(args: argparse.Namespace, query: str | dict[str, Any]) -> SearchOptions:
    mode = args.mode or "plain"
    if isinstance(query, dict):
        if args.mode and args.mode != "json":
            raise SearchError("invalid_query", "JSON queries require --mode json or no explicit mode.")
        mode = "json"
    if mode == "json" and not isinstance(query, dict):
        raise SearchError("invalid_query", "--mode json requires --query-json or --query-file.")
    if args.max_candidates is not None and args.max_candidates < args.limit:
        raise SearchError("invalid_max_candidates", "Max candidates must be greater than or equal to limit.")
    try:
        fields = normalize_fields(args.field)
    except ValueError as exc:
        raise SearchError("invalid_field", str(exc)) from exc
    return SearchOptions(
        mode=mode,
        match=args.match,
        fields=fields,
        max_candidates=args.max_candidates,
        explain=args.explain,
    )


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).resolve()
    action = args.action
    if action == "index-build":
        return 0, payload(True, "ready", index=build_index(workspace))
    if action == "index-check":
        status, issues, manifest = check_index(workspace)
        return (0 if status == "ready" else 2), payload(True, status, issues=issues, manifest=manifest)
    if action == "stats":
        return 0, payload(True, "ready", stats=stats(workspace))
    if action == "search":
        if args.limit < 1:
            raise SearchError("invalid_limit", "Search limit must be greater than zero.")
        domains = normalize_domains(args.domain)
        query = load_query(args)
        options = search_options(args, query)
        matches, explain = search_with_explain(
            workspace,
            query,
            domains=domains,
            limit=args.limit,
            options=options,
            index_mode=args.index,
        )
        status = "indexed_then_searched" if explain.get("index", {}).get("rebuilt") else "ready"
        result = payload(True, status, matches=matches, limit=args.limit, index=explain.get("index", {}))
        if args.explain:
            result["explain"] = {
                **explain,
                "queryType": "json" if isinstance(query, dict) else "text",
            }
        return 0, result
    if action == "get":
        return 0, payload(True, "ready", result=get(workspace, args.result_id))
    raise SearchError("unknown_command", f"Unknown command: {action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="4dt-search")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="action", required=True)

    index = sub.add_parser("index")
    add_runtime_arguments(index)
    index_sub = index.add_subparsers(dest="index_action", required=True)
    index_build = index_sub.add_parser("build")
    add_runtime_arguments(index_build)
    index_build.set_defaults(action="index-build")
    index_check = index_sub.add_parser("check")
    add_runtime_arguments(index_check)
    index_check.set_defaults(action="index-check")

    for command_name in ("search", "query"):
        search_parser = sub.add_parser(command_name)
        add_runtime_arguments(search_parser)
        search_parser.add_argument("query", nargs="?")
        search_parser.add_argument("--domain")
        search_parser.add_argument("--limit", type=int, default=10)
        search_parser.add_argument("--match", choices=["all", "any"], default="all")
        search_parser.add_argument("--mode", choices=["plain", "extended", "json"])
        search_parser.add_argument("--query-json")
        search_parser.add_argument("--query-file")
        search_parser.add_argument("--field", action="append")
        search_parser.add_argument("--explain", action="store_true")
        search_parser.add_argument("--max-candidates", type=int)
        search_parser.add_argument("--index", choices=["auto", "readonly", "rebuild"], default="auto")
        search_parser.set_defaults(action="search")

    get_parser = sub.add_parser("get")
    add_runtime_arguments(get_parser)
    get_parser.add_argument("result_id")
    get_parser.set_defaults(action="get")

    stats_parser = sub.add_parser("stats")
    add_runtime_arguments(stats_parser)
    return parser


def add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workspace", default=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        exit_code, result = command(args)
    except SearchError as error:
        result = error_payload(error.code, error.message)
        print_result(result, args.json)
        return 1
    print_result(result, args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
