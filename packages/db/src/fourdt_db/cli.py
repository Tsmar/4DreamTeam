from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_ROOT = Path(".4dt")


class UserError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sqlite_path(workspace: Path) -> Path:
    return workspace / RUNTIME_ROOT / "db.sqlite3"


def default_backup_path(workspace: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return workspace / RUNTIME_ROOT / "backups" / f"db-{stamp}.sqlite3"


def backup_create(workspace: Path, output: str | None) -> dict[str, Any]:
    source = sqlite_path(workspace)
    if not source.exists():
        raise UserError("db_missing", "Shared database does not exist.")
    target = Path(output).expanduser() if output else default_backup_path(workspace)
    if not target.is_absolute():
        target = (workspace / target).resolve(strict=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    source_connection = sqlite3.connect(source)
    target_connection = sqlite3.connect(target)
    try:
        source_connection.backup(target_connection)
    finally:
        target_connection.close()
        source_connection.close()
    return {
        "source": source.as_posix(),
        "backup": target.as_posix(),
        "bytes": target.stat().st_size,
        "createdAt": iso_now(),
    }


def backup_list(workspace: Path) -> list[dict[str, Any]]:
    root = workspace / RUNTIME_ROOT / "backups"
    if not root.exists():
        return []
    backups = []
    for path in sorted(root.glob("*.sqlite3")):
        stat = path.stat()
        backups.append({"path": path.as_posix(), "bytes": stat.st_size, "mtime": stat.st_mtime})
    return backups


def payload(ok: bool, status: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "status": status, **extra}


def print_result(value: dict[str, Any], json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return
    print(json.dumps(value, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="4dt-db", description="Maintain the shared .4dt/db.sqlite3 database.")
    parser.add_argument("--workspace", default=".", help="Workspace path. Defaults to the current directory.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output for agents.")
    sub = parser.add_subparsers(dest="action", required=True)
    backup = sub.add_parser("backup", help="Create or list shared database backups.")
    backup_sub = backup.add_subparsers(dest="backup_action", required=True)
    create = backup_sub.add_parser("create", help="Create a consistent SQLite backup copy.")
    create.add_argument("--output", help="Backup output path. Defaults to .4dt/backups/db-<timestamp>.sqlite3.")
    create.set_defaults(action="backup-create")
    list_parser = backup_sub.add_parser("list", help="List local shared database backups.")
    list_parser.set_defaults(action="backup-list")
    return parser


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).expanduser().resolve(strict=False)
    if args.action == "backup-create":
        return 0, payload(True, "ready", backup=backup_create(workspace, args.output))
    if args.action == "backup-list":
        return 0, payload(True, "ready", backups=backup_list(workspace))
    raise UserError("unknown_command", f"Unknown command: {args.action}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        exit_code, result = command(args)
    except UserError as error:
        result = payload(False, "error", error={"code": error.code, "message": error.message})
        print_result(result, args.json)
        return 1
    print_result(result, args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
