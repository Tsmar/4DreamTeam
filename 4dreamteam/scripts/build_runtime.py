#!/usr/bin/env python3
from __future__ import annotations

import shutil
import tempfile
import zipapp
from pathlib import Path


PACKAGE_NAMES = ("board", "wiki", "sources", "memory", "search")

MAIN = '''from __future__ import annotations

import importlib
import json
import sys

COMMANDS = {
    "board": "fourdt_board.cli",
    "wiki": "fourdt_wiki.cli",
    "sources": "fourdt_sources.cli",
    "memory": "fourdt_memory.cli",
    "search": "fourdt_search.cli",
    "search-validate": "fourdt_search.validate",
}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print("usage: 4dt-tools.pyz {board,wiki,sources,memory,search,search-validate} ...")
        return 0
    command = args.pop(0)
    module_name = COMMANDS.get(command)
    if module_name is None:
        print(json.dumps({"ok": False, "status": "error", "error": {"code": "unknown_command", "command": command}}, indent=2))
        return 2
    module = importlib.import_module(module_name)
    return int(module.main(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
'''


def copy_sources(packages_dir: Path, app_dir: Path) -> None:
    for name in PACKAGE_NAMES:
        src = packages_dir / name / "src"
        if not src.is_dir():
            raise SystemExit(f"missing package source: {src}")
        for child in src.iterdir():
            target = app_dir / child.name
            if child.is_dir():
                shutil.copytree(
                    child,
                    target,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
                )
            elif child.name != ".DS_Store":
                shutil.copy2(child, target)


def main() -> int:
    skill_dir = Path(__file__).resolve().parents[1]
    repo_root = skill_dir.parent
    packages_dir = repo_root / "packages"
    target = skill_dir / "scripts" / "4dt-tools.pyz"
    with tempfile.TemporaryDirectory(prefix="4dt-runtime-") as raw_tmp:
        app_dir = Path(raw_tmp) / "app"
        app_dir.mkdir()
        copy_sources(packages_dir, app_dir)
        (app_dir / "__main__.py").write_text(MAIN, encoding="utf-8")
        zipapp.create_archive(app_dir, target=target, interpreter="/usr/bin/env python3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
