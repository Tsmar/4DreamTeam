from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from fourdt_search.scoring import SearchOptions, query_text

from .benchmark import retrieval_quality_benchmark
from .migrations import SchemaMismatch, ensure_current_schema, schema_version
from .paths import workspace_identity, workspace_paths
from .redaction import check_memory_content
from .search_backend import normalize_memory_fields, search_memory_rows
from .sqlite_store import MemoryStore, utc_now


EXIT_OK = 0
EXIT_USER_CONFIG = 1
EXIT_STORAGE = 2
EXIT_DEGRADED = 3
EXIT_UNSAFE_SAVE = 4

PLACEHOLDER_COMMANDS = {
}

SESSION_STATE_MAX_BYTES = 8192
DEFAULT_SESSION_TTL_SECONDS = 24 * 60 * 60
CONTRACT_KEYS = {
    "project.rules": "Project-specific durable operating rules.",
    "project.workflow.current_mode": "Current project working mode name.",
    "project.workflow.modes": "Named project working mode definitions.",
    "project.operator.preferences": "Operator preferences for project work.",
    "project.operator.approval_policy": "Actions that require operator approval.",
    "project.sources.policy": "Project-specific source access policy.",
    "project.delivery.git_policy": "Commit, push, and release packaging preferences.",
    "project.quality.validation_policy": "Required validation checks and quality gates.",
    "project.communication.style": "Preferred operator-facing communication style.",
}
CONTRACT_KEY_ORDER = tuple(CONTRACT_KEYS)
MODE_DEFINITION_FIELDS = {
    "description",
    "autonomy",
    "approval_gates",
    "reporting_style",
    "commit_policy",
    "push_policy",
    "validation_expectations",
}
ONBOARDING_QUESTIONS = {
    "project.rules": "What should every new session remember before proposing work?",
    "project.workflow.current_mode": "What is the default working mode for this project?",
    "project.workflow.modes": "What does each working mode allow the agent to do without stopping?",
    "project.operator.preferences": "What operator preferences should guide this project's work?",
    "project.operator.approval_policy": "Which actions always require operator approval?",
    "project.sources.policy": "Are there project-specific source access rules outside the default workspace sources policy?",
    "project.delivery.git_policy": "How should git commits and pushes be handled?",
    "project.quality.validation_policy": "Which validation checks are mandatory before commit or handoff?",
    "project.communication.style": "How detailed should reports to the operator be?",
}

DEFAULT_WORKFLOW_MODES = {
    "read-only-status": {
        "description": "Inspect status, wiki, memory, source registry, board, git, and docs without edits.",
        "autonomy": "May run read-only commands and summarize current state.",
        "approval_gates": ["Before any file write or repair"],
        "reporting_style": "Short Russian status with concrete tool results.",
        "commit_policy": "No commits.",
        "push_policy": "No pushes.",
        "validation_expectations": ["Prefer command-based checks over managed storage inspection"],
    },
    "skill-development-controlled": {
        "description": "Default mode for this workspace: improve 4DreamTeam-controlled sources with explicit approval for behavior-changing edits and release actions.",
        "autonomy": "May inspect approved sources, use managed wiki/source/board/memory tools, propose plans, implement approved scoped changes, and run local validation checks.",
        "approval_gates": [
            "Before changing files unless the user already approved the exact scope",
            "Before repair commands that mutate workspace state",
            "Before dependency installs or network access",
            "Before destructive commands, infrastructure actions, release packaging, staging, commits, pushes, tags, or publication",
        ],
        "reporting_style": "Concise Russian progress updates and final summaries; internal artifacts and source docs remain English.",
        "commit_policy": "Do not commit unless the user explicitly asks and a visible commit plan exists.",
        "push_policy": "Never push without separate explicit approval.",
        "validation_expectations": [
            "Use 4dt-wiki/4dt-sources/4dt-board validation where relevant",
            "Run affected unittest suites or npm scripts for touched tools",
            "Run npm run rules after reference/template/workflow changes when practical",
        ],
    },
    "wiki-bootstrap-sync": {
        "description": "Create, deepen, or sync managed workspace wiki from approved sources.",
        "autonomy": "May use 4dt-wiki and 4dt-sources after intake/approval; may validate and index wiki.",
        "approval_gates": [
            "Show intake summary before first wiki writes unless scope already approved",
            "Do not document unconfirmed behavior as actual",
        ],
        "reporting_style": "Russian operator summary; wiki pages in English.",
        "commit_policy": "No commits unless separately requested.",
        "push_policy": "No pushes.",
        "validation_expectations": ["4dt-wiki index build", "4dt-wiki index check", "4dt-wiki validate"],
    },
}

DEFAULT_CONTRACT_VALUES: dict[str, tuple[Any, str]] = {
    "project.rules": (
        {
            "project": "4DreamTeam workspace",
            "purpose": "Use the current request, workspace instructions, managed tools, and accepted task/wiki state before proposing work.",
            "language_policy": "Source Markdown docs/templates/references stay English. Operator-facing chat can be Russian when preferred.",
            "memory_search_backend": "4dt-memory uses the shared .4dt/db.sqlite3 SQLite database as the authoritative store and 4dt-search as the runtime retrieval backend.",
            "knowledge_base": "Use managed workspace wiki first via 4dt-wiki search/get when it is available.",
        },
        "json",
    ),
    "project.workflow.current_mode": ("skill-development-controlled", "text"),
    "project.workflow.modes": (DEFAULT_WORKFLOW_MODES, "json"),
    "project.operator.preferences": (
        {
            "collaboration": "Be proactive but show concise status updates. Use 4DreamTeam workflow when applicable.",
            "language": "Russian for chat summaries and collaboration when the operator uses Russian; preserve commands, paths, ids, and role names exactly.",
            "memory_preference": "Persist durable project decisions, gotchas, and operating rules in 4dt-memory when useful for future sessions.",
        },
        "json",
    ),
    "project.operator.approval_policy": (
        {
            "file_edits": "Ask before changing files unless the user has approved the exact scope or explicitly asked to implement.",
            "dependencies": "Ask before installing dependencies or using network access.",
            "destructive_or_infrastructure": "Always ask before destructive commands, deploys, migrations, restarts, production access, secret access, or infrastructure changes.",
            "git": "Show commit plan and ask before staging or committing. Ask separately before pushing, tagging, or publishing releases.",
            "source_boundaries": "External source paths require explicit 4dt-sources registry approval.",
            "workspace_repairs": "Ask before repair commands or initialization that changes managed state, except when the user directly requested it.",
        },
        "json",
    ),
    "project.sources.policy": (
        {
            "builtin_boundary": "Workspace sources/ is readable by default through 4dt-sources.",
            "tooling": "Use 4dt-sources registry/list/search/get before broad source reading. Use 4dt-wiki search/get before broad source reading when answering project structure questions.",
            "forbidden": "Do not read or expose secrets, .env files, keys, dumps, credentials, or unrelated user files.",
        },
        "json",
    ),
    "project.delivery.git_policy": (
        {
            "commits": "Do not commit unless the operator explicitly asks. Before committing, show a visible commit plan with included/excluded files and proposed message.",
            "dirty_tree": "Respect unrelated dirty files and do not revert user changes.",
            "staging": "Never use git add . or git add -A. Stage only explicitly approved files.",
            "pushes": "Never push without separate explicit approval after any commit plan.",
            "release": "Release packaging requires accepted quality or product acceptance, changelog/source changelog policy check, and explicit approval.",
        },
        "json",
    ),
    "project.quality.validation_policy": (
        {
            "default_checks": [
                "For wiki/source docs: 4dt-wiki index build, 4dt-wiki index check, 4dt-wiki validate",
                "For wiki CLI changes: python3 -m unittest discover -s packages/wiki/tests",
                "For workflow/reference/template changes: npm run rules when practical",
                "For board/source/memory/search tool changes: run the affected unittest suite and relevant validate/doctor commands",
            ],
            "known_current_status": "Memory tables live in the shared .4dt/db.sqlite3 SQLite database; 4dt-memory search uses the shared 4dt-search runtime backend.",
            "quality_gate": "Implementation workflows require independent quality before acceptance. Documentation work should verify source backing, status correctness, link integrity, product readability, technical precision, scope control, and safety guarantees.",
        },
        "json",
    ),
    "project.communication.style": (
        {
            "operator_language": "Russian when the operator uses Russian.",
            "style": "Concise, warm, practical. Give short progress updates while working and a compact final summary with checks and changed files.",
            "technical_terms": "Keep commands, filenames, paths, task ids, memory ids, CLI names, and role names exact.",
            "final_answers": "Do not overwhelm; include what changed, validation results, and blockers/open issues.",
        },
        "json",
    ),
}


def response(
    *,
    ok: bool,
    status: str,
    warnings: list[str] | None = None,
    error: dict[str, Any] | None = None,
    **fields: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "status": status,
        **fields,
        "warnings": warnings or [],
    }
    if error is not None:
        payload["error"] = error
    return payload


def error_response(code: str, message: str, status: str | None = None) -> dict[str, Any]:
    return response(
        ok=False,
        status=status or code,
        error={"code": code, "message": message},
    )


def recovery_guidance(status: str) -> list[str]:
    if status == "degraded_setup_required":
        return [
            "Run 4dt-memory init --workspace . --json if storage is not initialized.",
            "Verify with 4dt-memory doctor --workspace . --json.",
        ]
    if status == "schema_mismatch":
        return [
            "Create a shared database backup before changing data.",
            "Recreate a clean database with current tool validation commands.",
            "Compare old and new schemas, then ask the operator to approve a migration plan before moving old data.",
        ]
    return []


def emit(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, sort_keys=True))
        return

    if payload.get("ok") and "jsonl" in payload:
        print(payload["jsonl"], end="" if str(payload["jsonl"]).endswith("\n") else "\n")
        return

    if payload.get("ok"):
        print(payload["status"])
    else:
        error = payload.get("error") or {}
        print(error.get("message", payload["status"]), file=sys.stderr)


def add_common_arguments(parser: argparse.ArgumentParser, *, workspace: bool = True) -> None:
    if workspace:
        parser.add_argument("--workspace", default=".", help="Workspace path.")
    parser.add_argument("--storage-root", help="Explicit storage root for tests/debug/maintenance.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="4dt-memory",
        description="Manage durable 4DreamTeam memory, contract defaults, session state, and recall.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Agent workflow:
  - Use doctor, then defaults load, during startup.
  - Search memory for durable decisions and Wake Context; do not invent missing defaults.
  - Import is dry-run by default; add --apply only after reviewing the import summary.""",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize SQLite-backed memory and default contracts.")
    add_common_arguments(init_parser)

    doctor_parser = subparsers.add_parser("doctor", help="Check memory storage, schema, and search backend health.")
    add_common_arguments(doctor_parser)

    list_parser = subparsers.add_parser("list", help="List durable memory items with optional filters.")
    add_common_arguments(list_parser)
    list_parser.add_argument("--limit", type=int)
    list_parser.add_argument("--scope")
    list_parser.add_argument("--type")
    list_parser.add_argument("--role")

    search_parser = subparsers.add_parser("search", help="Search durable memory items.")
    add_common_arguments(search_parser)
    search_parser.add_argument("query", nargs="?", help="Plain or extended text query.")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum memories to return.")
    search_parser.add_argument("--scope", help="Filter by memory scope.")
    search_parser.add_argument("--type", help="Filter by memory type.")
    search_parser.add_argument("--role", help="Filter by role.")
    search_parser.add_argument("--match", choices=["all", "any"], default="all", help="Require all terms or allow exploratory any-term recall.")
    search_parser.add_argument("--mode", choices=["plain", "extended", "json"], default="plain", help="Query parser mode.")
    search_parser.add_argument("--query-json", help="Inline structured JSON query. Best for generated one-off JSON.")
    search_parser.add_argument("--query-file", help="Structured JSON query file. Use for existing reusable artifacts.")
    search_parser.add_argument("--field", action="append", help="Restrict search fields; repeat for multiple fields.")
    search_parser.add_argument("--explain", action="store_true", help="Include search diagnostics.")
    search_parser.add_argument("--max-candidates", type=int, help="Candidate cap, must be >= --limit.")

    reindex_parser = subparsers.add_parser("reindex", help="Refresh memory search indexes.")
    add_common_arguments(reindex_parser)

    export_parser = subparsers.add_parser("export", help="Export memory rows as JSONL or full memory JSON.")
    add_common_arguments(export_parser)
    export_parser.add_argument("--format", default="jsonl", choices=["jsonl", "json"])
    export_parser.add_argument("--output")

    import_parser = subparsers.add_parser(
        "import",
        help="Import memory JSONL or full JSON. Dry-run by default; add --apply to write.",
        description="Import memory JSONL or full JSON. Dry-run by default; add --apply to write.",
    )
    add_common_arguments(import_parser)
    import_parser.add_argument("input", help="JSONL input file.")
    import_parser.add_argument("--format", default="jsonl", choices=["jsonl", "json"], help="Import format.")
    import_parser.add_argument("--apply", action="store_true", help="Write rows. Without --apply, import only validates and reports dry_run.")

    session_parser = subparsers.add_parser("session", help="Read or write temporary session state.")
    session_subparsers = session_parser.add_subparsers(dest="session_command", required=True)
    session_get = session_subparsers.add_parser("get")
    add_common_arguments(session_get)
    session_get.add_argument("id")
    session_set = session_subparsers.add_parser("set")
    add_common_arguments(session_set)
    session_set.add_argument("id")
    session_set.add_argument("state_json")
    session_set.add_argument("--ttl-seconds", type=int, default=DEFAULT_SESSION_TTL_SECONDS)

    defaults_parser = subparsers.add_parser("defaults", help="Load contract defaults for startup orientation.")
    defaults_subparsers = defaults_parser.add_subparsers(dest="defaults_command", required=True)
    defaults_load = defaults_subparsers.add_parser("load")
    add_common_arguments(defaults_load)

    keys_parser = subparsers.add_parser("keys", help="Manage contract memory keys.")
    keys_subparsers = keys_parser.add_subparsers(dest="keys_command", required=True)
    keys_list = keys_subparsers.add_parser("list")
    add_common_arguments(keys_list)
    keys_list.add_argument("--include-values", action="store_true")
    keys_get = keys_subparsers.add_parser("get")
    add_common_arguments(keys_get)
    keys_get.add_argument("key")
    keys_set = keys_subparsers.add_parser("set")
    add_common_arguments(keys_set)
    keys_set.add_argument("key")
    keys_set.add_argument("--value", required=True)
    keys_delete = keys_subparsers.add_parser("delete")
    add_common_arguments(keys_delete)
    keys_delete.add_argument("key")

    mode_parser = subparsers.add_parser("mode", help="List, read, or set workflow modes.")
    mode_subparsers = mode_parser.add_subparsers(dest="mode_command", required=True)
    mode_list = mode_subparsers.add_parser("list")
    add_common_arguments(mode_list)
    mode_get = mode_subparsers.add_parser("get")
    add_common_arguments(mode_get)
    mode_get.add_argument("mode")
    mode_set_current = mode_subparsers.add_parser("set-current")
    add_common_arguments(mode_set_current)
    mode_set_current.add_argument("mode")

    onboarding_parser = subparsers.add_parser("onboarding", help="Inspect missing contract defaults and suggested questions.")
    onboarding_subparsers = onboarding_parser.add_subparsers(dest="onboarding_command", required=True)
    onboarding_rules = onboarding_subparsers.add_parser("rules")
    add_common_arguments(onboarding_rules)
    onboarding_questions = onboarding_subparsers.add_parser("questions")
    add_common_arguments(onboarding_questions)

    benchmark_parser = subparsers.add_parser("benchmark", help="Run local memory retrieval and performance benchmarks.")
    add_common_arguments(benchmark_parser)
    benchmark_parser.add_argument("--mode", choices=["wiki-only", "memory-only", "memory-plus-wiki"])
    benchmark_parser.add_argument("--profile", choices=["harness", "retrieval-quality"], default="harness")

    get_parser = subparsers.add_parser("get", help="Read one durable memory item by id.")
    add_common_arguments(get_parser)
    get_parser.add_argument("id")

    remember_parser = subparsers.add_parser("remember", help="Save one source-backed durable memory item.")
    add_common_arguments(remember_parser)
    remember_parser.add_argument("content", help="Durable memory content. Keep concise and source-backed.")
    remember_parser.add_argument("--scope", required=True, help="Memory scope, for example workspace or project.")
    remember_parser.add_argument("--type", required=True, help="Memory type, for example decision, preference, or handoff.")
    remember_parser.add_argument("--role", help="Role associated with this memory.")
    remember_parser.add_argument("--source-type", required=True, help="Evidence source type.")
    remember_parser.add_argument("--source-ref", help="Evidence source reference.")
    remember_parser.add_argument("--confidence", type=float, default=0.70, help="Confidence score, defaults to 0.70.")
    remember_parser.add_argument("--metadata-json", help="Inline metadata JSON object.")
    remember_parser.add_argument("--ttl-at", help="Optional expiration timestamp.")

    forget_parser = subparsers.add_parser("forget", help="Retire one durable memory item with an audit reason.")
    add_common_arguments(forget_parser)
    forget_parser.add_argument("id")
    forget_parser.add_argument("--reason", required=True)

    for command in sorted(PLACEHOLDER_COMMANDS):
        placeholder = subparsers.add_parser(command)
        add_common_arguments(placeholder)
        placeholder.add_argument("args", nargs="*")

    return parser


def sqlite_info(sqlite_path: Path) -> tuple[int, bool]:
    connection = sqlite3.connect(sqlite_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        version = schema_version(connection)
        return version, True
    finally:
        connection.close()


def preview_text(item: dict[str, Any], limit: int = 160) -> str:
    text = item.get("summary") or item.get("content") or ""
    compact = " ".join(str(text).split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def search_item_payload(item: dict[str, Any], score: float | None) -> dict[str, Any]:
    return {
        "id": item["id"],
        "score": score,
        "scope": item["scope"],
        "type": item["type"],
        "role": item["role"],
        "preview": preview_text(item),
        "sourceType": item["source_type"],
        "sourceRef": item["source_ref"],
        "confidence": item["confidence"],
        "createdAt": item["created_at"],
    }


def parse_json_object(raw_json: str, *, error_code: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        value = json.loads(raw_json)
    except json.JSONDecodeError:
        return None, error_response(error_code, "Value must be a JSON object.")
    if not isinstance(value, dict):
        return None, error_response(error_code, "Value must be a JSON object.")
    return value, None


def seed_default_contracts(store: MemoryStore) -> list[str]:
    seeded: list[str] = []
    for key in CONTRACT_KEY_ORDER:
        if store.get_contract_entry(key) is not None:
            continue
        value, value_type = DEFAULT_CONTRACT_VALUES[key]
        store.set_contract_entry(key, value, value_type=value_type)
        seeded.append(key)
    return seeded


def load_search_query(args: argparse.Namespace) -> tuple[str | dict[str, Any] | None, dict[str, Any] | None]:
    query_sources = [source for source in (args.query, args.query_json, args.query_file) if source]
    if len(query_sources) != 1:
        return None, error_response("invalid_query", "Search requires exactly one query source.")
    if args.query_file:
        try:
            raw_query = Path(args.query_file).read_text(encoding="utf-8")
        except OSError:
            return None, error_response("query_file_unreadable", "Unable to read query file.")
        if args.mode == "json":
            return parse_json_object(raw_query, error_code="invalid_query_json")
        return raw_query.strip(), None
    if args.query_json:
        return parse_json_object(args.query_json, error_code="invalid_query_json")
    if args.mode == "json":
        return parse_json_object(args.query or "", error_code="invalid_query_json")
    return args.query or "", None


def build_search_options(args: argparse.Namespace) -> tuple[SearchOptions | None, dict[str, Any] | None]:
    if args.max_candidates is not None and args.max_candidates < 1:
        return None, error_response("invalid_max_candidates", "Max candidates must be greater than zero.")
    try:
        fields = normalize_memory_fields(args.field)
    except ValueError as exc:
        return None, error_response("invalid_search_field", str(exc))
    return SearchOptions(
        mode=args.mode,
        match=args.match,
        fields=fields,
        max_candidates=args.max_candidates,
        explain=args.explain,
    ), None


def handle_init(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        seeded_contracts = seed_default_contracts(store)
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            storageRoot=str(store.paths.storage_root),
            sqlitePath=str(store.paths.sqlite_path),
            schemaVersion=store.schema_version(),
            seededContracts=seeded_contracts,
        )
    except SchemaMismatch as exc:
        return EXIT_STORAGE, error_response("schema_mismatch", str(exc), status="schema_mismatch")
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to initialize memory storage.")
    finally:
        store.close()


def handle_doctor(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    identity = workspace_identity(args.workspace)
    paths = workspace_paths(args.workspace, args.storage_root)
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        version = store.schema_version()
        rows = store.list_live_memory_items()
    except SchemaMismatch as exc:
        store.close()
        return EXIT_STORAGE, response(
            ok=False,
            status="schema_mismatch",
            workspaceId=identity.id,
            storageRoot=str(paths.storage_root),
            sqlitePath=str(paths.sqlite_path),
            sqlite={"ok": False, "path": str(paths.sqlite_path), "schemaVersion": None},
            warnings=["memory_schema_mismatch"],
            recovery=recovery_guidance("schema_mismatch"),
            error={"code": "schema_mismatch", "message": str(exc)},
        )
    except sqlite3.Error:
        store.close()
        return EXIT_STORAGE, response(
            ok=False,
            status="storage_error",
            workspaceId=identity.id,
            storageRoot=str(paths.storage_root),
            sqlitePath=str(paths.sqlite_path),
            sqlite={"ok": False, "path": str(paths.sqlite_path), "schemaVersion": None},
            warnings=["sqlite_unreadable"],
        )
    finally:
        store.close()
    try:
        _version, sqlite_ok = sqlite_info(paths.sqlite_path)
    except sqlite3.Error:
        sqlite_ok = False

    return EXIT_OK, response(
        ok=True,
        status="ready",
        workspaceId=identity.id,
        storageRoot=str(paths.storage_root),
        sqlitePath=str(paths.sqlite_path),
        sqlite={"ok": sqlite_ok, "path": str(paths.sqlite_path), "schemaVersion": version},
        memory={"ok": True, "liveItems": len(rows), "searchBackend": "4dt-search"},
        warnings=[],
        recovery=[],
    )


def open_existing_store(args: argparse.Namespace) -> tuple[MemoryStore | None, dict[str, Any] | None, int]:
    paths = workspace_paths(args.workspace, args.storage_root)
    if not paths.sqlite_path.exists():
        status = "degraded_setup_required"
        return (
            None,
            response(
                ok=False,
                status=status,
                error={"code": "not_initialized", "message": "Memory store is not initialized."},
                storageRoot=str(paths.storage_root),
                sqlitePath=str(paths.sqlite_path),
                recovery=recovery_guidance(status),
            ),
            EXIT_DEGRADED,
        )

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        connection = store.connect()
        ensure_current_schema(connection)
        return store, None, EXIT_OK
    except SchemaMismatch as exc:
        store.close()
        return None, error_response("schema_mismatch", str(exc), status="schema_mismatch"), EXIT_STORAGE
    except sqlite3.Error:
        store.close()
        return None, error_response("storage_error", "Unable to open memory storage."), EXIT_STORAGE


def handle_list(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        items = store.list_live_memory_items(scope=args.scope, type=args.type, role=args.role)
        if args.limit is not None:
            items = items[: args.limit]
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            items=items,
        )
    finally:
        store.close()


def handle_get(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        item = store.get_memory_item(args.id)
        if item is None:
            return EXIT_USER_CONFIG, error_response("not_found", "Memory item was not found.")
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            item=item,
        )
    finally:
        store.close()


def handle_search(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.limit is not None and args.limit < 1:
        return EXIT_USER_CONFIG, error_response("invalid_limit", "Search limit must be greater than zero.")
    query, query_error = load_search_query(args)
    if query_error is not None or query is None:
        return EXIT_USER_CONFIG, query_error or error_response("invalid_query", "Search query is invalid.")
    options, options_error = build_search_options(args)
    if options_error is not None or options is None:
        return EXIT_USER_CONFIG, options_error or error_response("invalid_search_options", "Search options are invalid.")

    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        rows = store.list_live_memory_items(scope=args.scope, type=args.type, role=args.role)
        scored_rows, explain = search_memory_rows(query, rows, limit=args.limit, options=options)
        items = [search_item_payload(row, score) for score, row in scored_rows]
        payload = response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            query=query,
            queryText=query_text(query),
            items=items,
            warnings=[],
            recovery=[],
        )
        if args.explain:
            payload["explain"] = explain
        return EXIT_OK, payload
    finally:
        store.close()


def handle_reindex(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        rows = store.list_live_memory_items()
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            checkedItems=len(rows),
            searchBackend="4dt-search",
            warnings=[],
            recovery=[],
        )
    finally:
        store.close()


def validate_memory_fields(
    *,
    content: str,
    scope: str,
    source_type: str | None,
    source_ref: str | None,
    confidence: float,
    metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, int]:
    durable_scopes = {"workspace", "project", "role", "user"}
    source_ref_required_scopes = {"workspace", "project", "role"}

    if scope not in durable_scopes:
        return error_response("unsupported_scope", "Memory scope is not supported for durable storage."), EXIT_USER_CONFIG

    if not source_type:
        return error_response("missing_source_type", "Durable memories require source-type."), EXIT_USER_CONFIG

    if scope in source_ref_required_scopes and not source_ref:
        return error_response("missing_source_ref", "Durable workspace, project, and role memories require source-ref."), EXIT_USER_CONFIG

    if scope == "user" and source_type != "user" and not source_ref:
        return error_response("missing_source_ref", "User memories without file evidence require source-type user."), EXIT_USER_CONFIG

    if not 0 <= confidence <= 1:
        return error_response("invalid_confidence", "Confidence must be between 0 and 1."), EXIT_USER_CONFIG

    safety = check_memory_content(content, durable=True)
    if not safety.ok:
        return response(
            ok=False,
            status="unsafe_save_blocked",
            error={
                "code": "unsafe_save_blocked",
                "message": "Memory content was blocked by safety checks.",
                "reasons": [issue.code for issue in safety.issues],
            },
        ), EXIT_UNSAFE_SAVE

    return {"metadata": metadata or {}}, EXIT_OK


def parse_metadata(raw_metadata: str | None) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if raw_metadata is None:
        return {}, None
    try:
        metadata = json.loads(raw_metadata)
    except json.JSONDecodeError:
        return None, error_response("invalid_metadata_json", "Metadata must be a JSON object.")
    if not isinstance(metadata, dict):
        return None, error_response("invalid_metadata_json", "Metadata must be a JSON object.")
    return metadata, None


def contract_key_meta(key: str) -> dict[str, Any]:
    return {
        "key": key,
        "description": CONTRACT_KEYS[key],
        "required": True,
    }


def validate_contract_key(key: str) -> dict[str, Any] | None:
    if key in CONTRACT_KEYS:
        return None
    return error_response("invalid_key", f"Unsupported contract key: {key}.")


def parse_contract_value(raw_value: str) -> tuple[Any, str]:
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value.strip(), "text"
    return value, "json"


def contract_content_for_safety(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def validate_contract_value(key: str, value: Any) -> dict[str, Any] | None:
    if key == "project.workflow.current_mode":
        if not isinstance(value, str) or not value.strip():
            return error_response("invalid_value", "Current mode must be a non-empty string.")
    if key == "project.workflow.modes":
        if not isinstance(value, dict):
            return error_response("invalid_value", "Workflow modes must be a JSON object.")
        for mode_name, definition in value.items():
            if not isinstance(mode_name, str) or not mode_name.strip():
                return error_response("invalid_value", "Workflow mode names must be non-empty strings.")
            if not isinstance(definition, dict):
                return error_response("invalid_value", "Each workflow mode definition must be a JSON object.")
            missing_fields = sorted(MODE_DEFINITION_FIELDS - set(definition))
            if missing_fields:
                return response(
                    ok=False,
                    status="invalid_value",
                    error={
                        "code": "invalid_value",
                        "message": "Workflow mode definitions must include the fixed mode contract fields.",
                        "mode": mode_name,
                        "missingFields": missing_fields,
                    },
                )

    safety = check_memory_content(contract_content_for_safety(value), durable=True)
    if not safety.ok:
        return response(
            ok=False,
            status="unsafe_save_blocked",
            error={
                "code": "unsafe_save_blocked",
                "message": "Contract memory content was blocked by safety checks.",
                "reasons": [issue.code for issue in safety.issues],
            },
        )
    return None


def contract_entry_payload(entry: dict[str, Any] | None) -> dict[str, Any] | None:
    if entry is None:
        return None
    return {
        "key": entry["key"],
        "value": entry["value"],
        "valueType": entry["value_type"],
        "createdAt": entry["created_at"],
        "updatedAt": entry["updated_at"],
    }


def contract_entry_write_payload(entry: dict[str, Any]) -> dict[str, Any]:
    value = entry["value"]
    raw_value = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=False)
    return {
        "key": entry["key"],
        "valueType": entry["value_type"],
        "valueBytes": len(raw_value.encode("utf-8")),
        "createdAt": entry["created_at"],
        "updatedAt": entry["updated_at"],
    }


def contract_key_state(store: MemoryStore, key: str, *, include_value: bool = True) -> dict[str, Any]:
    entry = store.get_contract_entry(key)
    state = {
        **contract_key_meta(key),
        "configured": entry is not None,
        "missing": entry is None,
    }
    if include_value:
        state["entry"] = contract_entry_payload(entry)
    return state


def workflow_modes(store: MemoryStore) -> tuple[dict[str, Any], list[str]]:
    entry = store.get_contract_entry("project.workflow.modes")
    if entry is None:
        return {}, ["workflow_modes_missing"]
    value = entry["value"]
    if not isinstance(value, dict):
        return {}, ["workflow_modes_invalid"]
    return value, []


def onboarding_questions_for(missing_keys: list[str], warnings: list[str]) -> list[dict[str, str]]:
    questions = [
        {"key": key, "question": ONBOARDING_QUESTIONS[key]}
        for key in missing_keys
        if key in ONBOARDING_QUESTIONS
    ]
    if "current_mode_undefined" in warnings:
        questions.append(
            {
                "key": "project.workflow.current_mode",
                "question": "The current mode is not defined in project.workflow.modes. What should this mode allow and require?",
            }
        )
    if "current_mode_missing" in warnings and "project.workflow.current_mode" not in missing_keys:
        questions.append(
            {
                "key": "project.workflow.current_mode",
                "question": ONBOARDING_QUESTIONS["project.workflow.current_mode"],
            }
        )
    return questions


def validate_remember_args(args: argparse.Namespace) -> tuple[dict[str, Any] | None, int]:
    metadata, metadata_error = parse_metadata(args.metadata_json)
    if metadata_error is not None:
        return metadata_error, EXIT_USER_CONFIG
    return validate_memory_fields(
        content=args.content,
        scope=args.scope,
        source_type=args.source_type,
        source_ref=args.source_ref,
        confidence=args.confidence,
        metadata=metadata,
    )


def handle_remember(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    validation, exit_code = validate_remember_args(args)
    if exit_code != EXIT_OK:
        return exit_code, validation or error_response("invalid_memory", "Memory could not be saved.")

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        memory_id = store.create_memory_item(
            scope=args.scope,
            type=args.type,
            role=args.role,
            content=args.content.strip(),
            metadata=validation.get("metadata") if validation else {},
            confidence=args.confidence,
            source_type=args.source_type,
            source_ref=args.source_ref,
            ttl_at=args.ttl_at,
        )
        evidence_id = store.add_evidence(
            memory_id,
            source_type=args.source_type,
            source_ref=args.source_ref,
        )
        item = store.get_memory_item(memory_id)
        if item is None:
            return EXIT_STORAGE, error_response("storage_error", "Memory was saved but could not be read back.")
        return EXIT_OK, response(
            ok=True,
            status="remembered",
            workspaceId=store.identity.id,
            id=memory_id,
            scope=item["scope"],
            type=item["type"],
            role=item["role"],
            sourceType=item["source_type"],
            sourceRef=item["source_ref"],
            confidence=item["confidence"],
            createdAt=item["created_at"],
            evidenceId=evidence_id,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to save memory.")
    finally:
        store.close()


def handle_forget(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if not args.reason.strip():
        return EXIT_USER_CONFIG, error_response("missing_reason", "Forget requires a non-empty reason.")

    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        deleted = store.soft_delete_memory_item(args.id, args.reason.strip())
        if not deleted:
            return EXIT_USER_CONFIG, error_response("not_found", "Memory item was not found.")
        return EXIT_OK, response(
            ok=True,
            status="forgotten",
            workspaceId=store.identity.id,
            id=args.id,
            deleted=True,
        )
    finally:
        store.close()


def handle_export(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        if args.format == "json":
            connection = store.connect()
            tables = (
                "memory_items",
                "memory_evidence",
                "memory_agent_sessions",
                "memory_audit_log",
                "memory_contract_entries",
            )
            data = {
                "schemaVersion": store.schema_version(),
                "generatedAt": utc_now(),
                "tables": {
                    table: [dict(row) for row in connection.execute(f"SELECT * FROM {table}").fetchall()]
                    for table in tables
                },
            }
            raw_json = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            if args.output:
                Path(args.output).write_text(raw_json, encoding="utf-8")
            store.audit("export", payload={"format": args.format, "tables": list(tables)})
            return EXIT_OK, response(
                ok=True,
                status="exported",
                workspaceId=store.identity.id,
                format=args.format,
                output=args.output,
                json=None if args.output else data,
                warnings=["export_contains_sensitive_accepted_memory"],
            )
        rows = store.live_memory_export_rows()
        jsonl = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
        if args.output:
            Path(args.output).write_text(jsonl, encoding="utf-8")
        store.audit("export", payload={"format": args.format, "count": len(rows)})
        return EXIT_OK, response(
            ok=True,
            status="exported",
            workspaceId=store.identity.id,
            format=args.format,
            count=len(rows),
            output=args.output,
            jsonl=None if args.output else jsonl,
            warnings=["export_contains_sensitive_accepted_memory"],
        )
    except (OSError, sqlite3.Error):
        return EXIT_STORAGE, error_response("storage_error", "Unable to export memory.")
    finally:
        store.close()


def normalized_import_record(record: dict[str, Any]) -> dict[str, Any]:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    return {
        "scope": record.get("scope"),
        "type": record.get("type"),
        "role": record.get("role"),
        "content": record.get("content"),
        "summary": record.get("summary"),
        "metadata": metadata,
        "confidence": record.get("confidence", 0.70),
        "source_type": record.get("sourceType") or record.get("source_type"),
        "source_ref": record.get("sourceRef") or record.get("source_ref"),
        "ttl_at": record.get("ttlAt") or record.get("ttl_at"),
    }


def validate_import_jsonl(raw_jsonl: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    unsafe = False
    for index, line in enumerate(raw_jsonl.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw_record = json.loads(line)
        except json.JSONDecodeError:
            errors.append({"line": index, "code": "invalid_json", "message": "Line is not valid JSON."})
            continue
        if not isinstance(raw_record, dict):
            errors.append({"line": index, "code": "invalid_record", "message": "Line must be a JSON object."})
            continue
        record = normalized_import_record(raw_record)
        if not isinstance(record["content"], str) or not isinstance(record["scope"], str) or not isinstance(record["type"], str):
            errors.append({"line": index, "code": "invalid_record", "message": "Required memory fields are missing."})
            continue
        if record["role"] is not None and not isinstance(record["role"], str):
            errors.append({"line": index, "code": "invalid_record", "message": "Role must be a string."})
            continue
        try:
            confidence = float(record["confidence"])
        except (TypeError, ValueError):
            errors.append({"line": index, "code": "invalid_confidence", "message": "Confidence must be a number."})
            continue
        record["confidence"] = confidence
        validation, validation_exit = validate_memory_fields(
            content=record["content"],
            scope=record["scope"],
            source_type=record["source_type"],
            source_ref=record["source_ref"],
            confidence=record["confidence"],
            metadata=record["metadata"],
        )
        if validation_exit != EXIT_OK:
            error = validation.get("error", {}) if validation else {}
            errors.append(
                {
                    "line": index,
                    "code": error.get("code", "invalid_memory"),
                    "message": error.get("message", "Memory row is invalid."),
                    "reasons": error.get("reasons", []),
                }
            )
            if validation_exit == EXIT_UNSAFE_SAVE:
                unsafe = True
            continue
        records.append(record)
    return records, errors, unsafe


def handle_import(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    try:
        raw_input = Path(args.input).read_text(encoding="utf-8")
    except OSError:
        return EXIT_USER_CONFIG, error_response("input_not_found", "Import input could not be read.")

    if args.format == "json":
        try:
            data = json.loads(raw_input)
        except json.JSONDecodeError:
            return EXIT_USER_CONFIG, error_response("invalid_import", "Memory JSON import input is invalid.")
        tables = data.get("tables") if isinstance(data, dict) else None
        expected_tables = (
            "memory_items",
            "memory_evidence",
            "memory_agent_sessions",
            "memory_audit_log",
            "memory_contract_entries",
        )
        if not isinstance(tables, dict) or any(not isinstance(tables.get(table), list) for table in expected_tables):
            return EXIT_USER_CONFIG, error_response("invalid_import", "Memory JSON import must contain all memory tables.")
        row_count = sum(len(tables[table]) for table in expected_tables)
        if not args.apply:
            return EXIT_OK, response(ok=True, status="dry_run", format=args.format, apply=False, validRecords=row_count, written=0)
        store = MemoryStore(args.workspace, args.storage_root)
        try:
            store.initialize()
            connection = store.connect()
            connection.execute("BEGIN IMMEDIATE")
            for table in reversed(expected_tables):
                connection.execute(f"DELETE FROM {table}")
            columns = {
                "memory_items": (
                    "id",
                    "scope",
                    "type",
                    "role",
                    "content",
                    "summary",
                    "metadata_json",
                    "confidence",
                    "source_type",
                    "source_ref",
                    "evidence_hash",
                    "ttl_at",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
                "memory_evidence": ("id", "memory_id", "source_type", "source_ref", "quote_hash", "created_at"),
                "memory_agent_sessions": ("id", "state_json", "created_at", "updated_at"),
                "memory_audit_log": ("id", "action", "memory_id", "payload_json", "created_at"),
                "memory_contract_entries": ("key", "value_json", "value_type", "created_at", "updated_at"),
            }
            for table in expected_tables:
                table_columns = columns[table]
                placeholders = ", ".join("?" for _ in table_columns)
                connection.executemany(
                    f"INSERT INTO {table} ({', '.join(table_columns)}) VALUES ({placeholders})",
                    [tuple(row.get(column) for column in table_columns) for row in tables[table]],
                )
            connection.commit()
            return EXIT_OK, response(ok=True, status="imported", format=args.format, apply=True, written=row_count)
        except sqlite3.Error:
            store.connect().rollback()
            return EXIT_STORAGE, error_response("storage_error", "Unable to import memory.")
        finally:
            store.close()

    raw_jsonl = raw_input
    records, errors, unsafe = validate_import_jsonl(raw_jsonl)
    if errors:
        return_code = EXIT_UNSAFE_SAVE if unsafe else EXIT_USER_CONFIG
        return return_code, response(
            ok=False,
            status="import_rejected",
            format=args.format,
            apply=args.apply,
            validRecords=len(records),
            errors=errors,
        )

    if not args.apply:
        return EXIT_OK, response(
            ok=True,
            status="dry_run",
            format=args.format,
            apply=False,
            validRecords=len(records),
            written=0,
        )

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        written_ids: list[str] = []
        for record in records:
            memory_id = store.create_memory_item(
                scope=record["scope"],
                type=record["type"],
                role=record["role"],
                content=record["content"].strip(),
                summary=record["summary"] if isinstance(record["summary"], str) else None,
                metadata=record["metadata"],
                confidence=record["confidence"],
                source_type=record["source_type"],
                source_ref=record["source_ref"],
                ttl_at=record["ttl_at"] if isinstance(record["ttl_at"], str) else None,
            )
            store.add_evidence(memory_id, source_type=record["source_type"], source_ref=record["source_ref"])
            written_ids.append(memory_id)
        store.audit("import", payload={"format": args.format, "count": len(written_ids)})
        return EXIT_OK, response(
            ok=True,
            status="imported",
            workspaceId=store.identity.id,
            format=args.format,
            apply=True,
            written=len(written_ids),
            ids=written_ids,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to import memory.")
    finally:
        store.close()


def handle_session_get(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")
    try:
        record = store.get_session_record(args.id)
        if record is None:
            return EXIT_USER_CONFIG, error_response("not_found", "Session state was not found.")
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            id=args.id,
            state=record["state"],
            expiresAt=record["expiresAt"],
        )
    finally:
        store.close()


def handle_session_set(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if len(args.state_json.encode("utf-8")) > SESSION_STATE_MAX_BYTES:
        return EXIT_USER_CONFIG, error_response("session_too_large", "Session state exceeds the size limit.")
    if args.ttl_seconds < 1:
        return EXIT_USER_CONFIG, error_response("invalid_ttl", "Session TTL must be greater than zero.")
    state, state_error = parse_json_object(args.state_json, error_code="invalid_session_json")
    if state_error is not None or state is None:
        return EXIT_USER_CONFIG, state_error or error_response("invalid_session_json", "Session state must be JSON.")

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        expires_at = store.set_session_record(args.id, state, ttl_seconds=args.ttl_seconds)
        return EXIT_OK, response(
            ok=True,
            status="session_saved",
            workspaceId=store.identity.id,
            id=args.id,
            expiresAt=expires_at,
            sizeBytes=len(args.state_json.encode("utf-8")),
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to save session state.")
    finally:
        store.close()


def handle_keys_list(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        keys = [contract_key_state(store, key, include_value=args.include_values) for key in CONTRACT_KEY_ORDER]
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            keys=keys,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to list contract keys.")
    finally:
        store.close()


def handle_defaults_load(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        data = onboarding_rules_payload(store)
        incomplete = bool(data["warnings"])
        return EXIT_OK, response(
            ok=True,
            status="defaults_incomplete" if incomplete else "ready",
            workspaceId=store.identity.id,
            onboardingRequired=incomplete,
            onboardingCommand="4dt-memory onboarding questions --workspace . --json" if incomplete else None,
            **data,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to load memory defaults.")
    finally:
        store.close()


def handle_keys_get(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    invalid_key = validate_contract_key(args.key)
    if invalid_key is not None:
        return EXIT_USER_CONFIG, invalid_key

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        state = contract_key_state(store, args.key, include_value=True)
        return EXIT_OK, response(
            ok=True,
            status="missing" if state["missing"] else "ready",
            workspaceId=store.identity.id,
            key=state,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to read contract key.")
    finally:
        store.close()


def handle_keys_set(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    invalid_key = validate_contract_key(args.key)
    if invalid_key is not None:
        return EXIT_USER_CONFIG, invalid_key
    value, value_type = parse_contract_value(args.value)
    invalid_value = validate_contract_value(args.key, value)
    if invalid_value is not None:
        exit_code = EXIT_UNSAFE_SAVE if invalid_value.get("status") == "unsafe_save_blocked" else EXIT_USER_CONFIG
        return exit_code, invalid_value

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        entry = store.set_contract_entry(args.key, value, value_type=value_type)
        return EXIT_OK, response(
            ok=True,
            status="contract_saved",
            workspaceId=store.identity.id,
            key=contract_entry_write_payload(entry),
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to save contract key.")
    finally:
        store.close()


def handle_keys_delete(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    invalid_key = validate_contract_key(args.key)
    if invalid_key is not None:
        return EXIT_USER_CONFIG, invalid_key

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        deleted = store.delete_contract_entry(args.key)
        return EXIT_OK, response(
            ok=True,
            status="contract_deleted" if deleted else "missing",
            workspaceId=store.identity.id,
            key=args.key,
            deleted=deleted,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to delete contract key.")
    finally:
        store.close()


def handle_mode_list(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        modes, warnings = workflow_modes(store)
        current_entry = store.get_contract_entry("project.workflow.current_mode")
        current_mode = current_entry["value"] if current_entry and isinstance(current_entry["value"], str) else None
        return EXIT_OK, response(
            ok=True,
            status="ready" if not warnings else "missing",
            workspaceId=store.identity.id,
            currentMode=current_mode,
            modes=[{"name": name, "definition": definition} for name, definition in sorted(modes.items())],
            warnings=warnings,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to list workflow modes.")
    finally:
        store.close()


def handle_mode_get(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        modes, warnings = workflow_modes(store)
        definition = modes.get(args.mode)
        return EXIT_OK, response(
            ok=True,
            status="ready" if definition is not None else "missing",
            workspaceId=store.identity.id,
            mode=args.mode,
            defined=definition is not None,
            definition=definition,
            warnings=warnings,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to read workflow mode.")
    finally:
        store.close()


def handle_mode_set_current(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        modes, warnings = workflow_modes(store)
        definition = modes.get(args.mode)
        if definition is None:
            return EXIT_USER_CONFIG, response(
                ok=False,
                status="undefined_mode",
                workspaceId=store.identity.id,
                mode=args.mode,
                warnings=[*warnings, "current_mode_undefined"],
                questions=onboarding_questions_for([], ["current_mode_undefined"]),
                error={
                    "code": "undefined_mode",
                    "message": "Workflow mode is not defined. Define it in project.workflow.modes before setting it current.",
                },
            )
        entry = store.set_contract_entry("project.workflow.current_mode", args.mode, value_type="text")
        return EXIT_OK, response(
            ok=True,
            status="current_mode_set",
            workspaceId=store.identity.id,
            currentMode=args.mode,
            definition=definition,
            key=contract_entry_payload(entry),
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to set current workflow mode.")
    finally:
        store.close()


def onboarding_rules_payload(store: MemoryStore) -> dict[str, Any]:
    keys = [contract_key_state(store, key, include_value=True) for key in CONTRACT_KEY_ORDER]
    missing_keys = [item["key"] for item in keys if item["missing"]]
    warnings: list[str] = []
    if missing_keys:
        warnings.append("contract_keys_missing")

    modes, mode_warnings = workflow_modes(store)
    warnings.extend(mode_warnings)
    current_entry = store.get_contract_entry("project.workflow.current_mode")
    current_mode = current_entry["value"] if current_entry and isinstance(current_entry["value"], str) else None
    if current_mode is None:
        warnings.append("current_mode_missing")
    current_definition = modes.get(current_mode) if current_mode else None
    if current_mode and current_definition is None:
        warnings.append("current_mode_undefined")

    return {
        "keys": keys,
        "missingKeys": missing_keys,
        "currentMode": current_mode,
        "currentModeDefinition": current_definition,
        "modeDefinitionFields": sorted(MODE_DEFINITION_FIELDS),
        "questions": onboarding_questions_for(missing_keys, warnings),
        "warnings": warnings,
    }


def handle_onboarding_rules(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        data = onboarding_rules_payload(store)
        status = "ready" if not data["warnings"] else "missing_contract"
        return EXIT_OK, response(
            ok=True,
            status=status,
            workspaceId=store.identity.id,
            **data,
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to read onboarding rules.")
    finally:
        store.close()


def handle_onboarding_questions(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        data = onboarding_rules_payload(store)
        return EXIT_OK, response(
            ok=True,
            status="ready" if not data["questions"] else "questions_available",
            workspaceId=store.identity.id,
            questions=data["questions"],
            missingKeys=data["missingKeys"],
            currentMode=data["currentMode"],
            warnings=data["warnings"],
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to build onboarding questions.")
    finally:
        store.close()


def handle_benchmark(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.profile == "retrieval-quality":
        return EXIT_OK, response(
            ok=True,
            status="benchmark_complete",
            workspaceId=workspace_identity(args.workspace).id,
            **retrieval_quality_benchmark(),
        )

    modes = [args.mode] if args.mode else ["wiki-only", "memory-only", "memory-plus-wiki"]
    metrics = [
        "correctness",
        "completeness",
        "irrelevantStaleRecalls",
        "filesRead",
        "latencyMs",
        "safety",
    ]
    return EXIT_OK, response(
        ok=True,
        status="benchmark_harness",
        workspaceId=workspace_identity(args.workspace).id,
        modes=[
            {
                "mode": mode,
                "metrics": {metric: None for metric in metrics},
            }
            for mode in modes
        ],
        seedFromWiki="deferred",
        sourceBoundary="does_not_read_sources",
    )


def handle_placeholder(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    return EXIT_USER_CONFIG, error_response(
        "not_implemented",
        "Command is not implemented in this build.",
        status="not_implemented",
    )


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.command == "init":
        return handle_init(args)
    if args.command == "doctor":
        return handle_doctor(args)
    if args.command == "list":
        return handle_list(args)
    if args.command == "search":
        return handle_search(args)
    if args.command == "reindex":
        return handle_reindex(args)
    if args.command == "get":
        return handle_get(args)
    if args.command == "remember":
        return handle_remember(args)
    if args.command == "forget":
        return handle_forget(args)
    if args.command == "export":
        return handle_export(args)
    if args.command == "import":
        return handle_import(args)
    if args.command == "session" and args.session_command == "get":
        return handle_session_get(args)
    if args.command == "session" and args.session_command == "set":
        return handle_session_set(args)
    if args.command == "defaults" and args.defaults_command == "load":
        return handle_defaults_load(args)
    if args.command == "keys" and args.keys_command == "list":
        return handle_keys_list(args)
    if args.command == "keys" and args.keys_command == "get":
        return handle_keys_get(args)
    if args.command == "keys" and args.keys_command == "set":
        return handle_keys_set(args)
    if args.command == "keys" and args.keys_command == "delete":
        return handle_keys_delete(args)
    if args.command == "mode" and args.mode_command == "list":
        return handle_mode_list(args)
    if args.command == "mode" and args.mode_command == "get":
        return handle_mode_get(args)
    if args.command == "mode" and args.mode_command == "set-current":
        return handle_mode_set_current(args)
    if args.command == "onboarding" and args.onboarding_command == "rules":
        return handle_onboarding_rules(args)
    if args.command == "onboarding" and args.onboarding_command == "questions":
        return handle_onboarding_questions(args)
    if args.command == "benchmark":
        return handle_benchmark(args)
    if args.command in PLACEHOLDER_COMMANDS:
        return handle_placeholder(args)
    return EXIT_USER_CONFIG, error_response("unknown_command", "Unknown command.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code, payload = run(args)
    emit(payload, bool(getattr(args, "json", False)))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
