---
id: contracts-workspace-tools
kind: contract
title: Workspace Tools Contract
status: actual
created_at: "2026-05-23T07:32:07Z"
updated_at: "2026-06-01T04:03:04Z"
owner: wiki
source_refs: ["sources/4DreamTeam/package.json", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/4dreamteam/references/lead/lifecycle.md", "sources/4DreamTeam/packages/board/src/fourdt_board/cli.py", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py"]
task_refs: ["TASK-0023", "TASK-0024"]
tags: ["backup", "contracts", "migration", "sqlite", "tools"]
---

# Workspace Tools Contract

## Summary

Workspace tool contracts define the stable agent-facing API for managed state. They answer which command owns each read, write, validation, import/export, and browser view without becoming the place for product meaning or table-by-table schema detail.

## Content

The workspace model is a script-managed overlay. Agents operate through command output and JSON contracts; storage layout is an implementation detail owned by tools. This keeps lifecycle movement, source boundaries, wiki page shape, validation, search, database maintenance, local browser surfaces, and memory safety centralized.

Contract boundaries:

- Discovery contract: 4dt-search is the unified discovery facade. Agents search explicit domains before broad reading and then follow getCommand values for exact reads.
- Board contract: 4dt-board owns epics, tasks, columns, metadata, sections, timeline comments, validation, repair, and JSON export/import.
- Wiki contract: 4dt-wiki owns managed pages, sections, tags, status, validation, search/indexing, get, creation, page updates, section updates, combined page apply, export/import, and ADR creation.
- Workspace View contract: 4dt-web owns local read-only browser views over managed workspace state. It is the Workspace View, currently wiki-first, and should stay separate from domain management CLIs.
- Sources contract: 4dt-sources owns approved source boundaries, inventory, stats, search, and safe snippet reads.
- Memory contract: 4dt-memory owns durable memory, evidence, sessions, audit logs, defaults, onboarding questions, mode definitions, and import/export.
- Database contract: 4dt-db owns shared database backup, schema status, and reviewed migration plan/apply operations.

Contract pages should define what agents may call, what each command owns, safe defaults, concurrency expectations, and launch rules. Table names, schema hashes, and migration mechanics belong in Tool Storage Schema. Product promise belongs in Overview.

## Evidence

- `sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py`
- `sources/4DreamTeam/packages/board/src/fourdt_board/cli.py`
- `sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py`
- `sources/4DreamTeam/packages/search/src/fourdt_search/cli.py`
- `sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py`
- `TASK-0023` quality acceptance
- `TASK-0024` release polish
- `sources/4DreamTeam/packages/db/src/fourdt_db/cli.py` defines backup, schema status, and controlled migration commands.
- v0.5.7/v0.5.8 tests cover shared SQLite storage, export/import cycles, schema bootstrap, and no legacy directory creation during validation.

## Decisions

- Treat command output as the interface for managed workspace state.
- Do not inspect or edit managed board/wiki storage directly in agent workflows.
- Use 4dt-search for discovery; use domain tools for exact reads, writes, validation, and administration.
- Keep Workspace View read-only and localhost-bound by default.
- Keep browser UI in 4dt-web so domain tools do not accumulate presentation code.
- Keep memory as recall below current request, workspace artifacts, board/wiki evidence, and approved sources.

## Open Questions

- Global shell commands for board/sources/wiki/search/memory are not available in this environment; source-local npm scripts are currently used.
- CI should make the local validation surface mandatory on push and pull request.

## Related

- [Overview](../start/overview.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Search Domain](../domains/search.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Memory Domain](../domains/memory.md)
- [Wiki](../workflows/wiki.md)
- [Overview](../architecture/overview.md)
