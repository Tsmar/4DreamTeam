# Lead Memory Policy

Use this file when a request may benefit from prior session context, saved decisions, user preferences, project continuity, local memory fallback, or memory effectiveness checks.

## Source Of Truth

4DT Memory is an optional local recall layer, not an authority.

Authority order:

1. Current user request and explicit approvals.
2. Current workspace instructions, tool-managed board/wiki artifacts, and accepted timeline evidence.
3. Approved source files inside explicit source boundaries.
4. 4DT Memory recalls and session state when available.

If memory conflicts with workspace artifacts, approved source files, or the current user request, trust the current artifacts/source/request and mention the conflict only when it affects the answer or next action.

## Recall Flow

At the start of a new session, always check memory readiness and load contract defaults when memory is ready:

```txt
4dt-memory doctor --workspace . --json
4dt-memory defaults load --workspace . --json
```

Apply contract project rules, operator preferences, active modes, and workflow constraints before proposing actions. If defaults load as `ready`, do not ask the operator to repeat context. If defaults are incomplete or invalid, run `4dt-memory onboarding questions --workspace . --json` and ask only the returned repair or setup questions before treating a mode or rule as active. If memory is degraded, empty, low-signal, or unavailable, report that state and continue from current workspace instructions without inventing remembered rules.

Use additional local 4DT Memory searches only as supplemental recall when they are likely to reduce context loss:

1. Continuing work from a previous session.
2. Looking for prior accepted decisions, user preferences, implementation lessons, or recurring project constraints.
3. Investigating why a previous task chose a direction.
4. Preparing a benchmark or retrospective about memory usefulness.

When memory is relevant, start with:

```txt
4dt-memory doctor --workspace . --json
```

If storage is ready, use `4dt-memory search "<query>" --workspace . --json` for concise previews, then `4dt-memory get <id> --workspace . --json` for full content when needed. Search preview output is not enough to change behavior by itself; verify important claims against board timeline entries, wiki pages, or approved sources.

Fallback order:

```txt
4DT Memory recall when ready and relevant
-> `lead_handoff` timeline entries for completed epic context
-> local wiki search
-> board timeline entries
-> exact approved source files when needed and allowed
-> user clarification only when required for safety or product meaning
```

If 4DT Memory is unavailable, uninitialized, degraded, empty, low-signal, or contradictory, continue with local wiki search and board evidence. Do not fail the workflow because memory is unavailable.

## English-First Memory Search Protocol

4DreamTeam managed knowledge artifacts are written in English for agents. When the user asks in another language, translate the search intent into English before searching memory, wiki pages, tasks, reports, or accepted quality artifacts.

Do not rely on a single literal memory query for conceptual, architectural, continuation, decision-history, or cross-artifact questions. Use a bounded query plan:

1. Search or read exact task ids, file paths, commands, titles, and known artifact pointers first.
2. Identify the user's intent, project or framework name, source type, and important entities.
3. Preserve technical terms while translating: commands, CLI names, filenames, package names, class names, task ids, `4dt-memory`, SQLite, LanceDB, MCP, hooks, and other project-specific identifiers.
4. Generate 4-8 typed English query variants, selected from normalized technical wording, architecture/workflow, implementation/file, decision/history, task/report/wiki artifact, and benchmark/process queries.
5. Use the user's original-language wording only as a fallback when English queries are thin or when the target source is known to contain that language.
6. Prefer results supported by exact pointers, multiple query variants, or current wiki/task/report evidence.
7. Verify memory hits against the authority order before making strong claims or changing behavior.
8. Answer in the user's language, while preserving artifact ids, file paths, commands, and technical terms exactly.

Example for `как работает память в dreamteam`:

```txt
4DreamTeam memory architecture
4DreamTeam memory recall workflow
4DreamTeam local memory runtime
4DT Memory SQLite LanceDB search reindex
4DreamTeam memory policy wiki fallback board timeline
4DT Memory retrieval quality benchmark
references lead memory context budget source map
```

## Wiki Fallback

The local wiki is the authoritative project memory fallback.

Use `4dt-wiki search/get` and `4dt-sources search/get` before broad approved-source reading. Memory does not expand source permissions and does not replace current wiki, source, or board evidence.

For plain workspace status, use `4dt-board` first. Do not run broad wiki search unless a project-specific question or continuation needs it.

## Epic Handoffs

`lead_handoff` timeline entries are the preferred durable local memory for completed epics. Use them before broad board history when continuing into the next epic, restarting work in a new session, or orienting a new agent.

Handoffs do not override current board items, timeline entries, wiki pages, approved sources, or the current user request. Treat them as compressed navigation and context: verify details from authoritative artifacts before changing behavior.

## Save Flow

Save to 4DT Memory only when the information is durable, accepted, and useful across future sessions:

1. Stable user preferences about workflow, communication, or project operation.
2. Accepted architecture, product, source-boundary, or process decisions.
3. Lessons learned from completed quality/release/debugging work.
4. Reusable gotchas that would prevent repeated mistakes.

Use `4dt-memory remember "<text>" --workspace . --scope <scope> --type <type> --source-type <source-type> --source-ref <source-ref> --json` for durable workspace, project, or role memory. User preferences may omit `--source-ref` only when `--scope user --source-type user` is explicit.

Do not save:

1. Secrets, credentials, tokens, private keys, `.env` contents, local secret files, dumps, production data, or personal data.
2. Large copied board/wiki/source contents.
3. Temporary implementation details that are already obvious from current files.
4. Unaccepted proposals, rejected assumptions, or speculative claims as durable memory.

Prefer concise memory entries with pointers to file paths instead of copying full content. Redaction blocks unsafe saves before storage; it is a safety gate, not a guarantee that all possible secrets can be detected.

## Storage And Degraded Mode

SQLite is the authoritative memory store. LanceDB is an experimental, rebuildable semantic index for improved retrieval quality. If LanceDB, embeddings, or index metadata are unavailable or mismatched, memory search degrades to lexical fallback or reports structured degraded status. The framework workflow continues through board timeline entries, wiki pages, and approved sources.

## Import, Export, And Sessions

`4dt-memory export --format jsonl` exports live memory items only. JSONL export may include full accepted memory content and should be treated as local private data.

`4dt-memory import <file> --format jsonl` is dry-run by default. It writes only with `--apply`, runs the same safety checks as `remember`, and leaves imported rows unindexed until `reindex`.

Session state is local workspace state for continuation. It is below board timeline entries, wiki pages, approved sources, and the current request in authority. Session state must be JSON-object data, size-limited, and TTL-scoped.

## Effectiveness Benchmark

Use `4dt-memory benchmark --workspace . --json` when the user asks whether memory improves 4DreamTeam work for a project.

Compare at least three modes:

1. Wiki-only: use managed wiki and board timeline evidence; do not use memory.
2. Memory-only: use 4DT Memory recalls first and avoid wiki/source reads unless required for safety.
3. Memory plus wiki fallback: use memory for continuity, then verify or fill gaps from wiki and board timeline evidence.

Measure:

1. Correctness against authoritative workspace/wiki/source artifacts.
2. Completeness of relevant decisions and constraints.
3. Number of irrelevant or stale recalled items.
4. Number of files read before a useful answer.
5. Time or latency when it materially affects workflow.
6. Safety: no secret exposure, no source-boundary bypass, and no unsupported claims.

Report whether memory should be used by default, used only on continuation tasks, or skipped for that project.

For retrieval-quality checks, compare a raw user query against the English-first agent protocol query set. The protocol is successful when it improves `top3`/MRR or reduces false negatives for bilingual and conceptual prompts without materially increasing irrelevant or stale recalls.
