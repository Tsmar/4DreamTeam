---
id: domains-memory
kind: domain
title: Memory Domain
status: actual
created_at: 2026-05-23T07:32:22Z
updated_at: 2026-05-23T08:40:12Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/lead/memory.md", "sources/4DreamTeam/4dreamteam/tools/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/4dreamteam/tools/memory/src/fourdt_memory/lance_index.py", "sources/4DreamTeam/4dreamteam/tools/memory/src/fourdt_memory/embedder.py"]
task_refs: []
---

# Memory Domain

## Summary


4DT Memory is optional local recall. SQLite is authoritative for memory storage; LanceDB is an experimental rebuildable index; memory never outranks current request, workspace artifacts, accepted timeline evidence, or approved sources.

## Content


The memory authority order is current user request and explicit approvals, current workspace instructions and tool-managed artifacts, approved source files, then 4DT Memory recalls and session state. Memory is a navigation and continuity layer, not a source of truth.

New-session memory flow starts with `4dt-memory doctor --workspace . --json`. When ready, the lead loads contract defaults with `4dt-memory defaults load --workspace . --json`. Defaults define project rules, current mode, mode definitions, operator preferences, approval policy, source policy, git policy, validation policy, and communication style. If defaults are incomplete, onboarding questions should be asked instead of inventing remembered rules.

Storage is workspace-local and tool-managed. SQLite stores memory items, evidence, workspace identity, session state, and audit logs. LanceDB is a rebuildable vector index intended to improve retrieval quality. If LanceDB, embeddings, or metadata are unavailable, workflows continue using board timeline evidence, wiki pages, and approved sources.

The CLI supports initialization, doctor, list, search, reindex, export/import, session state, defaults, keys, modes, onboarding, benchmark, get, remember, and forget. Durable memory should be concise, accepted, useful across sessions, and source-referenced. It must not store secrets, credentials, private keys, `.env` contents, dumps, production data, large copied artifacts, temporary implementation details, or unaccepted speculative claims.

For multilingual user requests, managed knowledge artifacts are English-first. The memory protocol translates conceptual queries into bounded English variants while preserving technical terms such as commands, filenames, task ids, SQLite, LanceDB, and package names. Important hits must be verified against authoritative artifacts before changing behavior.

## Evidence



- `sources/4DreamTeam/4dreamteam/references/lead/memory.md` defines authority order, recall flow, save flow, and benchmark expectations.
- `sources/4DreamTeam/4dreamteam/tools/memory/src/fourdt_memory/cli.py` defines contract keys, mode fields, onboarding questions, degraded statuses, and commands.
- `sources/4DreamTeam/4dreamteam/tools/memory/src/fourdt_memory/lance_index.py` and `embedder.py` implement index and embedding-provider behavior.

## Decisions


- Do not fail 4DreamTeam workflow because memory is degraded or unavailable.
- Treat contract defaults as stricter than supplemental semantic recall when memory is ready.
- Verify memory hits against board, wiki, or approved sources before making strong claims.

## Open Questions


- This workspace has initialized SQLite memory, but contract defaults are incomplete.
- Local LanceDB setup currently has a dependency compatibility problem: tested `lancedb` 0.27.1 and 0.26.1 both failed direct import with `CreateEmptyTableRequest` missing from `lance_namespace`; this is saved as memory `mem_431f2d0d86ce493f97fac683624a23bb`.
- `4dt-memory doctor` may need stronger real-import/connect/create-table validation for LanceDB availability.

## Related


- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Source Boundaries Domain](source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
