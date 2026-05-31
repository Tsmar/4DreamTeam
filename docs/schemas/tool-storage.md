---
id: schemas-tool-storage
kind: schema
title: Tool Storage Schema
status: actual
created_at: "2026-05-23T07:32:29Z"
updated_at: "2026-06-01T00:00:00Z"
owner: wiki
source_refs: ["sources/4DreamTeam/packages/board/src/fourdt_board/cli.py", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/storage.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/paths.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/schema.sql", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/migrations.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0013", "EPIC-0002-TASK-0014"]
tags: ["migration", "schema", "sqlite", "storage"]
---

# Tool Storage Schema

## Summary

Managed storage is under workspace runtime areas and is owned by tools. Agents interact through commands and validation, not direct storage edits.

## Content

The common runtime root is `.4dt`, and the shared SQLite database at `.4dt/db.sqlite3` is the authoritative store for managed board, wiki, sources, memory, and rebuildable search state. Domain-specific legacy folders are not active mutation surfaces: Markdown board tasks and wiki pages are conversion inputs or export outputs, old source registry/index files are obsolete, and search chunks/manifests are database rows rather than `.4dt/search` JSONL files.

Every tool owns its schema and query/write API. Agents should use `4dt-board`, `4dt-wiki`, `4dt-sources`, `4dt-memory`, `4dt-search`, and `4dt-db` instead of editing database tables or generated files directly.

Board tables store item metadata/body (`board_items`), timeline comments (`board_comments`), and rebuildable index summaries (`board_index`). Board validation checks required metadata, kind, status, filename conventions, board-column consistency, deprecated fields, deprecated sections, and other lifecycle issues. Board writes run through SQLite transactions so concurrent timeline comments are preserved.

Wiki tables store page metadata (`wiki_pages`), section content (`wiki_sections`), unique tags (`wiki_tags`), page-tag links (`wiki_page_tags`), rebuildable index summaries (`wiki_index`), and FTS rows (`wiki_fts`). Wiki page frontmatter uses `id`, `kind`, `title`, `status`, `created_at`, `updated_at`, `owner`, `source_refs`, and `task_refs`. Required sections are Summary, Content, Evidence, Decisions, Open Questions, and Related. Each section is limited to 32,000 UTF-8 bytes; larger material should be split into related pages. Wiki tags are durable semantic labels for domain, component, workflow, source area, and decision topic discovery.

Sources tables store approved external boundaries in `source_registry`, rebuildable inventory rows in `source_inventory`, and index summaries in `source_index`. Workspace `sources/` remains the built-in source boundary. Source indexing and safe reads honor forbidden/ignored patterns and project-provided `.gitignore` files, but bootstrap must not create `sources/.gitignore`.

Memory tables store durable items, evidence, session state, audit logs, and default contract keys in the shared database without `workspace_id` namespacing. Memory setup creates the current packaged schema only when memory tables are absent. Existing populated mismatched memory schemas report `schema_mismatch` and require operator-controlled backup, comparison, and migration/reset planning rather than silent startup migration.

Search tables store rebuildable chunks and manifests in `search_chunks` and `search_manifest`. The memory domain remains live over SQLite rows; wiki search can use `wiki_fts` for candidate selection before shared ranking/output formatting.

The shared `tool_schema_versions` registry records each domain's schema version, schema hash, tool version, and applied timestamp. Board, wiki, sources, search, and memory record their schema state when they create or validate current tables. `4dt-db schema status --workspace . --json` is the supported inspection surface for this registry.

The shared database can be backed up with `4dt-db backup create --workspace . --json`; the backup command uses SQLite's backup API and writes a consistent copy under `.4dt/backups/` by default. Schema-changing upgrades should use backup first and reviewed migration specs through `4dt-db migrate plan/apply`. The migration runner performs SQL-side column-to-column copies, defaults, renames, guarded drops, validations, and schema registry updates without exposing row contents in agent output.

Repository tool source and tests live under root `packages/`. The installable skill package under `4dreamteam/` contains instructions, references, templates, agent metadata, and helper scripts. Installed wrappers delegate to the generated `4dreamteam/scripts/4dt-tools.pyz` runtime archive.

Validation is part of the storage contract. Startup and handoff flows should run tool validation commands and report tool-specific state rather than inferring health from folder inspection. Validation should create missing current tables, record schema state, and avoid creating legacy domain directories.

## Evidence

- `packages/board/src/fourdt_board/cli.py` defines board tables, transaction-backed writes, validation, import/export, and board schema recording.
- `packages/wiki/src/fourdt_wiki/cli.py` defines wiki tables, section storage, tags, FTS, validation, import/export, and wiki schema recording.
- `packages/sources/src/fourdt_sources/cli.py` defines source registry, inventory, search/get exclusion behavior, and sources schema recording.
- `packages/search/src/fourdt_search/storage.py` defines rebuildable search chunk and manifest tables plus search schema recording.
- `packages/memory/src/fourdt_memory/schema.sql` and `migrations.py` define memory tables, package-data schema loading, current-schema setup, and strict schema mismatch behavior.
- `packages/db/src/fourdt_db/cli.py` defines shared database backup, schema status, and controlled migration plan/apply commands.
- v0.5.7 tests cover shared SQLite authority, concurrent board/wiki writes, wiki tags/FTS, sources/search database storage, and full JSON export/import for wiki/board/memory.
- v0.5.8 tests cover per-domain schema recording, startup bootstrap without legacy directories, strict memory schema mismatch handling, and migration output that does not leak row contents.

## Decisions

- Treat `.4dt/db.sqlite3` as the shared authoritative store for board, wiki, sources, memory, and rebuildable search state.
- Treat legacy domain folders as conversion inputs, export outputs, or obsolete implementation details, not active mutation surfaces.
- Use domain CLIs for reads, writes, validation, import/export, and search rather than direct table edits.
- Record per-domain schema versions and hashes in `tool_schema_versions`.
- Back up before schema-changing upgrades and use operator-approved migration specs for SQL-side data movement.
- Do not silently migrate populated mismatched memory schemas during startup.
- Validation should bootstrap missing current tables without creating legacy domain directories.

## Open Questions

- Whether future schema specs should be generated directly from tool-owned schema definitions.
- Whether board/wiki/sources/search should adopt the same strict no-auto-migration policy as memory once schema versions begin changing.

## Related

- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Search Domain](../domains/search.md)
- [Wiki Workflow](../flows/wiki-workflow.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Memory Domain](../domains/memory.md)
