# Lead Memory Policy

Use this file when a request may benefit from prior session context, saved decisions, user preferences, project continuity, local memory fallback, or memory effectiveness checks.

## Source Of Truth

4DT Memory is an optional local recall layer, not an authority.

Authority order:

1. Current user request and explicit approvals.
2. Current workspace artifacts: `AGENTS.md`, `tasks/`, `reports/`, and managed wiki pages.
3. Approved source files inside explicit source boundaries.
4. 4DT Memory recalls and session state when available.

If memory conflicts with workspace artifacts, approved source files, or the current user request, trust the current artifacts/source/request and mention the conflict only when it affects the answer or next action.

## Recall Flow

Use local 4DT Memory only when it is likely to reduce context loss:

1. Continuing work from a previous session.
2. Looking for prior accepted decisions, user preferences, implementation lessons, or recurring project constraints.
3. Investigating why a previous task chose a direction.
4. Preparing a benchmark or retrospective about memory usefulness.

When memory is relevant, start with:

```txt
4dt-memory doctor --workspace . --json
```

If storage is ready, use `4dt-memory search "<query>" --workspace . --json` for concise previews, then `4dt-memory get <id> --workspace . --json` for full content when needed. Search preview output is not enough to change behavior by itself; verify important claims against tasks, reports, wiki pages, or approved sources.

Fallback order:

```txt
4DT Memory recall when ready and relevant
-> epic handoffs in reports/handoffs/ for completed epic context
-> local wiki index/docs
-> tasks and reports
-> exact approved source files when needed and allowed
-> user clarification only when required for safety or product meaning
```

If 4DT Memory is unavailable, uninitialized, degraded, empty, low-signal, or contradictory, continue with local wiki index-first navigation and workspace artifacts. Do not fail the workflow because memory is unavailable.

## Wiki Fallback

The local wiki is the authoritative project memory fallback.

When a current `docs/<project-name>/.index/source-map.json` exists, use index-first navigation before broad wiki or approved-source reading. If the generated index is missing or stale, use `docs/<project-name>/source-map.md` directly, then the smallest relevant wiki pages.

For plain workspace status, use the board and reports first. Do not run broad wiki search unless a project-specific question or continuation needs it.

## Epic Handoffs

Epic handoffs in `reports/handoffs/` are the preferred durable local memory for completed epics. Use them before broad task/report history when continuing into the next epic, restarting work in a new session, or orienting a new agent.

Handoffs do not override current tasks, reports, wiki pages, approved sources, or the current user request. Treat them as compressed navigation and context: verify details from authoritative artifacts before changing behavior.

## Save Flow

Save to 4DT Memory only when the information is durable, accepted, and useful across future sessions:

1. Stable user preferences about workflow, communication, or project operation.
2. Accepted architecture, product, source-boundary, or process decisions.
3. Lessons learned from completed quality/release/debugging work.
4. Reusable gotchas that would prevent repeated mistakes.

Use `4dt-memory remember "<text>" --workspace . --scope <scope> --type <type> --source-type <source-type> --source-ref <source-ref> --json` for durable workspace, project, or role memory. User preferences may omit `--source-ref` only when `--scope user --source-type user` is explicit.

Do not save:

1. Secrets, credentials, tokens, private keys, `.env` contents, local secret files, dumps, production data, or personal data.
2. Large copied task/report/wiki/source contents.
3. Temporary implementation details that are already obvious from current files.
4. Unaccepted proposals, rejected assumptions, or speculative claims as durable memory.

Prefer concise memory entries with pointers to file paths instead of copying full content. Redaction blocks unsafe saves before storage; it is a safety gate, not a guarantee that all possible secrets can be detected.

## Storage And Degraded Mode

The default storage root is:

```txt
~/.codex/storage/4dreamteam/memory
```

SQLite is the authoritative memory store. LanceDB is only a rebuildable semantic index. If LanceDB, embeddings, or index metadata are unavailable or mismatched, memory search degrades to lexical fallback or reports structured degraded status. The framework workflow continues through tasks, reports, wiki pages, and approved sources.

## Import, Export, And Sessions

`4dt-memory export --format jsonl` exports live memory items only. JSONL export may include full accepted memory content and should be treated as local private data.

`4dt-memory import <file> --format jsonl` is dry-run by default. It writes only with `--apply`, runs the same safety checks as `remember`, and leaves imported rows unindexed until `reindex`.

Session state is local workspace state for continuation. It is below tasks, reports, wiki pages, approved sources, and the current request in authority. Session state must be JSON-object data, size-limited, and TTL-scoped.

## Effectiveness Benchmark

Use `4dt-memory benchmark --workspace . --json` when the user asks whether memory improves 4DreamTeam work for a project.

Compare at least three modes:

1. Wiki-only: use managed wiki, source map, tasks, and reports; do not use memory.
2. Memory-only: use 4DT Memory recalls first and avoid wiki/source reads unless required for safety.
3. Memory plus wiki fallback: use memory for continuity, then verify or fill gaps from wiki/tasks/reports.

Measure:

1. Correctness against authoritative workspace/wiki/source artifacts.
2. Completeness of relevant decisions and constraints.
3. Number of irrelevant or stale recalled items.
4. Number of files read before a useful answer.
5. Time or latency when it materially affects workflow.
6. Safety: no secret exposure, no source-boundary bypass, and no unsupported claims.

Report whether memory should be used by default, used only on continuation tasks, or skipped for that project.
