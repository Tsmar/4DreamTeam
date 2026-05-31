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




The common runtime root in board, wiki, sources, search, and memory tooling is `.4dt`. The shared SQLite database at `.4dt/db.sqlite3` is the authoritative store for managed board, wiki, sources, memory, and rebuildable search state. `.4dt/board/tasks` and `.4dt/wiki/pages` are Markdown conversion inputs for existing workspaces, not active mutation surfaces. Board, wiki, sources, and search indexes remain rebuildable. 4dt-search stores rebuildable chunks and manifests in shared database tables.

Board items use frontmatter-shaped metadata plus structured sections reconstructed by `4dt-board`. SQLite tables separate item metadata/body (`board_items`), timeline comments (`board_comments`), and rebuildable index summaries (`board_index`). Board validation checks required metadata, kind, status, filename conventions, board-column consistency, deprecated fields, deprecated sections, and other lifecycle issues. Supported columns and statuses are encoded in the board CLI. Board writes run through SQLite transactions so concurrent tool processes serialize item updates and preserve parallel timeline comments.

Wiki pages use frontmatter fields `id`, `kind`, `title`, `status`, `created_at`, `updated_at`, `owner`, `source_refs`, and `task_refs`. Required sections are Summary, Content, Evidence, Decisions, Open Questions, and Related. Page kinds include overview, product, architecture, domain, flow, contract, schema, decision, devops, changelog, runbook, and source registry. Status values include draft, actual, accepted, superseded, deprecated, and unknown. SQLite tables separate page metadata (`wiki_pages` with explicit columns for id, kind, title, status, owner, refs, timestamps, and extra frontmatter JSON), section content (`wiki_sections`), unique tags (`wiki_tags`), page-tag links (`wiki_page_tags`), rebuildable index summaries (`wiki_index`), and rebuildable full-text rows (`wiki_fts`). Wiki writes run through SQLite transactions so concurrent tool processes serialize updates instead of racing over full Markdown files.

Sources storage is SQLite-authoritative inside the shared `.4dt/db.sqlite3` database. `4dt-sources` keeps a built-in workspace source boundary plus registered external boundaries in `source_registry`, rebuildable inventory rows in `source_inventory`, and index summaries in `source_index`. Inventory entries include active, ignored, forbidden, and missing states with reasons.

Memory storage is SQLite-first and SQLite-authoritative inside the shared `.4dt/db.sqlite3` database. Memory is single-workspace state for the current folder, so memory tables do not carry `workspace_id` namespacing. Tables store durable items, evidence, session state, audit logs, and default contract keys. The CLI exposes schema setup, doctor, reindex, JSONL live-memory import/export, full JSON import/export, sessions, contract keys, defaults, onboarding, and benchmarks. Memory search is live through the shared 4dt-search runtime backend; there is no separate vector database or persisted memory retrieval index.

The shared database can be backed up with `4dt-db backup create --workspace . --json`. The backup command uses SQLite's backup API and writes a consistent copy under `.4dt/backups/` by default.

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
