---
id: domains-memory
kind: domain
title: Memory Domain
status: actual
created_at: 2026-05-23T07:32:22Z
updated_at: 2026-05-25T03:44:53Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/lead/memory.md", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/sqlite_store.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/search_backend.py", "sources/4DreamTeam/packages/search/src/fourdt_search/scoring.py"]
task_refs: ["EPIC-0001-TASK-0013", "TASK-0017"]
---

# Memory Domain

## Summary






4DT Memory is optional local recall. SQLite is authoritative for memory storage, and memory retrieval uses the shared 4dt-search runtime backend over live SQLite rows. Memory now has explicit operator-intent, placement, role-scoped recall, and bounded startup/task recall policy; it never outranks current request, workspace artifacts, accepted timeline evidence, wiki pages, or approved sources.

## Content







The memory authority order is current user request and explicit approvals, current workspace instructions and tool-managed artifacts, approved source files, then 4DT Memory recalls and session state. Memory is a navigation and continuity layer, not a source of truth.

New-session memory flow starts with `4dt-memory doctor --workspace . --json`. When ready, the lead loads contract defaults with `4dt-memory defaults load --workspace . --json`. Defaults define project rules, current mode, mode definitions, operator preferences, approval policy, source policy, git policy, validation policy, and communication style. After defaults, agents must not dump all memory into context; supplemental recall is bounded and used only when route, role, continuation state, or operator request makes prior lessons relevant.

Operator memory intent may be expressed in any language. Durable memory content is stored in English for portability, cross-agent recall, and consistent 4dt-search ranking. Exact commands, file paths, task ids, CLI names, code identifiers, and localized user-facing text are preserved when they are the fact being remembered.

Operator memory intent is recognized from natural language such as "remember", "запомни", "нужно запомнить", "чтобы в следующий раз не изучать", noisy-log/context-waste corrections, and corrective lessons. The policy classifies requests as `direct_save`, `investigate_then_save`, `behavior_change_plus_lesson`, or `do_not_save`. Memory intent never bypasses source boundaries, approval gates, role workflow, or independent quality.

Memory placement uses the narrowest durable scope: `workspace` for operating rules and source boundaries, `project` for cross-role architecture/process/testing/logging knowledge, `role --role ROLE` for role-specific lessons such as developer test commands or quality acceptance traps, and `user` for stable operator preferences. Durable types include `implementation_lesson`, `gotcha`, `operator_preference`, `process_instruction`, and `decision`.

Storage is workspace-local and tool-managed. SQLite stores memory items, evidence, workspace identity, session state, audit logs, and default contract keys. Search is live: `4dt-search query --domain memory` reads SQLite rows and ranks them through the shared 4dt-search scoring backend. There is no embedding provider, vector table, or separate persisted memory retrieval index in the current architecture.

The CLI supports initialization, doctor, list, search, reindex, export/import, session state, defaults, keys, modes, onboarding, benchmark, get, remember, and forget. Durable memory should be concise, accepted, useful across sessions, and source-referenced. It must not store secrets, credentials, private keys, `.env` contents, dumps, production data, large copied artifacts, temporary implementation details, or unaccepted speculative claims.

For multilingual user requests, managed knowledge artifacts are English-first. The memory protocol translates conceptual queries into bounded English variants while preserving technical terms such as commands, filenames, task ids, SQLite, 4dt-search, and package names. Role/task recall uses small enriched queries and exact reads only for hits that may change the plan. Important hits must be verified against authoritative artifacts before changing behavior.

## Evidence







- `4dreamteam/references/lead/memory.md` defines authority order, recall flow, operator memory intent, placement policy, role-scoped recall, save flow, stale-memory handling, and unified search usage.
- `4dreamteam/references/lead/preflight.md` defines startup defaults loading and bounded supplemental memory recall after contract defaults.
- `packages/memory/src/fourdt_memory/cli.py` defines contract keys, defaults, mode fields, onboarding questions, degraded statuses, and commands.
- `packages/memory/src/fourdt_memory/sqlite_store.py` and `schema.sql` define the authoritative SQLite store.
- `packages/memory/src/fourdt_memory/search_backend.py` adapts memory rows to the shared 4dt-search runtime backend.
- EPIC-0001-TASK-0013 accepted quality evidence backs removal of vector retrieval from active memory code.
- TASK-0017 accepted quality evidence backs operator-intent, placement, role-scoped recall, and bounded startup/task recall policy.

## Decisions






- Do not fail 4DreamTeam workflow because memory is degraded or unavailable.
- Treat contract defaults as stricter than supplemental recall when memory is ready.
- Do not dump all memory into startup context; use bounded role/task-enriched recall only when useful.
- Recognize natural-language operator memory intent, but classify it before saving and keep normal workflow gates intact.
- Place memory in the narrowest durable scope: workspace, project, role, or user.
- Verify memory hits against board, wiki, or approved sources before making strong claims.
- Keep SQLite as the memory authority and 4dt-search as the runtime retrieval backend.
- Trust current request, accepted artifacts, approved sources, and live validation over stale or conflicting memory.

## Open Questions






- Decide whether additional benchmark fixtures are needed for long-term memory retrieval quality.
- Decide whether memory onboarding should persist more project-specific defaults during workspace initialization.
- Decide whether a future `4dt-memory classify-intent` or `plan-save` helper is needed if policy-only memory-intent behavior is not reliable enough.

## Related






- [Memory Human Analogy](memory-human-analogy.md)
- [Search Domain](search.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Source Boundaries Domain](source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
