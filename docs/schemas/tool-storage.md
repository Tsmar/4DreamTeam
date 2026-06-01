---
id: schemas-tool-storage
kind: schema
title: Tool Storage Schema
status: actual
created_at: "2026-05-23T07:32:29Z"
updated_at: "2026-06-01T04:03:04Z"
owner: wiki
source_refs: ["sources/4DreamTeam/packages/board/src/fourdt_board/cli.py", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/storage.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/paths.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/schema.sql", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/migrations.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0013", "EPIC-0002-TASK-0014"]
tags: ["migration", "schema", "sqlite", "storage"]
---

# Tool Storage Schema

## Summary

Tool Storage Schema owns the storage-authority layer: runtime roots, SQLite authority, domain tables, schema registry, backups, migrations, and validation expectations. It should not carry product value or role workflow explanations except as context for storage safety.

## Content

The common runtime root is .4dt, and the shared SQLite database at .4dt/db.sqlite3 is the authoritative store for managed board, wiki, sources, memory, and rebuildable search state. Domain-specific legacy folders are not active mutation surfaces: Markdown board tasks and wiki pages are conversion inputs or export outputs, old source registry/index files are obsolete, and search chunks/manifests are database rows rather than .4dt/search JSONL files.

Storage boundaries:

- Board tables store item metadata/body, timeline comments, and rebuildable index summaries. Board writes run through SQLite transactions so concurrent timeline comments are preserved.
- Wiki tables store page metadata, section content, tags, page-tag links, rebuildable index summaries, and FTS rows. Wiki sections are limited to 32,000 UTF-8 bytes; larger material belongs in related pages.
- Sources tables store approved boundaries, rebuildable inventory rows, and index summaries. Workspace sources/ remains the built-in source boundary.
- Memory tables store durable items, evidence, session state, audit logs, and default contract keys without workspace_id namespacing. Populated mismatched schemas require operator-controlled migration/reset planning.
- Search tables store rebuildable chunks and manifests. The memory search domain remains live over SQLite rows.
- 4dt-web is read-only over managed state and currently owns no database tables.
- tool_schema_versions records each domain schema version, schema hash, tool version, and applied timestamp.

Schema pages should define authority, table ownership, backup/migration expectations, validation behavior, and known limits. Agent-facing command semantics belong in Workspace Tools Contract. Repository package layout belongs in Overview.

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

- Treat .4dt/db.sqlite3 as the shared authoritative store for board, wiki, sources, memory, and rebuildable search state.
- Treat legacy domain folders as conversion inputs, export outputs, or obsolete implementation details, not active mutation surfaces.
- Use domain CLIs for reads, writes, validation, import/export, and search rather than direct table edits.
- Record per-domain schema versions and hashes in tool_schema_versions.
- Back up before schema-changing upgrades and use operator-approved migration specs for SQL-side data movement.
- Do not silently migrate populated mismatched memory schemas during startup.
- Validation should bootstrap missing current tables without creating legacy domain directories.

## Open Questions

- Whether future schema specs should be generated directly from tool-owned schema definitions.
- Whether board/wiki/sources/search should adopt the same strict no-auto-migration policy as memory once schema versions begin changing.

## Related

- [Overview](../start/overview.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Overview](../architecture/overview.md)
- [Search Domain](../domains/search.md)
- [Wiki](../workflows/wiki.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Memory Domain](../domains/memory.md)
