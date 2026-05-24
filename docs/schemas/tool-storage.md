---
id: schemas-tool-storage
kind: schema
title: Tool Storage Schema
status: actual
created_at: 2026-05-23T07:32:29Z
updated_at: 2026-05-24T10:42:41Z
owner: wiki
source_refs: ["sources/4DreamTeam/packages/board/src/fourdt_board/cli.py", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/storage.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/paths.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/schema.sql"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0013", "EPIC-0002-TASK-0014"]
---

# Tool Storage Schema

## Summary




Managed storage is under workspace runtime areas and is owned by tools. Agents interact through commands and validation, not direct storage edits.

## Content




The common runtime root in board, wiki, sources, and search tooling is `.4dt`. Board storage is under `.4dt/board/tasks` with column directories and a board index. Wiki storage is under `.4dt/wiki/pages` with a wiki index. Source registry and inventory live under `.4dt/sources`. 4dt-search stores rebuildable chunks and manifests under `.4dt/search/`. Memory uses workspace-local SQLite storage, sessions, and related runtime data.

Board files use frontmatter plus structured sections. Board validation checks required frontmatter, kind, status, filename conventions, board-column consistency, deprecated fields, deprecated sections, and other lifecycle issues. Supported columns and statuses are encoded in the board CLI.

Wiki pages use frontmatter fields `id`, `kind`, `title`, `status`, `created_at`, `updated_at`, `owner`, `source_refs`, and `task_refs`. Required sections are Summary, Content, Evidence, Decisions, Open Questions, and Related. Page kinds include overview, product, architecture, domain, flow, contract, schema, decision, devops, changelog, runbook, and source registry. Status values include draft, actual, accepted, superseded, deprecated, and unknown.

Sources storage includes a registry file and generated index/manifest. `4dt-sources` keeps a built-in workspace source boundary plus registered external boundaries. Inventory entries include active, ignored, forbidden, and missing states with reasons.

Memory storage is SQLite-first and SQLite-authoritative. The CLI exposes schema migration, doctor, reindex, import/export, sessions, contract keys, defaults, onboarding, and benchmarks. Memory search is live through the shared 4dt-search runtime backend; there is no separate vector database or persisted memory retrieval index.

Repository tool source and tests live under root `packages/`. The installable skill package under `4dreamteam/` contains instructions, references, templates, agents metadata, and helper scripts, not tool source trees.

Validation is part of the storage contract. Startup and handoff flows should run tool validation commands and report tool-specific state rather than inferring health from folder inspection.

## Evidence





- `packages/board/src/fourdt_board/cli.py` defines board storage and commands.
- `packages/wiki/src/fourdt_wiki/cli.py` defines wiki storage, validation, page commands, and export.
- `packages/sources/src/fourdt_sources/cli.py` defines source registry, inventory, search, get, and exclusion behavior.
- `packages/search/src/fourdt_search/storage.py` defines rebuildable search chunk and manifest storage.
- `packages/memory/src/fourdt_memory/paths.py` and `schema.sql` define memory storage paths and schema.
- EPIC-0002-TASK-0014 accepted quality evidence backs root `packages/` source separation from the skill package.

## Decisions




- Treat `.4dt` as tool-managed runtime storage.
- Prefer validation commands over manual folder inspection when reporting workspace state.
- Keep generated indexes rebuildable and below source/board/wiki authority.
- Keep tool source outside the installable skill package.

## Open Questions




- Whether wiki validation should enforce source_refs syntax beyond JSON-array string shape.
- Whether board, wiki, sources, memory, and search tools should share a small common frontmatter/section utility library in the future.

## Related




- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Search Domain](../domains/search.md)
- [Wiki Workflow](../flows/wiki-workflow.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Memory Domain](../domains/memory.md)
