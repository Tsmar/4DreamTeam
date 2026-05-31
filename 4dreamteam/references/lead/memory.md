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

If memory is not initialized and the current folder is already a confirmed 4DreamTeam workspace, run `4dt-memory init --workspace . --json`; it creates SQLite storage and seeds only missing baseline contract keys. Do not initialize memory in an unconfirmed empty workspace without operator approval.

Apply contract project rules, operator preferences, active modes, and workflow constraints before proposing actions. If defaults load as `ready`, do not ask the operator to repeat context. If defaults are incomplete or invalid, run `4dt-memory onboarding questions --workspace . --json` and ask only the returned repair or setup questions before treating a mode or rule as active. If memory is empty, low-signal, or unavailable, report that state and continue from current workspace instructions without inventing remembered rules.

Use additional local 4DT Memory searches only as supplemental recall when they are likely to reduce context loss:

1. Continuing work from a previous session.
2. Looking for prior accepted decisions, user preferences, implementation lessons, or recurring project constraints.
3. Investigating why a previous task chose a direction.
4. Preparing a benchmark or retrospective about memory usefulness.

When memory is relevant, start with:

```txt
4dt-memory doctor --workspace . --json
```

If storage is ready, use `4dt-search query "<query>" --domain memory --workspace . --json` for concise previews, then the result `getCommand` or `4dt-memory get <id> --workspace . --json` for full content when needed. Search preview output is not enough to change behavior by itself; verify important claims against board timeline entries, wiki pages, or approved sources.

Fallback order:

```txt
4DT Memory recall when ready and relevant
-> `lead_handoff` timeline entries for completed epic context
-> local wiki discovery through `4dt-search --domain wiki`
-> board timeline entries
-> exact approved source files when needed and allowed
-> user clarification only when required for safety or product meaning
```

If 4DT Memory is unavailable, uninitialized, degraded, empty, low-signal, or contradictory, continue with local wiki and board evidence through `4dt-search` and exact domain reads. Do not fail the workflow because memory is unavailable.

## Operator Memory Intent

Operators often ask for durable learning in natural language instead of naming `4dt-memory`. Treat the following as memory-intent signals when the current request is durable, project-relevant, and useful beyond the current turn:

1. Explicit remember phrases: "remember", "save this", "запомни", "нужно запомнить", "сохрани на будущее".
2. Avoid repeated discovery: "next time do not study this again", "so we do not rediscover it", "чтобы в следующий раз не изучать".
3. Context-waste corrections: noisy logs, repeated setup, irrelevant output, repeated source reading, or workflow friction that consumes agent/operator context.
4. Corrective lessons: "avoid doing this", "we made this mistake", "учти на будущее", "больше так не делай".

Classify the request before saving:

1. `direct_save`: the operator states the durable rule clearly and it is safe to save.
2. `investigate_then_save`: the operator names an area, such as test workflow or noisy logs, but the agent must inspect approved wiki, board, memory, or source evidence before summarizing the durable lesson.
3. `behavior_change_plus_lesson`: the operator asks for a code, docs, tooling, or workflow change; run the normal task workflow first, then save a lesson only after evidence or acceptance makes it durable.
4. `do_not_save`: the content is temporary, speculative, unsafe, secret-bearing, unaccepted, already obvious from files, or contradicted by current evidence.

Memory intent does not bypass approval gates, source boundaries, role workflow, or independent quality. If the request includes file changes, infrastructure, dependencies, release actions, or other gated work, follow the normal workflow and record memory only through the safe save flow.

The operator may express memory intent in any language. Store durable memory content in English for portability, cross-agent recall, and consistent `4dt-search` ranking. Preserve exact commands, file paths, task ids, CLI names, code identifiers, and localized user-facing text when they are the fact being remembered.

## Memory Placement Policy

Choose the narrowest durable scope that will be recalled by the right future agent:

1. `scope=workspace`: workspace operating rules, startup commands, source boundaries, validation expectations, tool launch rules, and cross-project 4DreamTeam workspace behavior.
2. `scope=project`: project-wide product, architecture, process, testing, logging, build, or documentation knowledge useful across multiple roles.
3. `scope=role --role <role>`: role-specific lessons and instructions. Examples: `developer` test commands and log-noise gotchas; `quality` acceptance traps; `wiki` documentation sync rules; `release` packaging constraints; `devops` operational runbooks.
4. `scope=user`: stable operator preferences about communication, approval style, workflow, or collaboration.

Use concise durable types:

1. `implementation_lesson` for learned behavior from completed implementation, debugging, testing, or validation.
2. `gotcha` for mistakes or environmental traps that would cause repeated failures.
3. `operator_preference` for stable user or operator preferences.
4. `process_instruction` for accepted workflow instructions that should guide future agents.
5. `decision` for accepted product, architecture, source-boundary, or process decisions.

Save project, workspace, and role memories with a concrete `--source-ref`, preferably a task id, timeline entry id, wiki page id, or approved source path. Prefer one compact memory that points to evidence over copied logs, full reports, or broad source excerpts.

## Role-Scoped Recall

After route selection, use role-scoped memory searches only when prior lessons are likely to affect the next action. Build a small query from the current role, task title, artifact ids, commands, source paths, and translated English technical terms.

Examples:

```txt
developer project test workflow noisy logs validation commands
quality acceptance criteria rejected gotcha task TASK-0017
wiki post-acceptance documentation source-backed update
release packaging changelog staging commit policy
```

Search `scope=role` memories for the active role first when supported by the tool, then project/workspace memory for cross-role constraints. Keep recall bounded: use a small limit, read previews first, and fetch exact memory records only for results that could change the plan.

## Wake Context / Wakeup Recall

Wake Context is the compact continuation layer that lets a new agent session resume like a rested person waking up with the important parts of yesterday retained and the noisy working context gone. It is not a full transcript and it is not authority over current artifacts. It is a short set of memory records and pointers that tells the next session what matters first.

Use Wakeup Recall at the start of every confirmed 4DreamTeam workspace session after memory readiness and contract defaults:

1. Search memory for pending startup instructions, one-time operator messages, and the latest session handoff.
2. Fetch exact memory records before acting on them.
3. Deliver operator-facing one-time messages in the user's language unless the message explicitly requires another language.
4. Retire or forget delivered one-time records when their metadata or content says `delete_after_delivery`, `temporary`, or equivalent.
5. Treat session handoffs as compressed navigation: use their board task ids, wiki page ids, source paths, commands, decisions, and next-action pointers before broad discovery.
6. Verify substantive claims against current board, wiki, approved sources, or the current user request before changing files, moving tasks, or making release decisions.

Good Wakeup Recall queries include:

```txt
startup instruction pending operator message one-time delete after delivery
latest session handoff wake context continuation next session
```

Use durable memory types consistently:

1. `process_instruction` for accepted startup behavior, including pending one-time messages.
2. `operator_preference` for stable operator collaboration preferences.
3. `decision` for accepted project or workflow decisions.
4. `implementation_lesson` or `gotcha` for reusable lessons from completed work.

For session endings, create or update a compact handoff when the operator says the chat is ending, moving to a new chat, or should be continued later. The handoff should include current focus, last meaningful state, accepted decisions, exact task/wiki/source pointers, the best next action, and avoid repeating content that already exists in board/wiki/source artifacts. Supersede old handoffs instead of letting multiple stale continuation records compete.

Deleted or forgotten memory should remain administratively auditable when the tool supports it, but normal Wakeup Recall must ignore retired records.

## Startup And Task Recall Profiles

Startup memory has two layers:

1. Contract defaults from `4dt-memory defaults load --workspace . --json`; these are always applied when ready.
2. Wake Context from Wakeup Recall; pending startup instructions, one-time operator messages, and the latest session handoff are checked before proposing work.
3. Bounded supplemental recall; use it only after the task route, role, or continuation context makes it useful.

Do not dump all memory into the startup context. Use `4dt-search query` with explicit domains and role/task-enriched English query variants. Prefer `--domain memory` for prior lessons, `--domain wiki` for accepted project knowledge, `--domain board` for timeline evidence, and `--domain sources` for approved source truth. Bring in only the smallest set needed to prevent repeated discovery or avoid known mistakes.

For requests like "remember how tests work so next time you do not study it again", first discover the current test workflow through approved wiki/source/board evidence, then save a concise `project` or `role=developer` memory. For requests like "optimize test logs because they waste context", treat the log change as normal developer work and save a lesson afterward only if the final behavior is accepted or source-backed.

## English-First Memory Search Protocol

4DreamTeam managed knowledge artifacts are written in English for agents. When the user asks in any other language, translate the search intent into English before searching memory, wiki pages, tasks, reports, or accepted quality artifacts. Durable memory content should be saved in English regardless of the operator's language, except for exact localized strings that are themselves the subject of the memory.

Do not rely on a single literal memory query for conceptual, architectural, continuation, decision-history, or cross-artifact questions. Use a bounded query plan:

1. Search or read exact task ids, file paths, commands, titles, and known artifact pointers first.
2. Identify the user's intent, project or framework name, source type, and important entities.
3. Preserve technical terms while translating: commands, CLI names, filenames, package names, class names, task ids, `4dt-memory`, SQLite, `4dt-search`, MCP, hooks, and other project-specific identifiers.
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
4DT Memory SQLite 4dt-search runtime retrieval
4DreamTeam memory policy wiki fallback board timeline
4DT Memory retrieval quality benchmark
references lead memory context budget source map
```

## Wiki Fallback

The local wiki is the authoritative project memory fallback.

Use `4dt-search query` with explicit `wiki` or `sources` domains before broad approved-source reading. Memory does not expand source permissions and does not replace current wiki, source, or board evidence.

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

Memory write commands return compact confirmations instead of echoing saved prose or JSON values. Use explicit read commands such as `4dt-memory get`, `4dt-memory keys get`, or `4dt-memory defaults load` only when the saved content must be inspected.

Do not save:

1. Secrets, credentials, tokens, private keys, `.env` contents, local secret files, dumps, production data, or personal data.
2. Large copied board/wiki/source contents.
3. Temporary implementation details that are already obvious from current files.
4. Unaccepted proposals, rejected assumptions, or speculative claims as durable memory.

Prefer concise memory entries with pointers to file paths instead of copying full content. Redaction blocks unsafe saves before storage; it is a safety gate, not a guarantee that all possible secrets can be detected.

## Contradiction, Staleness, And Forgetting

If recalled memory conflicts with the current request, current workspace instructions, board/wiki artifacts, approved source files, or live validation output, trust the current evidence. Do not silently follow stale memory.

When a durable memory is stale, unsafe, or superseded, do one of the following through visible workflow:

1. Save a newer memory with a clear source reference and mention the superseded lesson in the new content when useful.
2. Use the available memory administration command to retire or forget the old memory when the operator requests cleanup.
3. Record the conflict in the active task timeline when it affects implementation, quality, release, or operator expectations.

Do not create a second source of truth by copying full agent instructions into memory. Keep canonical role workflows and long-form policy in Markdown references, and use memory for compact rules, gotchas, preferences, decisions, and pointers.

## Tool Launch Contract

Prefer installed skill wrappers for normal Codex workspace startup. Resolve the package from the active skill path or `$CODEX_HOME/skills/4dreamteam`; do not hardcode user-specific home directories:

```txt
python3 <installed-4dreamteam-skill>/scripts/4dt-memory.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-search.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-board.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-sources.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-wiki.py <args>
```

Use project scripts when intentionally working inside the 4DreamTeam source checkout:

```txt
npm run memory -- <args>
npm run search -- <args>
npm run board -- <args>
npm run sources -- <args>
npm run 4dt-wiki -- <args>
```

Use console entrypoints only when they are already known to work in the current shell:

```txt
4dt-memory <args>
4dt-search <args>
4dt-board <args>
4dt-sources <args>
4dt-wiki <args>
```

Use direct module fallbacks only when installed wrappers, source scripts, and known-good console entrypoints are unavailable:

```txt
PYTHONPATH=packages/memory/src:packages/search/src python3 -m fourdt_memory.cli <args>
PYTHONPATH=packages/search/src:packages/sources/src:packages/wiki/src:packages/board/src:packages/memory/src python3 -m fourdt_search.cli <args>
PYTHONPATH=packages/board/src python3 -m fourdt_board.cli <args>
PYTHONPATH=packages/sources/src python3 -m fourdt_sources.cli <args>
PYTHONPATH=packages/wiki/src:packages/sources/src python3 -m fourdt_wiki.cli <args>
```

For Python compile/test commands in sandboxed environments, set:

```txt
PYTHONPYCACHEPREFIX=/tmp/4dt-pycache
```

Resolve the launcher once per session and reuse it for startup checks, Wakeup Recall, validation, and exact reads. Do not spend the morning routine probing global `4dt-*` commands before using installed wrappers.

## Storage And Retrieval

SQLite is the authoritative memory store. The memory domain in `4dt-search query --domain memory` reads live SQLite rows and ranks them through the shared `4dt-search` runtime backend. There is no separate persisted retrieval index to rebuild. The framework workflow continues through board timeline entries, wiki pages, and approved sources if memory is unavailable.

## Unified Search Protocol

Use `4dt-search query` as the only discovery search entrypoint for agent work. Choose explicit domains instead of remembering separate search commands:

```txt
4dt-search query "<query>" --domain wiki --json
4dt-search query "<query>" --domain sources --json
4dt-search query "<query>" --domain memory --json
4dt-search query "<query>" --domain board --json
```

Use domain tools for exact reads, writes, validation, and administration. Search results include locators and `getCommand` values; prefer those for full reads after discovery.

Improve recall in this order:

1. Translate non-English or conceptual operator intent into 4-8 English query variants while preserving technical identifiers.
2. Restrict with `--domain` to reduce noise, or use comma-separated domains for intentional cross-domain search.
3. Start with `--match all`; retry with `--match any` when the query is long or exploratory.
4. Use `--field title,path` for known files/pages/tasks, `--field body` for content, and `--field all` as a fallback.
5. Increase `--limit` and `--max-candidates` when recall is thin.
6. Use `--mode extended` for `|`, negation, exact-ish patterns, prefixes, and suffixes.
7. Use `--explain` when validating quality or diagnosing ranking.
8. Use `--index auto` normally, `--index readonly` for quality checks that must not hide missing/stale indexes, and `--index rebuild` after broad workspace changes.

## Import, Export, And Sessions

`4dt-memory export --format jsonl` exports live memory items only. JSONL export may include full accepted memory content and should be treated as local private data.

`4dt-memory export --format json` exports full memory tables, including contract entries, sessions, evidence, and audit log. Treat it as local private data.

`4dt-memory import <file> --format jsonl` is dry-run by default. It writes only with `--apply` and runs the same safety checks as `remember`. `--format json` imports a full memory-table export and is also dry-run by default.

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
