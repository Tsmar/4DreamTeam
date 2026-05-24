#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: run_tool.py <tool-command> [args...]", file=sys.stderr)
        return 2
    archive = Path(__file__).resolve().with_name("4dt-tools.pyz")
    if not archive.exists():
        print(f"missing runtime archive: {archive}", file=sys.stderr)
        return 2
    os.execv(sys.executable, [sys.executable, str(archive), *args])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
