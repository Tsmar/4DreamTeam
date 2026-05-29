#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


WRAPPERS = (
    "4dt-board.py",
    "4dt-wiki.py",
    "4dt-sources.py",
    "4dt-memory.py",
    "4dt-search.py",
    "4dt-search-validate.py",
)


def ignore_runtime_noise(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name == "__pycache__" or name.endswith(".pyc")}


def main() -> int:
    source_skill = Path(__file__).resolve().parents[1]
    if not (source_skill / "scripts" / "4dt-tools.pyz").exists():
        return 2
    with tempfile.TemporaryDirectory(prefix="4dt-installed-skill-") as raw_tmp:
        target_skill = Path(raw_tmp) / "4dreamteam"
        shutil.copytree(source_skill, target_skill, ignore=ignore_runtime_noise)
        for wrapper in WRAPPERS:
            result = subprocess.run(
                [sys.executable, str(target_skill / "scripts" / wrapper), "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                print(f"runtime wrapper failed: {wrapper}", file=sys.stderr)
                return result.returncode or 1
        memory_workspace = Path(raw_tmp) / "memory-workspace"
        memory_workspace.mkdir()
        result = subprocess.run(
            [
                sys.executable,
                str(target_skill / "scripts" / "4dt-memory.py"),
                "init",
                "--workspace",
                str(memory_workspace),
                "--json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            print("runtime wrapper failed: 4dt-memory.py init", file=sys.stderr)
            return result.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
