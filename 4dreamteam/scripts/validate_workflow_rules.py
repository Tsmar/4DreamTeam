#!/usr/bin/env python3
"""Validate agent-facing workflow rules stay on the script-managed model."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_GLOBS = [
    "4dreamteam/SKILL.md",
    "4dreamteam/references/**/*.md",
    "4dreamteam/assets/templates/**/*.md",
    "docs/**/*.md",
    "README.md",
    "AGENTS.md",
]


@dataclass(frozen=True)
class Rule:
    code: str
    pattern: re.Pattern[str]
    message: str


RULES = [
    Rule(
        "removed_docs_index",
        re.compile(r"\bdocs/index\.md\b"),
        "docs/index.md registry must not be presented as an active workflow artifact.",
    ),
    Rule(
        "removed_multi_project_wiki",
        re.compile(r"docs/<project-name>|docs/<project"),
        "Multi-project docs/<project-name> wiki paths must not be presented as the active model.",
    ),
    Rule(
        "removed_source_map",
        re.compile(r"\bsource-map(?:\.md)?\b|\.index/sources"),
        "Source-map and generated source inventory workflows are legacy.",
    ),
    Rule(
        "removed_standalone_reports",
        re.compile(r"reports/(?:tasks|quality|product|release|handoffs)|developer/report|quality/(?:accepted|rejected)"),
        "Standalone reports must be described as board timeline entries, not active report files.",
    ),
    Rule(
        "direct_task_paths",
        re.compile(r"(?<!script-managed `)tasks/(?:backlog|analytic|developer|quality|wiki|release|released|done|rejected)/"),
        "Agent-facing instructions must route board access through 4dt-board instead of direct task paths.",
    ),
]


ALLOW_RE = re.compile(
    r"(legacy|old|removed|no longer|must not|do not|stale|replaced|example output|"
    r"script-managed|internal storage|storage path|tool output|validation check|"
    r"4dt-board|4dt-wiki|4dt-sources|fourdt_board|fourdt_wiki|fourdt_sources)",
    re.IGNORECASE,
)


def iter_default_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for pattern in DEFAULT_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def iter_target_files(root: Path, paths: Iterable[str] | None) -> Iterable[Path]:
    if paths is None:
        yield from iter_default_files(root)
        return
    for rel in paths:
        path = root / rel
        if path.exists():
            yield path


def validate_file(root: Path, path: Path) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        if ALLOW_RE.search(line):
            continue
        for rule in RULES:
            if rule.pattern.search(line):
                issues.append(
                    {
                        "code": rule.code,
                        "severity": "error",
                        "path": path.relative_to(root).as_posix(),
                        "line": lineno,
                        "message": rule.message,
                        "text": line.strip(),
                    }
                )
    return issues


def run(paths: Iterable[str] | None = None, root: Path = REPO_ROOT) -> dict[str, object]:
    checked = list(iter_target_files(root, paths))
    issues: list[dict[str, object]] = []
    for path in checked:
        issues.extend(validate_file(root, path))
    return {
        "ok": not issues,
        "checked": [path.relative_to(root).as_posix() for path in checked],
        "issueCount": len(issues),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate 4DreamTeam workflow rule docs.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("paths", nargs="*", help="Optional repository-relative files to check.")
    args = parser.parse_args()

    result = run(args.paths or None)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["ok"]:
        print(f"workflow rules ok ({len(result['checked'])} files checked)")
    else:
        print(f"workflow rules failed ({result['issueCount']} issues)")
        for issue in result["issues"]:
            print(f"{issue['path']}:{issue['line']}: {issue['code']}: {issue['text']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
