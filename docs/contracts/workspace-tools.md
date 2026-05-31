---
id: contracts-workspace-tools
kind: contract
title: Workspace Tools Contract
status: actual
created_at: "2026-05-23T07:32:07Z"
updated_at: "2026-06-01T00:00:00Z"
owner: wiki
source_refs: ["sources/4DreamTeam/package.json", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/4dreamteam/references/lead/lifecycle.md", "sources/4DreamTeam/packages/board/src/fourdt_board/cli.py", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py"]
task_refs: ["TASK-0023", "TASK-0024"]
tags: ["backup", "contracts", "migration", "sqlite", "tools"]
---

# Workspace Tools Contract

## Summary

Workspace tools are the stable API for managed state. Agents use 4dt-search for discovery and domain tools for exact reads, writes, administration, and validation instead of directly reading or writing managed storage.

## Content

The workspace model is a script-managed overlay. Agents operate through commands and JSON contracts; storage layout is an implementation detail owned by tools. This keeps lifecycle movement, source boundaries, wiki page shape, validation, search, database maintenance, and memory safety centralized.

`4dt-search` is the unified discovery facade. Agents use `4dt-search query` with explicit domains (`wiki`, `sources`, `board`, or `memory`) before broad reading. Search results include snippets, locators, freshness metadata, and `getCommand` values that point back to authoritative domain tools. Its help documents query modes, `--match any` for exploratory recall, JSON payload sources, and index modes such as `auto`, `readonly`, and `rebuild`. Rebuildable chunks and manifests live in the shared `.4dt/db.sqlite3` database.

`4dt-board` manages epics, tasks, board columns, metadata, sections, timeline comments, validation, repair, and full JSON export/import. Shared SQLite at `.4dt/db.sqlite3` is the authoritative board store; legacy Markdown task directories are conversion input only, not the active mutation surface. Validation must bootstrap current database tables when missing and must not create `.4dt/board/tasks`. Board writes run through SQLite transactions so concurrent comments are preserved instead of racing over one Markdown file. Board import is dry-run by default and requires `--apply` to replace state.

`4dt-wiki` manages the single workspace wiki. Shared SQLite at `.4dt/db.sqlite3` is the authoritative wiki store; release-facing Markdown is produced through export, and full JSON export/import is available for backup or workspace transfer. The tool stores page metadata, stable sections, and tags in separate relational tables, then reconstructs Markdown for reads and exports. It owns page frontmatter, stable sections, page kinds, statuses, initialization, validation, indexing, FTS5-backed search, get, page creation, page updates, section-scoped updates, combined page application, tag administration, export, import, and ADR creation. `4dt-search --domain wiki` uses the wiki FTS5 table as its candidate source when available, then applies the shared 4dt-search ranking/output contract. `section-set` returns page metadata and the section key without echoing replacement content. Agents should use one `page apply` payload when one logical same-page change updates multiple sections or tags. Each section is limited to 32,000 UTF-8 bytes; larger material belongs in separate managed wiki pages linked through `related`. Wiki import is dry-run by default and requires `--apply` to replace state.

`4dt-sources` manages the approved source registry, inventory, stats, search, and safe snippet reads. Shared SQLite at `.4dt/db.sqlite3` is the authoritative sources store: external boundaries live in `source_registry`, rebuildable inventory rows live in `source_inventory`, and index summaries live in `source_index`. The tool honors project-provided `.gitignore` files, but workspace bootstrap must not create `sources/.gitignore` because generated ignore rules can hide useful source material from agents.

`4dt-memory` manages local memory status, initialization, recall, saving, import/export, session state, contract defaults, onboarding questions, mode definitions, and benchmark behavior. Shared SQLite at `.4dt/db.sqlite3` is authoritative for memory tables. Memory is single-workspace state for the current folder and does not use `workspace_id` namespacing. Memory setup creates the current packaged schema only when memory tables are absent; populated older or incomplete schemas report `schema_mismatch` and require operator-controlled backup, comparison, and migration/reset planning. JSONL memory import/export covers live memory items; full JSON memory import/export covers memory items, evidence, sessions, audit log, and contract entries. Memory import is dry-run by default and writes only when `--apply` is explicit.

`4dt-db` manages shared database maintenance. `4dt-db backup create --workspace . --json` writes a consistent SQLite backup copy without printing database contents, and `backup list` lists local backups. `4dt-db schema status --workspace . --json` reports recorded per-domain schema versions and hashes from `tool_schema_versions`. `4dt-db migrate plan/apply` applies reviewed JSON migration specs through SQL-side operations such as column-to-column table copy, defaults, rename, guarded drop, count/not-null/foreign-key validations, and schema registry updates; `apply --backup` creates a database backup first and migration output reports counts and mappings rather than row contents.

The source repository exposes local development scripts in `package.json`: `npm run board`, `npm run memory`, `npm run search`, `npm run search:validate`, `npm run sources`, `npm run db`, `npm run 4dt-wiki`, and `npm run rules`. Tool source and tests live under root `packages/`; the installable skill package lives under `4dreamteam/`. CLI help is part of the agent contract and should describe safe defaults, payload sources, and mode choices when commands have multiple ways to run.

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
- Keep memory as recall below current request, workspace artifacts, board/wiki evidence, and approved sources.
- Agent-friendly CLI contract: generated content should flow through stdin or inline arguments; reusable or reviewed artifacts should use `--file` or `--query-file`; broad discovery starts with `4dt-search`; exact reads use `getCommand`, `--range`, or `--section`; external source boundaries require explicit operator approval.

## Open Questions

- Global shell commands for board/sources/wiki/search/memory are not available in this environment; source-local npm scripts are currently used.
- CI should make the local validation surface mandatory on push and pull request.

## Related

- [Search Domain](../domains/search.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Memory Domain](../domains/memory.md)
- [Wiki Workflow](../flows/wiki-workflow.md)
