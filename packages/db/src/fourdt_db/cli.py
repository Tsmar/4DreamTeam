from __future__ import annotations

import argparse
import re
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_ROOT = Path(".4dt")
SCHEMA_REGISTRY_TABLE = "tool_schema_versions"
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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


def quote_identifier(value: str) -> str:
    if not IDENTIFIER_RE.match(value):
        raise UserError("invalid_identifier", f"Invalid SQL identifier: {value}")
    return f'"{value}"'


def table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def row_count(connection: sqlite3.Connection, table: str) -> int:
    if not table_exists(connection, table):
        return 0
    row = connection.execute(f"SELECT COUNT(*) AS count FROM {quote_identifier(table)}").fetchone()
    return int(row["count"])


def load_migration_spec(path: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except OSError as exc:
        raise UserError("migration_read_failed", str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise UserError("invalid_migration_json", str(exc)) from exc
    if not isinstance(value, dict):
        raise UserError("invalid_migration", "Migration spec must be a JSON object.")
    steps = value.get("steps")
    if not isinstance(steps, list):
        raise UserError("invalid_migration", "Migration spec requires a steps array.")
    return value


def registry_row(connection: sqlite3.Connection, domain: str) -> sqlite3.Row | None:
    ensure_schema_registry(connection)
    return connection.execute(
        f"SELECT * FROM {SCHEMA_REGISTRY_TABLE} WHERE domain = ?",
        (domain,),
    ).fetchone()


def validate_migration_preconditions(connection: sqlite3.Connection, spec: dict[str, Any]) -> None:
    domain = str(spec.get("domain", ""))
    if not domain:
        raise UserError("invalid_migration", "Migration spec requires domain.")
    expected_from = spec.get("from") or {}
    if not isinstance(expected_from, dict):
        raise UserError("invalid_migration", "Migration spec from must be an object.")
    row = registry_row(connection, domain)
    if row is None:
        raise UserError("schema_unknown", f"No recorded schema version for domain: {domain}")
    expected_version = expected_from.get("schemaVersion")
    expected_hash = expected_from.get("schemaHash")
    if expected_version is not None and int(row["schema_version"]) != int(expected_version):
        raise UserError("schema_mismatch", f"Domain {domain} version is {row['schema_version']}, expected {expected_version}.")
    if expected_hash is not None and str(row["schema_hash"]) != str(expected_hash):
        raise UserError("schema_mismatch", f"Domain {domain} schema hash does not match migration precondition.")


def expression_sql(value: Any) -> str:
    if isinstance(value, dict) and set(value) == {"sql"}:
        sql = str(value["sql"])
        if re.search(r";|--|/\*", sql):
            raise UserError("unsafe_expression", "SQL expressions cannot contain statement separators or comments.")
        return sql
    return "?"


def expression_params(value: Any) -> list[Any]:
    if isinstance(value, dict) and set(value) == {"sql"}:
        return []
    return [value]


def apply_copy_table(connection: sqlite3.Connection, step: dict[str, Any]) -> dict[str, Any]:
    from_table = str(step.get("fromTable", ""))
    to_table = str(step.get("toTable", ""))
    columns = step.get("columns")
    defaults = step.get("defaults", {})
    where = str(step.get("where", "")).strip()
    if not from_table or not to_table or not isinstance(columns, dict):
        raise UserError("invalid_step", "copy_table requires fromTable, toTable, and columns.")
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        raise UserError("invalid_step", "copy_table defaults must be an object.")
    if where and re.search(r";|--|/\*", where):
        raise UserError("unsafe_where", "copy_table where cannot contain statement separators or comments.")
    target_columns: list[str] = []
    select_parts: list[str] = []
    params: list[Any] = []
    for target, source in columns.items():
        target_columns.append(quote_identifier(str(target)))
        select_parts.append(quote_identifier(str(source)))
    for target, value in defaults.items():
        target_columns.append(quote_identifier(str(target)))
        select_parts.append(expression_sql(value))
        params.extend(expression_params(value))
    sql = (
        f"INSERT INTO {quote_identifier(to_table)} ({', '.join(target_columns)}) "
        f"SELECT {', '.join(select_parts)} FROM {quote_identifier(from_table)}"
    )
    if where:
        sql += f" WHERE {where}"
    before = row_count(connection, to_table)
    source_count = row_count(connection, from_table)
    connection.execute(sql, params)
    after = row_count(connection, to_table)
    return {"op": "copy_table", "fromTable": from_table, "toTable": to_table, "sourceRows": source_count, "insertedRows": after - before}


def apply_rename_table(connection: sqlite3.Connection, step: dict[str, Any]) -> dict[str, Any]:
    from_table = str(step.get("fromTable", ""))
    to_table = str(step.get("toTable", ""))
    if not from_table or not to_table:
        raise UserError("invalid_step", "rename_table requires fromTable and toTable.")
    connection.execute(f"ALTER TABLE {quote_identifier(from_table)} RENAME TO {quote_identifier(to_table)}")
    return {"op": "rename_table", "fromTable": from_table, "toTable": to_table}


def apply_drop_table(connection: sqlite3.Connection, step: dict[str, Any], *, allow_drop: bool) -> dict[str, Any]:
    table = str(step.get("table", ""))
    if not table:
        raise UserError("invalid_step", "drop_table requires table.")
    if not allow_drop:
        raise UserError("drop_not_allowed", "drop_table requires --allow-drop.")
    rows = row_count(connection, table)
    connection.execute(f"DROP TABLE IF EXISTS {quote_identifier(table)}")
    return {"op": "drop_table", "table": table, "droppedRows": rows}


def apply_validate_counts(connection: sqlite3.Connection, step: dict[str, Any]) -> dict[str, Any]:
    left = str(step.get("leftTable", ""))
    right = str(step.get("rightTable", ""))
    if not left or not right:
        raise UserError("invalid_step", "validate_counts requires leftTable and rightTable.")
    left_count = row_count(connection, left)
    right_count = row_count(connection, right)
    if left_count != right_count:
        raise UserError("validation_failed", f"Row count mismatch: {left}={left_count}, {right}={right_count}.")
    return {"op": "validate_counts", "leftTable": left, "rightTable": right, "rowCount": left_count}


def apply_validate_not_null(connection: sqlite3.Connection, step: dict[str, Any]) -> dict[str, Any]:
    table = str(step.get("table", ""))
    columns = step.get("columns")
    if not table or not isinstance(columns, list):
        raise UserError("invalid_step", "validate_not_null requires table and columns.")
    failures: dict[str, int] = {}
    for column in columns:
        row = connection.execute(
            f"SELECT COUNT(*) AS count FROM {quote_identifier(table)} WHERE {quote_identifier(str(column))} IS NULL"
        ).fetchone()
        count = int(row["count"])
        if count:
            failures[str(column)] = count
    if failures:
        raise UserError("validation_failed", f"NULL validation failed for {table}: {failures}.")
    return {"op": "validate_not_null", "table": table, "columns": columns}


def apply_validate_foreign_keys(connection: sqlite3.Connection) -> dict[str, Any]:
    rows = connection.execute("PRAGMA foreign_key_check").fetchall()
    if rows:
        raise UserError("validation_failed", f"Foreign key validation failed: {len(rows)} issue(s).")
    return {"op": "validate_foreign_keys", "issueCount": 0}


def apply_record_schema(connection: sqlite3.Connection, step: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    domain = str(step.get("domain") or spec.get("domain") or "")
    target = step.get("to") or spec.get("to") or {}
    if not domain or not isinstance(target, dict):
        raise UserError("invalid_step", "record_schema requires domain and to schema metadata.")
    version = target.get("schemaVersion")
    schema_hash = target.get("schemaHash")
    if version is None or schema_hash is None:
        raise UserError("invalid_step", "record_schema requires schemaVersion and schemaHash.")
    tool_version = str(target.get("toolVersion") or spec.get("toolVersion") or "")
    ensure_schema_registry(connection)
    connection.execute(
        f"""
        INSERT INTO {SCHEMA_REGISTRY_TABLE} (domain, schema_version, schema_hash, tool_version, applied_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(domain) DO UPDATE SET
          schema_version = excluded.schema_version,
          schema_hash = excluded.schema_hash,
          tool_version = excluded.tool_version,
          applied_at = excluded.applied_at
        """,
        (domain, int(version), str(schema_hash), tool_version, iso_now()),
    )
    return {"op": "record_schema", "domain": domain, "schemaVersion": int(version), "schemaHash": str(schema_hash)}


def migration_plan(workspace: Path, spec_path: str) -> dict[str, Any]:
    spec = load_migration_spec(spec_path)
    if not sqlite_path(workspace).exists():
        raise UserError("db_missing", "Shared database does not exist.")
    connection = connect(workspace)
    try:
        validate_migration_preconditions(connection, spec)
        steps = []
        for index, step in enumerate(spec["steps"], start=1):
            if not isinstance(step, dict):
                raise UserError("invalid_step", f"Step {index} must be an object.")
            op = str(step.get("op", ""))
            summary: dict[str, Any] = {"index": index, "op": op}
            if op == "copy_table":
                summary.update(
                    {
                        "fromTable": step.get("fromTable"),
                        "toTable": step.get("toTable"),
                        "sourceRows": row_count(connection, str(step.get("fromTable", ""))),
                        "columns": step.get("columns", {}),
                        "defaults": sorted((step.get("defaults") or {}).keys()),
                    }
                )
            elif op in {"rename_table", "drop_table", "validate_counts", "validate_not_null", "validate_foreign_keys", "record_schema"}:
                summary.update({key: value for key, value in step.items() if key != "op"})
            else:
                raise UserError("unsupported_step", f"Unsupported migration op: {op}")
            steps.append(summary)
    finally:
        connection.close()
    return {"id": spec.get("id"), "domain": spec.get("domain"), "applyRequiredApproval": True, "steps": steps}


def migration_apply(workspace: Path, spec_path: str, *, backup: bool, allow_drop: bool) -> dict[str, Any]:
    spec = load_migration_spec(spec_path)
    if not sqlite_path(workspace).exists():
        raise UserError("db_missing", "Shared database does not exist.")
    backup_result = backup_create(workspace, None) if backup else None
    connection = connect(workspace)
    reports: list[dict[str, Any]] = []
    try:
        validate_migration_preconditions(connection, spec)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN IMMEDIATE")
        for step in spec["steps"]:
            if not isinstance(step, dict):
                raise UserError("invalid_step", "Migration steps must be objects.")
            op = str(step.get("op", ""))
            if op == "copy_table":
                reports.append(apply_copy_table(connection, step))
            elif op == "rename_table":
                reports.append(apply_rename_table(connection, step))
            elif op == "drop_table":
                reports.append(apply_drop_table(connection, step, allow_drop=allow_drop))
            elif op == "validate_counts":
                reports.append(apply_validate_counts(connection, step))
            elif op == "validate_not_null":
                reports.append(apply_validate_not_null(connection, step))
            elif op == "validate_foreign_keys":
                reports.append(apply_validate_foreign_keys(connection))
            elif op == "record_schema":
                reports.append(apply_record_schema(connection, step, spec))
            else:
                raise UserError("unsupported_step", f"Unsupported migration op: {op}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"id": spec.get("id"), "domain": spec.get("domain"), "backup": backup_result, "steps": reports}


def connect(workspace: Path) -> sqlite3.Connection:
    (workspace / RUNTIME_ROOT).mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path(workspace))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    ensure_schema_registry(connection)
    return connection


def ensure_schema_registry(connection: sqlite3.Connection) -> None:
    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_REGISTRY_TABLE} (
          domain TEXT PRIMARY KEY,
          schema_version INTEGER NOT NULL,
          schema_hash TEXT NOT NULL,
          tool_version TEXT NOT NULL DEFAULT '',
          applied_at TEXT NOT NULL
        )
        """
    )
    connection.commit()


def schema_status(workspace: Path) -> dict[str, Any]:
    if not sqlite_path(workspace).exists():
        return {"database": sqlite_path(workspace).as_posix(), "exists": False, "domains": []}
    connection = connect(workspace)
    try:
        rows = connection.execute(
            f"""
            SELECT domain, schema_version, schema_hash, tool_version, applied_at
            FROM {SCHEMA_REGISTRY_TABLE}
            ORDER BY domain
            """
        ).fetchall()
    finally:
        connection.close()
    return {
        "database": sqlite_path(workspace).as_posix(),
        "exists": True,
        "registryTable": SCHEMA_REGISTRY_TABLE,
        "domains": [
            {
                "domain": row["domain"],
                "schemaVersion": row["schema_version"],
                "schemaHash": row["schema_hash"],
                "toolVersion": row["tool_version"],
                "appliedAt": row["applied_at"],
                "status": "recorded",
            }
            for row in rows
        ],
    }


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
    schema = sub.add_parser("schema", help="Inspect shared database schema registry.")
    schema_sub = schema.add_subparsers(dest="schema_action", required=True)
    status = schema_sub.add_parser("status", help="Show per-domain recorded schema versions.")
    status.set_defaults(action="schema-status")
    migrate = sub.add_parser("migrate", help="Plan or apply declarative database migrations.")
    migrate_sub = migrate.add_subparsers(dest="migrate_action", required=True)
    plan = migrate_sub.add_parser("plan", help="Summarize a migration without reading row contents or writing data.")
    plan.add_argument("--file", required=True, help="Migration JSON spec path.")
    plan.set_defaults(action="migrate-plan")
    apply_parser = migrate_sub.add_parser("apply", help="Apply an operator-approved migration spec.")
    apply_parser.add_argument("--file", required=True, help="Migration JSON spec path.")
    apply_parser.add_argument("--backup", action="store_true", help="Create a database backup before applying.")
    apply_parser.add_argument("--allow-drop", action="store_true", help="Allow drop_table steps.")
    apply_parser.set_defaults(action="migrate-apply")
    return parser


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).expanduser().resolve(strict=False)
    if args.action == "backup-create":
        return 0, payload(True, "ready", backup=backup_create(workspace, args.output))
    if args.action == "backup-list":
        return 0, payload(True, "ready", backups=backup_list(workspace))
    if args.action == "schema-status":
        return 0, payload(True, "ready", schema=schema_status(workspace))
    if args.action == "migrate-plan":
        return 0, payload(True, "ready", migration=migration_plan(workspace, args.file))
    if args.action == "migrate-apply":
        return 0, payload(True, "applied", migration=migration_apply(workspace, args.file, backup=args.backup, allow_drop=args.allow_drop))
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
