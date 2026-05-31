---
id: domains-search
kind: domain
title: Search Domain
status: actual
created_at: 2026-05-24T10:04:24Z
updated_at: 2026-05-24T10:42:39Z
owner: wiki
source_refs: ["sources/4DreamTeam/packages/search/src/fourdt_search/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/indexer.py", "sources/4DreamTeam/packages/search/src/fourdt_search/storage.py", "sources/4DreamTeam/packages/search/src/fourdt_search/domains/sources.py", "sources/4DreamTeam/packages/search/src/fourdt_search/domains/wiki.py", "sources/4DreamTeam/packages/search/src/fourdt_search/domains/board.py", "sources/4DreamTeam/packages/search/src/fourdt_search/domains/memory.py", "sources/4DreamTeam/4dreamteam/references/lead/memory.md", "sources/4DreamTeam/4dreamteam/references/lead/context-budget.md"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0010", "EPIC-0001-TASK-0011", "EPIC-0001-TASK-0012", "EPIC-0001-TASK-0013"]
---

# Search Domain

## Summary




4dt-search is the unified discovery interface for 4DreamTeam agents. It searches managed wiki, approved sources, board history, and memory through one CLI while preserving domain authority and exact-read commands.

## Content




Agents use `4dt-search query` before broad discovery across wiki, sources, board, or memory. The agent translates operator intent into concise English search terms while preserving exact technical identifiers such as task ids, command names, filenames, and package names.

Supported domains are `wiki`, `sources`, `board`, and `memory`. Wiki, sources, and board are rebuildable indexed domains stored in `.4dt/db.sqlite3` tables `search_chunks` and `search_manifest`. Memory is live: it reads SQLite rows directly and ranks them through the shared 4dt-search runtime backend, so there is no separate persisted memory search index to rebuild.

The CLI exposes `index build`, `index check`, `stats`, `search`, `query`, and `get`. `query` is the preferred agent-facing alias for search. The index mode can be `auto`, `readonly`, or `rebuild`; auto checks for a missing or stale index and builds it before answering. Advanced controls include domains, fields, match mode, search mode, threshold, location filters, include/exclude paths, result limits, and JSON query syntax.

Search results include domain, kind, authority, score, snippet, locator, freshness metadata, and a `getCommand`. The `getCommand` points back to the authoritative domain tool (`4dt-wiki`, `4dt-sources`, `4dt-board`, or `4dt-memory`) for exact reads. Search previews help choose what to read, but important facts must be verified through the exact domain read before changing behavior.

4dt-search does not expand source permissions. The sources domain uses 4dt-sources boundaries and exclusions, wiki uses managed wiki pages, board uses 4dt-board items and timeline entries, and memory remains supplemental recall below current request, workspace instructions, accepted board evidence, wiki pages, and approved source files.

## Evidence




- `packages/search/src/fourdt_search/cli.py` defines CLI commands, query alias, domain selection, index mode, filters, JSON output, and get behavior.
- `packages/search/src/fourdt_search/indexer.py` and `storage.py` define rebuildable search chunks and manifest storage in `.4dt/db.sqlite3`.
- `packages/search/src/fourdt_search/domains/*.py` define domain collectors and authoritative get command metadata.
- `packages/memory/src/fourdt_memory/search_backend.py` connects live SQLite memory rows to the shared search scoring backend.
- EPIC-0001 accepted tasks provide implementation, integration, benchmark, advanced CLI, and memory-backend acceptance evidence.

## Decisions




- Use `4dt-search query` as the first discovery interface for agents across wiki, sources, board, and memory.
- Keep exact writes, administration, validation, and authoritative reads in the domain-owned tools.
- Keep search indexes rebuildable and below source/wiki/board authority.
- Use live SQLite-backed memory search instead of embeddings or vector retrieval.

## Open Questions




- CI should enforce search, memory, board, wiki, and source tests on push and pull request.
- Future relevance improvements should focus on agent query translation, scoring fixtures, and domain-specific quality cases before adding external dependencies.

## Related




- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Memory Domain](memory.md)
- [Source Boundaries Domain](source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
