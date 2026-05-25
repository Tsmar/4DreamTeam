---
id: domains-memory
kind: domain
title: Memory Domain
status: actual
created_at: 2026-05-23T07:32:22Z
updated_at: 2026-05-25T05:34:15Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/lead/memory.md", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/README.md", "sources/4DreamTeam/README.ru.md", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/sqlite_store.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/search_backend.py", "sources/4DreamTeam/packages/search/src/fourdt_search/scoring.py"]
task_refs: ["EPIC-0001-TASK-0013", "TASK-0017", "TASK-0021", "TASK-0022"]
---

# Memory Domain

## Summary







4DT Memory is optional local recall. SQLite is authoritative for storage, memory retrieval uses the shared 4dt-search runtime backend, and Wake Context is the startup continuation layer that lets a new session resume from compact handoffs instead of a noisy transcript.

## Content








The memory authority order is current user request and explicit approvals, current workspace instructions and tool-managed artifacts, approved source files, then 4DT Memory recalls and session state. Memory is a navigation and continuity layer, not a source of truth.

New-session memory flow starts with 4dt-memory doctor --workspace . --json. When ready, the lead loads contract defaults with 4dt-memory defaults load --workspace . --json. After defaults, Wakeup Recall checks pending startup instructions, one-time operator messages, and the latest session handoff before broad board/wiki/source discovery. Delivered one-time messages are retired when their metadata or content requires delete-after-delivery behavior.

Wake Context follows the human memory analogy now described in the README files: after a session, useful context should settle into memory, board evidence, and wiki pointers; at the next start, the agent should wake with the next step in mind rather than carrying the whole prior chat.

Startup tooling is wrapper-first in Codex workspaces. Agents resolve the installed 4DreamTeam skill package from the active skill path or CODEX_HOME/skills/4dreamteam and use scripts/4dt-*.py wrappers first. Console 4dt-* commands are optional shortcuts only after they are known to work in the current shell.

Operator memory intent may be expressed in any language. Durable memory content is stored in English for portability, cross-agent recall, and consistent 4dt-search ranking. Exact commands, file paths, task ids, CLI names, code identifiers, and localized user-facing text are preserved when they are the fact being remembered.

Storage is workspace-local and tool-managed. SQLite stores memory items, evidence, workspace identity, session state, audit logs, and default contract keys. Search is live: 4dt-search query --domain memory reads SQLite rows and ranks them through the shared 4dt-search scoring backend.

## Evidence








- 4dreamteam/references/lead/memory.md defines authority order, Wake Context, Wakeup Recall, operator memory intent, placement policy, role-scoped recall, save flow, stale-memory handling, and unified search usage.
- 4dreamteam/references/lead/preflight.md defines startup defaults loading, wrapper-first tool launch, and Wakeup Recall after contract defaults.
- README.md and README.ru.md include the short human/agent Wake Context analogy.
- TASK-0021 accepted quality evidence backs wrapper-first startup and measured startup improvement from 53 seconds to 36 seconds.
- TASK-0022 accepted quality evidence backs README and release documentation updates.
- EPIC-0001-TASK-0013 accepted quality evidence backs removal of vector retrieval from active memory code.
- TASK-0017 accepted quality evidence backs operator-intent, placement, role-scoped recall, and bounded startup/task recall policy.

## Decisions







- Do not fail 4DreamTeam workflow because memory is degraded or unavailable.
- Treat contract defaults as stricter than supplemental recall when memory is ready.
- Run Wakeup Recall after contract defaults and before broad discovery in confirmed 4DreamTeam workspaces.
- Do not dump all memory into startup context; use bounded role/task-enriched recall only when useful.
- Resolve installed skill wrappers first for startup tooling in Codex sessions.
- Recognize natural-language operator memory intent, but classify it before saving and keep normal workflow gates intact.
- Place memory in the narrowest durable scope: workspace, project, role, or user.
- Verify memory hits against board, wiki, or approved sources before making strong claims.

## Open Questions







- Decide whether additional benchmark fixtures are needed for long-term memory retrieval quality.
- Decide whether a future 4dt-memory classify-intent or plan-save helper is needed if policy-only memory-intent behavior is not reliable enough.

## Related







- [Memory Human Analogy](memory-human-analogy.md)
- [Search Domain](search.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Source Boundaries Domain](source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
