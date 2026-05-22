from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Sequence

from .migrations import migrate, schema_version
from .paths import workspace_identity, workspace_paths
from .sqlite_store import MemoryStore


EXIT_OK = 0
EXIT_USER_CONFIG = 1
EXIT_STORAGE = 2
EXIT_DEGRADED = 3
EXIT_UNSAFE_SAVE = 4

PLACEHOLDER_COMMANDS = {
    "remember",
    "forget",
    "search",
    "reindex",
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

    get_parser = subparsers.add_parser("get")
    add_common_arguments(get_parser)
    get_parser.add_argument("id")

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

    return EXIT_OK, response(
        ok=True,
        status="ready",
        workspaceId=identity.id,
        storageRoot=str(paths.storage_root),
        sqlitePath=str(paths.sqlite_path),
        sqlite={"ok": sqlite_ok, "path": str(paths.sqlite_path), "schemaVersion": version},
        lancedb={"ok": paths.lancedb_dir.exists(), "path": str(paths.lancedb_dir), "indexedItems": None},
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
    if args.command == "get":
        return handle_get(args)
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
