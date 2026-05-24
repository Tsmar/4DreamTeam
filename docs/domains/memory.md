---
id: domains-memory
kind: domain
title: Memory Domain
status: actual
created_at: 2026-05-23T07:32:22Z
updated_at: 2026-05-24T10:42:38Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/lead/memory.md", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/sqlite_store.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/search_backend.py", "sources/4DreamTeam/packages/search/src/fourdt_search/scoring.py"]
task_refs: ["EPIC-0001-TASK-0013"]
---

# Memory Domain

## Summary





4DT Memory is optional local recall. SQLite is authoritative for memory storage, and memory retrieval uses the shared 4dt-search runtime backend over live SQLite rows; memory never outranks current request, workspace artifacts, accepted timeline evidence, wiki pages, or approved sources.

## Content





The memory authority order is current user request and explicit approvals, current workspace instructions and tool-managed artifacts, approved source files, then 4DT Memory recalls and session state. Memory is a navigation and continuity layer, not a source of truth.

New-session memory flow starts with `4dt-memory doctor --workspace . --json`. When ready, the lead loads contract defaults with `4dt-memory defaults load --workspace . --json`. Defaults define project rules, current mode, mode definitions, operator preferences, approval policy, source policy, git policy, validation policy, and communication style. If defaults are incomplete, onboarding questions should be asked instead of inventing remembered rules.

Storage is workspace-local and tool-managed. SQLite stores memory items, evidence, workspace identity, session state, audit logs, and default contract keys. Search is live: `4dt-search query --domain memory` reads SQLite rows and ranks them through the shared 4dt-search scoring backend. There is no embedding provider, vector table, or separate persisted memory retrieval index in the current architecture.

The CLI supports initialization, doctor, list, search, reindex, export/import, session state, defaults, keys, modes, onboarding, benchmark, get, remember, and forget. Durable memory should be concise, accepted, useful across sessions, and source-referenced. It must not store secrets, credentials, private keys, `.env` contents, dumps, production data, large copied artifacts, temporary implementation details, or unaccepted speculative claims.

For multilingual user requests, managed knowledge artifacts are English-first. The memory protocol translates conceptual queries into bounded English variants while preserving technical terms such as commands, filenames, task ids, SQLite, 4dt-search, and package names. Important hits must be verified against authoritative artifacts before changing behavior.

## Evidence






- `4dreamteam/references/lead/memory.md` defines authority order, recall flow, save flow, startup checks, and the unified search usage pattern.
- `packages/memory/src/fourdt_memory/cli.py` defines contract keys, defaults, mode fields, onboarding questions, degraded statuses, and commands.
- `packages/memory/src/fourdt_memory/sqlite_store.py` and `schema.sql` define the authoritative SQLite store.
- `packages/memory/src/fourdt_memory/search_backend.py` adapts memory rows to the shared 4dt-search runtime backend.
- EPIC-0001-TASK-0013 accepted quality evidence backs removal of vector retrieval from active memory code.

## Decisions





- Do not fail 4DreamTeam workflow because memory is degraded or unavailable.
- Treat contract defaults as stricter than supplemental recall when memory is ready.
- Verify memory hits against board, wiki, or approved sources before making strong claims.
- Keep SQLite as the memory authority and 4dt-search as the runtime retrieval backend.

## Open Questions





- Decide whether additional benchmark fixtures are needed for long-term memory retrieval quality.
- Decide whether memory onboarding should persist more project-specific defaults during workspace initialization.

## Related





- [Search Domain](search.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Source Boundaries Domain](source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
