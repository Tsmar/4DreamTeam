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
    Rule(
        "contract_rules_via_semantic_search",
        re.compile(r'4dt-memory search "project rules operator preferences active modes workflow constraints"'),
        "Startup project rules must come from contract memory defaults, not semantic search.",
    ),
]


REQUIRED_TEXT = [
    (
        "new_session_memory_recall",
        "4dreamteam/references/lead/preflight.md",
        "4dt-memory defaults load --workspace . --json",
        "New-session startup must load contract memory defaults when memory is ready.",
    ),
    (
        "new_session_memory_questions",
        "4dreamteam/references/lead/preflight.md",
        "4dt-memory onboarding questions --workspace . --json",
        "New-session startup must ask suggested operator questions when defaults are incomplete or invalid.",
    ),
    (
        "new_session_board_check",
        "4dreamteam/references/lead/preflight.md",
        "4dt-board --workspace . --json validate",
        "New-session onboarding must check 4dt-board explicitly.",
    ),
    (
        "new_session_sources_check",
        "4dreamteam/references/lead/preflight.md",
        "4dt-sources --workspace . --json registry validate",
        "New-session onboarding must check 4dt-sources explicitly.",
    ),
    (
        "new_session_wiki_check",
        "4dreamteam/references/lead/preflight.md",
        "4dt-wiki --workspace . --json validate",
        "New-session onboarding must check 4dt-wiki explicitly.",
    ),
    (
        "new_session_memory_check",
        "4dreamteam/references/lead/preflight.md",
        "4dt-memory doctor --workspace . --json",
        "New-session onboarding must check 4dt-memory explicitly.",
    ),
    (
        "bounded_memory_recall",
        "4dreamteam/references/lead/preflight.md",
        "do not dump all memory into context",
        "Startup memory recall must stay bounded after contract defaults.",
    ),
    (
        "operator_memory_intent",
        "4dreamteam/references/lead/memory.md",
        "Operator Memory Intent",
        "Memory policy must recognize natural-language operator memory intent.",
    ),
    (
        "memory_placement_policy",
        "4dreamteam/references/lead/memory.md",
        "Memory Placement Policy",
        "Memory policy must define workspace, project, user, and role placement.",
    ),
    (
        "role_scoped_recall",
        "4dreamteam/references/lead/memory.md",
        "Role-Scoped Recall",
        "Memory policy must define role-scoped recall for active work.",
    ),
    (
        "memory_intent_russian_phrase",
        "4dreamteam/references/lead/memory.md",
        "чтобы в следующий раз не изучать",
        "Memory policy must cover Russian operator phrasing for avoid-repeat-discovery intent.",
    ),
    (
        "memory_behavior_change_plus_lesson",
        "4dreamteam/references/lead/memory.md",
        "behavior_change_plus_lesson",
        "Memory policy must distinguish behavior changes from durable memory saves.",
    ),
    (
        "memory_english_for_any_operator_language",
        "4dreamteam/references/lead/memory.md",
        "The operator may express memory intent in any language. Store durable memory content in English",
        "Durable memory must be saved in English regardless of operator language.",
    ),
    (
        "repair_confirmation",
        "4dreamteam/references/lead/preflight.md",
        "Repair commands require explicit operator confirmation.",
        "Recovery and repair actions must require explicit operator confirmation.",
    ),
    (
        "startup_tool_status",
        "docs/architecture/runtime-entrypoint.md",
        "reports each tool status",
        "Operator-facing startup docs must require per-tool status output.",
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
    relpath = path.relative_to(root).as_posix()
    if relpath.startswith("docs/changelog/"):
        return issues
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
                        "path": relpath,
                        "line": lineno,
                        "message": rule.message,
                        "text": line.strip(),
                    }
                )
    return issues


def validate_required_text(root: Path) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    for code, relpath, needle, message in REQUIRED_TEXT:
        path = root / relpath
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if needle not in text:
            issues.append(
                {
                    "code": code,
                    "severity": "error",
                    "path": relpath,
                    "line": None,
                    "message": message,
                    "text": needle,
                }
            )
    return issues


def run(paths: Iterable[str] | None = None, root: Path = REPO_ROOT) -> dict[str, object]:
    checked = list(iter_target_files(root, paths))
    issues: list[dict[str, object]] = []
    for path in checked:
        issues.extend(validate_file(root, path))
    if paths is None:
        issues.extend(validate_required_text(root))
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
