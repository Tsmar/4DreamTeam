#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


EXPECTED_PACKAGES = ("board", "wiki", "sources", "memory", "search", "db")
FORBIDDEN_PATTERNS = (
    "Lan" + "ceDB",
    "lan" + "cedb",
    "lance" + "_index",
    "embed" + "der",
    "4dreamteam" + "/tools",
)
SCAN_ROOTS = ("4dreamteam", "docs", "packages", "package.json", ".github")


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    if not path.exists():
        return
    for child in path.rglob("*"):
        if child.is_file() and "__pycache__" not in child.parts and child.suffix != ".pyc":
            yield child


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    issues: list[str] = []
    if (repo_root / "tools").exists():
        issues.append("legacy root tool-source directory must be renamed to packages/")
    if (repo_root / "4dreamteam" / "tools").exists():
        issues.append("installable skill package must not contain a tool-source tree")
    for name in EXPECTED_PACKAGES:
        package_dir = repo_root / "packages" / name
        if not (package_dir / "src").is_dir():
            issues.append(f"missing package src: packages/{name}/src")
        if not (package_dir / "tests").is_dir():
            issues.append(f"missing package tests: packages/{name}/tests")
    if not (repo_root / "4dreamteam" / "scripts" / "4dt-tools.pyz").exists():
        issues.append("missing built installed-skill runtime archive: 4dreamteam/scripts/4dt-tools.pyz")
    for root_name in SCAN_ROOTS:
        for file_path in iter_files(repo_root / root_name):
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    issues.append(f"forbidden pattern {pattern!r} in {file_path.relative_to(repo_root)}")
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
