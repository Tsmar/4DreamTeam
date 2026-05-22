from __future__ import annotations

import re
from dataclasses import dataclass


MAX_CONTENT_CHARS = 4000
MAX_CONTENT_LINES = 80


@dataclass(frozen=True)
class SafetyIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SafetyResult:
    ok: bool
    issues: tuple[SafetyIssue, ...] = ()


PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?im)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|secret|password|passwd|pwd)\b"
    r"\s*[:=]\s*['\"]?[^\s'\"]{8,}"
)
TOKEN_LABEL_RE = re.compile(
    r"(?im)\b(token|secret|api[_-]?key|password)\b\s+(?:is|=|:)\s*[A-Za-z0-9_\-./+=]{12,}"
)
HIGH_ENTROPY_TOKEN_RE = re.compile(r"\b(?:[A-Za-z0-9+/]{32,}={0,2}|[A-Fa-f0-9]{40,})\b")
ENV_FILE_RE = re.compile(
    r"(?im)^\s*(DATABASE_URL|REDIS_URL|AWS_SECRET_ACCESS_KEY|OPENAI_API_KEY|GITHUB_TOKEN|PRIVATE_KEY)\s*="
)
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PRODUCTION_DATA_RE = re.compile(r"(?i)\b(production data|prod data|database dump|db dump|sql dump|customer dump)\b")
UNACCEPTED_SPECULATION_RE = re.compile(
    r"(?i)\b(unaccepted speculation|not accepted|unapproved assumption|speculative|hypothesis|maybe|probably)\b"
)


def check_memory_content(content: str, *, durable: bool = True) -> SafetyResult:
    issues: list[SafetyIssue] = []
    stripped = content.strip()

    if not stripped:
        issues.append(SafetyIssue("empty_content", "Memory content must not be empty."))

    if len(content) > MAX_CONTENT_CHARS or content.count("\n") + 1 > MAX_CONTENT_LINES:
        issues.append(SafetyIssue("large_artifact", "Memory content is too large for durable storage."))

    if PRIVATE_KEY_RE.search(content):
        issues.append(SafetyIssue("private_key", "Memory content appears to contain a private key."))

    if SECRET_ASSIGNMENT_RE.search(content) or TOKEN_LABEL_RE.search(content) or ENV_FILE_RE.search(content):
        issues.append(SafetyIssue("secret_like_content", "Memory content appears to contain secrets or credentials."))

    if HIGH_ENTROPY_TOKEN_RE.search(content):
        issues.append(SafetyIssue("token_like_content", "Memory content appears to contain a token-like value."))

    if PRODUCTION_DATA_RE.search(content):
        issues.append(SafetyIssue("production_data", "Memory content appears to contain production data or a dump."))

    if SSN_RE.search(content):
        issues.append(SafetyIssue("personal_data", "Memory content appears to contain personal data."))

    if EMAIL_RE.search(content):
        issues.append(SafetyIssue("personal_data", "Memory content appears to contain personal data."))

    if durable and UNACCEPTED_SPECULATION_RE.search(content):
        issues.append(SafetyIssue("unaccepted_speculation", "Durable memory must not store unaccepted speculation."))

    deduped: dict[str, SafetyIssue] = {}
    for issue in issues:
        deduped.setdefault(issue.code, issue)
    return SafetyResult(ok=not deduped, issues=tuple(deduped.values()))
