# Lead Memory Policy

Use this file when a request may benefit from prior session context, saved decisions, user preferences, project continuity, or a comparison between `agentmemory` and the local wiki.

## Source Of Truth

Memory is an optional recall layer, not an authority.

Authority order:

1. Current user request and explicit approvals.
2. Current workspace artifacts: `AGENTS.md`, `tasks/`, `reports/`, and managed wiki pages.
3. Approved source files inside explicit source boundaries.
4. `agentmemory` recalls, lessons, and sessions when available.

If memory conflicts with workspace artifacts, approved source files, or the current user request, trust the current artifacts/source/request and mention the conflict only when it affects the answer or next action.

## Recall Flow

Use `agentmemory` recall only when it is available in the current session and likely to reduce context loss:

1. Continuing work from a previous session.
2. Looking for prior decisions, user preferences, implementation lessons, or recurring project constraints.
3. Investigating why a previous task chose a direction.
4. Preparing a benchmark or retrospective about memory usefulness.

Fallback order:

```txt
agentmemory recall when available and relevant
-> local wiki index/docs
-> tasks and reports
-> exact approved source files when needed and allowed
-> user clarification only when required for safety or product meaning
```

If `agentmemory` is unavailable, slow, empty, low-signal, or contradictory, continue with local wiki index-first navigation and workspace artifacts. Do not fail the workflow because memory is unavailable.

## Wiki Fallback

The local wiki is the authoritative project memory fallback.

When a current `docs/<project-name>/.index/source-map.json` exists, use index-first navigation before broad wiki or approved-source reading. If the generated index is missing or stale, use `docs/<project-name>/source-map.md` directly, then the smallest relevant wiki pages.

For plain workspace status, use the board and reports first. Do not run broad wiki search unless a project-specific question or continuation needs it.

## Save Flow

Save to memory only when the information is durable and useful across future sessions:

1. Stable user preferences about workflow, communication, or project operation.
2. Accepted architecture, product, source-boundary, or process decisions.
3. Lessons learned from completed quality/release/debugging work.
4. Reusable gotchas that would prevent repeated mistakes.

Do not save:

1. Secrets, credentials, tokens, private keys, `.env` contents, dumps, production data, or personal data.
2. Large copied task/report/wiki/source contents.
3. Temporary implementation details that are already obvious from current files.
4. Unaccepted proposals, rejected assumptions, or speculative claims unless clearly marked as unaccepted.

Prefer concise memory entries with pointers to file paths instead of copying full content.

## Effectiveness Benchmark

Use this benchmark when the user asks whether `agentmemory` improves 4DreamTeam work for a project.

Compare at least three modes:

1. Wiki-only: use managed wiki, source map, tasks, and reports; do not use memory.
2. Memory-only: use `agentmemory` recalls first and avoid wiki/source reads unless required for safety.
3. Memory plus wiki fallback: use memory for continuity, then verify or fill gaps from wiki/tasks/reports.

Use 5-10 realistic prompts, such as:

1. Continue an existing task.
2. Explain why a previous decision was made.
3. Identify source boundaries for a project.
4. Summarize what remains to do.
5. Shape a new task from prior project context.

Measure:

1. Correctness against authoritative workspace/wiki/source artifacts.
2. Completeness of relevant decisions and constraints.
3. Number of irrelevant or stale recalled items.
4. Number of files read before a useful answer.
5. Time or latency when it materially affects workflow.
6. Safety: no secret exposure, no source-boundary bypass, and no unsupported claims.

Report whether memory should be used by default, used only on continuation tasks, or skipped for that project.
