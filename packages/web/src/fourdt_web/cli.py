from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .server import serve


def payload(ok: bool, status: str, **extra: Any) -> dict[str, Any]:
    return {"ok": ok, "status": status, **extra}


def print_result(value: dict[str, Any], json_output: bool) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def command(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    workspace = Path(args.workspace).resolve()
    if args.action == "serve":
        result = serve(workspace, args.host, args.port)
        return 0, payload(True, "stopped", serve=result)
    raise ValueError(f"Unknown command: {args.action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="4dt-web",
        description="Run the local 4DreamTeam Workspace View over managed workspace state.",
    )
    parser.add_argument("--workspace", default=".", help="Workspace path. Defaults to the current directory.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output after the server stops.")
    sub = parser.add_subparsers(dest="action", required=True)
    serve_parser = sub.add_parser("serve", help="Run the read-only local Workspace View.")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    serve_parser.add_argument("--port", type=int, default=4174, help="Bind port. Defaults to 4174. Use 0 for an ephemeral port.")
    serve_parser.set_defaults(action="serve")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code, result = command(args)
    print_result(result, args.json)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
