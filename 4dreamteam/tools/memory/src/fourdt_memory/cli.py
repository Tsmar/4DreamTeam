from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Sequence

from .embedder import cosine_similarity, lexical_score, provider_from_args, provider_key
from .lance_index import LanceIndex
from .migrations import migrate, schema_version
from .paths import workspace_identity, workspace_paths
from .redaction import check_memory_content
from .sqlite_store import MemoryStore


EXIT_OK = 0
EXIT_USER_CONFIG = 1
EXIT_STORAGE = 2
EXIT_DEGRADED = 3
EXIT_UNSAFE_SAVE = 4

PLACEHOLDER_COMMANDS = {
    "export",
    "import",
    "session",
    "benchmark",
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


def emit(payload: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, sort_keys=True))
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
    parser = argparse.ArgumentParser(prog="4dt-memory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    add_common_arguments(init_parser)

    doctor_parser = subparsers.add_parser("doctor")
    add_common_arguments(doctor_parser)

    list_parser = subparsers.add_parser("list")
    add_common_arguments(list_parser)
    list_parser.add_argument("--limit", type=int)
    list_parser.add_argument("--scope")
    list_parser.add_argument("--type")
    list_parser.add_argument("--role")

    search_parser = subparsers.add_parser("search")
    add_common_arguments(search_parser)
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.add_argument("--scope")
    search_parser.add_argument("--type")
    search_parser.add_argument("--role")
    search_parser.add_argument("--embedding-provider", default="none", choices=["none", "hash"])
    search_parser.add_argument("--embedding-model")

    reindex_parser = subparsers.add_parser("reindex")
    add_common_arguments(reindex_parser)
    reindex_parser.add_argument("--embedding-provider", default="none", choices=["none", "hash"])
    reindex_parser.add_argument("--embedding-model")

    get_parser = subparsers.add_parser("get")
    add_common_arguments(get_parser)
    get_parser.add_argument("id")

    remember_parser = subparsers.add_parser("remember")
    add_common_arguments(remember_parser)
    remember_parser.add_argument("content")
    remember_parser.add_argument("--scope", required=True)
    remember_parser.add_argument("--type", required=True)
    remember_parser.add_argument("--role")
    remember_parser.add_argument("--source-type", required=True)
    remember_parser.add_argument("--source-ref")
    remember_parser.add_argument("--confidence", type=float, default=0.70)
    remember_parser.add_argument("--metadata-json")
    remember_parser.add_argument("--ttl-at")

    forget_parser = subparsers.add_parser("forget")
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


def index_report(store: MemoryStore) -> dict[str, Any]:
    index = LanceIndex(store.paths.lancedb_dir)
    live_ids = set(store.list_live_memory_ids())
    indexed_ids = set(index.ids())
    missing_sqlite_ids = sorted(indexed_ids - live_ids)
    rows = store.list_live_memory_items()
    sqlite_indexed = [row for row in rows if row.get("indexed_at") is not None]
    warnings: list[str] = []
    if not index.available:
        warnings.append("semantic_index_unavailable")
    if missing_sqlite_ids:
        warnings.append("index_missing_sqlite_rows")
    if indexed_ids and len(indexed_ids & live_ids) != len(sqlite_indexed):
        warnings.append("indexed_item_count_mismatch")
    data = index.read()
    if data.get("corrupt"):
        warnings.append("semantic_index_corrupt")
    return {
        "ok": index.available and not warnings,
        "path": str(store.paths.lancedb_dir),
        "available": index.available,
        "indexedItems": len(indexed_ids) if indexed_ids else len(sqlite_indexed),
        "sqliteIndexedItems": len(sqlite_indexed),
        "providerModel": data.get("providerModel"),
        "missingSqliteIds": missing_sqlite_ids,
        "warnings": warnings,
    }


def handle_init(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store = MemoryStore(args.workspace, args.storage_root)
    try:
        store.initialize()
        return EXIT_OK, response(
            ok=True,
            status="ready",
            workspaceId=store.identity.id,
            storageRoot=str(store.paths.storage_root),
            sqlitePath=str(store.paths.sqlite_path),
            schemaVersion=store.schema_version(),
        )
    except sqlite3.Error:
        return EXIT_STORAGE, error_response("storage_error", "Unable to initialize memory storage.")
    finally:
        store.close()


def handle_doctor(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    identity = workspace_identity(args.workspace)
    paths = workspace_paths(args.workspace, args.storage_root)
    if not paths.sqlite_path.exists():
        return EXIT_DEGRADED, response(
            ok=False,
            status="not_initialized",
            workspaceId=identity.id,
            storageRoot=str(paths.storage_root),
            sqlitePath=str(paths.sqlite_path),
            sqlite={"ok": False, "path": str(paths.sqlite_path), "schemaVersion": None},
            lancedb={"ok": False, "path": str(paths.lancedb_dir), "indexedItems": None},
            warnings=["memory_store_not_initialized"],
        )

    try:
        version, sqlite_ok = sqlite_info(paths.sqlite_path)
    except sqlite3.Error:
        return EXIT_STORAGE, response(
            ok=False,
            status="storage_error",
            workspaceId=identity.id,
            storageRoot=str(paths.storage_root),
            sqlitePath=str(paths.sqlite_path),
            sqlite={"ok": False, "path": str(paths.sqlite_path), "schemaVersion": None},
            lancedb={"ok": False, "path": str(paths.lancedb_dir), "indexedItems": None},
            warnings=["sqlite_unreadable"],
        )

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        connection = store.connect()
        migrate(connection)
        lancedb = index_report(store)
    except sqlite3.Error:
        store.close()
        return EXIT_STORAGE, response(
            ok=False,
            status="storage_error",
            workspaceId=identity.id,
            storageRoot=str(paths.storage_root),
            sqlitePath=str(paths.sqlite_path),
            sqlite={"ok": False, "path": str(paths.sqlite_path), "schemaVersion": None},
            lancedb={"ok": False, "path": str(paths.lancedb_dir), "indexedItems": None},
            warnings=["sqlite_unreadable"],
        )
    finally:
        store.close()

    warnings = lancedb.pop("warnings")
    status = "ready" if not warnings else "degraded"
    exit_code = EXIT_OK if not warnings else EXIT_DEGRADED
    return exit_code, response(
        ok=True,
        status=status,
        workspaceId=identity.id,
        storageRoot=str(paths.storage_root),
        sqlitePath=str(paths.sqlite_path),
        sqlite={"ok": sqlite_ok, "path": str(paths.sqlite_path), "schemaVersion": version},
        lancedb=lancedb,
        warnings=warnings,
    )


def open_existing_store(args: argparse.Namespace) -> tuple[MemoryStore | None, dict[str, Any] | None, int]:
    paths = workspace_paths(args.workspace, args.storage_root)
    if not paths.sqlite_path.exists():
        return None, error_response("not_initialized", "Memory store is not initialized."), EXIT_DEGRADED

    store = MemoryStore(args.workspace, args.storage_root)
    try:
        connection = store.connect()
        migrate(connection)
        return store, None, EXIT_OK
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

    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        provider = provider_from_args(args.embedding_provider, args.embedding_model)
    except ValueError:
        store.close()
        return EXIT_USER_CONFIG, error_response("unsupported_embedding_provider", "Embedding provider is not supported.")

    try:
        rows = store.list_live_memory_items(scope=args.scope, type=args.type, role=args.role)
        live_by_id = {row["id"]: row for row in rows}
        scored_rows: list[tuple[float, dict[str, Any]]] = []
        index = LanceIndex(store.paths.lancedb_dir)
        index_data = index.read()
        warnings: list[str] = []

        if not index.available:
            warnings.append("semantic_index_unavailable")

        expected_provider_model = provider_key(provider)
        provider_mismatch = provider.supports_vectors and index_data.get("providerModel") not in (
            None,
            expected_provider_model,
        )
        if provider_mismatch:
            warnings.append("embedding_provider_mismatch")

        if provider.supports_vectors and index.exists() and not provider_mismatch:
            query_vector = provider.embed(args.query)
            for item in index.vector_search(query_vector, provider_model=expected_provider_model, limit=args.limit * 3):
                if not isinstance(item, dict) or item.get("providerModel") != expected_provider_model:
                    continue
                memory_id = item.get("id")
                if not isinstance(memory_id, str):
                    continue
                row = live_by_id.get(memory_id)
                if row is None:
                    continue
                if "score" in item and isinstance(item["score"], (float, int)):
                    score = float(item["score"])
                else:
                    vector = item.get("vector")
                    if not isinstance(vector, list):
                        continue
                    score = cosine_similarity(query_vector, [float(value) for value in vector])
                scored_rows.append((score, row))
        else:
            warnings.append("using_lexical_fallback")
            for row in rows:
                score = lexical_score(args.query, " ".join([row.get("summary") or "", row.get("content") or ""]))
                if score > 0:
                    scored_rows.append((score, row))

        if not scored_rows and rows:
            scored_rows = [(0.0, row) for row in rows]

        scored_rows.sort(key=lambda pair: (-pair[0], pair[1]["created_at"]))
        items = [search_item_payload(row, score) for score, row in scored_rows[: args.limit]]
        status = "degraded" if warnings else "ready"
        exit_code = EXIT_DEGRADED if warnings else EXIT_OK
        return exit_code, response(
            ok=True,
            status=status,
            workspaceId=store.identity.id,
            query=args.query,
            items=items,
            warnings=warnings,
        )
    finally:
        store.close()


def handle_reindex(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    store, error, exit_code = open_existing_store(args)
    if error is not None or store is None:
        return exit_code, error or error_response("storage_error", "Unable to open memory storage.")

    try:
        provider = provider_from_args(args.embedding_provider, args.embedding_model)
    except ValueError:
        store.close()
        return EXIT_USER_CONFIG, error_response("unsupported_embedding_provider", "Embedding provider is not supported.")

    try:
        rows = store.list_live_memory_items()
        provider_model = provider_key(provider)
        index_items: list[dict[str, Any]] = []
        if provider.supports_vectors:
            for row in rows:
                index_items.append(
                    {
                        "id": row["id"],
                        "vector": provider.embed(" ".join([row.get("summary") or "", row.get("content") or ""])),
                        "providerModel": provider_model,
                    }
                )

        index = LanceIndex(store.paths.lancedb_dir)
        if provider.supports_vectors:
            index.rebuild(provider_model=provider_model, items=index_items)
        store.update_index_metadata([row["id"] for row in rows], embedding_model=provider_model)
        warnings = []
        if not index.available:
            warnings.append("semantic_index_unavailable")
        if not provider.supports_vectors:
            warnings.append("using_lexical_fallback")
        return EXIT_OK, response(
            ok=True,
            status="reindexed",
            workspaceId=store.identity.id,
            indexedItems=len(rows),
            provider=provider.name,
            embeddingModel=provider_model,
            lancedb={"ok": index.available, "path": str(store.paths.lancedb_dir), "indexedItems": len(index_items)},
            warnings=warnings,
        )
    finally:
        store.close()


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


def validate_remember_args(args: argparse.Namespace) -> tuple[dict[str, Any] | None, int]:
    durable_scopes = {"workspace", "project", "role", "user"}
    source_ref_required_scopes = {"workspace", "project", "role"}

    if args.scope not in durable_scopes:
        return error_response("unsupported_scope", "Memory scope is not supported for durable storage."), EXIT_USER_CONFIG

    if args.scope in source_ref_required_scopes and not args.source_ref:
        return error_response("missing_source_ref", "Durable workspace, project, and role memories require source-ref."), EXIT_USER_CONFIG

    if args.scope == "user" and args.source_type != "user" and not args.source_ref:
        return error_response("missing_source_ref", "User memories without file evidence require source-type user."), EXIT_USER_CONFIG

    if not 0 <= args.confidence <= 1:
        return error_response("invalid_confidence", "Confidence must be between 0 and 1."), EXIT_USER_CONFIG

    metadata, metadata_error = parse_metadata(args.metadata_json)
    if metadata_error is not None:
        return metadata_error, EXIT_USER_CONFIG

    safety = check_memory_content(args.content, durable=True)
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
            indexedAt=item["indexed_at"],
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
