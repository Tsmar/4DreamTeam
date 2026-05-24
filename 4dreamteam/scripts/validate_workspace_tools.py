#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def find_workspace(start: Path) -> Path | None:
    env_workspace = os.environ.get("FOURDT_WORKSPACE")
    if env_workspace:
        candidate = Path(env_workspace).expanduser().resolve()
        return candidate if (candidate / ".4dt").exists() else None
    for candidate in (start, *start.parents):
        if (candidate / ".4dt").exists() and (candidate / ".4dt" / "board").exists():
            return candidate
    return None


def run(command: list[str], cwd: Path) -> int:
    print("+ " + " ".join(command))
    result = subprocess.run(command, cwd=str(cwd), check=False)
    return result.returncode


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    workspace = find_workspace(repo_root)
    if workspace is None:
        print(
            json.dumps(
                {
                    "ok": True,
                    "status": "skipped",
                    "reason": "No managed 4DreamTeam workspace with .4dt/board found in this checkout.",
                },
                indent=2,
            )
        )
        return 0

    commands = [
        [sys.executable, "packages/wiki/src/fourdt_wiki/cli.py", "--workspace", str(workspace), "--json", "index", "build"],
        [sys.executable, "packages/wiki/src/fourdt_wiki/cli.py", "--workspace", str(workspace), "--json", "index", "check"],
        [sys.executable, "packages/wiki/src/fourdt_wiki/cli.py", "--workspace", str(workspace), "--json", "validate"],
        [sys.executable, "-m", "fourdt_search.validate", "--workspace", str(workspace), "--json"],
        [sys.executable, "packages/board/src/fourdt_board/cli.py", "--workspace", str(workspace), "--json", "validate"],
    ]
    for command in commands:
        exit_code = run(command, repo_root)
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
