---
id: workflows-wiki
kind: flow
title: Wiki
status: actual
created_at: "2026-05-23T07:32:13Z"
updated_at: "2026-06-01T04:03:29Z"
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/wiki.md", "sources/4DreamTeam/4dreamteam/references/wiki/index.md", "sources/4DreamTeam/4dreamteam/references/wiki/shared/page-shape.md", "sources/4DreamTeam/4dreamteam/references/wiki/bootstrap.md", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py"]
task_refs: ["TASK-0023"]
tags: ["fts", "sqlite", "tags", "wiki", "workflow"]
---

# Wiki

## Summary

The wiki workflow maintains one source-backed workspace knowledge base through 4dt-wiki. It also protects page boundaries: product meaning, workflow behavior, architecture, domains, contracts, and schemas should be updated in their own layers instead of blended into one page.

## Content

Wiki work starts by reading references/wiki.md, then references/wiki/index.md, then shared modules, then the smallest mode file needed for the request. The role supports a single workspace wiki; old multi-project wiki registry and source-map workflows are legacy for new work.

Before changing content, choose the page layer:

- Product pages: purpose, users, value, scope, non-goals, acceptance meaning, and operator-facing product behavior.
- Workflow pages: role movement, handoffs, gates, evidence requirements, and operating procedures.
- Architecture pages: repository layout, runtime entrypoints, installed package boundaries, dependency direction, and package separation.
- Domain pages: one subsystem or capability at a time, including owned commands/files, decisions, evidence, and neighboring domains.
- Contract pages: stable agent-facing APIs, command ownership, safe defaults, launch rules, and concurrency rules.
- Schema pages: storage authority, table ownership, schema versions, backups, migrations, validation, and limits.

Mode selection is simple. Use bootstrap for a new source-backed wiki. Use post-acceptance when accepted quality evidence exists and docs need updating. Use sync to align existing wiki pages with accepted changes or explicitly approved current sources. Use audit or check for read-only review. Use blueprint for proposed future documentation. Use deepening to add implementation detail to existing docs from current sources.

Discovery should start with 4dt-search query using explicit wiki or sources domains. For domain wiki, 4dt-search uses the wiki FTS5 table as its candidate source when available while preserving shared search result payloads and getCommand values. Use result getCommand values or exact 4dt-wiki/4dt-sources commands for full reads. Use 4dt-wiki index build/check for wiki administration and validation, not as the first broad discovery surface.

The wiki role must not read or write wiki storage directly. It must not document rejected or unconfirmed changes as facts. Confirmed pre-development requirements must be marked proposed until source or accepted quality proves implementation. Source-of-truth claims should point to approved sources, accepted timeline evidence, or explicit blueprint assumptions.

Managed pages have stable frontmatter and required sections: Summary, Content, Evidence, Decisions, Open Questions, and Related. Section keys are summary, content, evidence, decisions, open_questions, and related. SQLite is the authoritative wiki store, and old Markdown page files are only a legacy import source or export output. Use page apply when metadata, tags, and multiple sections need to change together from one JSON payload. SQLite transactions serialize managed writes. Parallel reads/searches and independent page writes are allowed; for one logical same-page change, combine section, tag, status, and ref changes into one page apply payload so readers see one coherent update. Larger material belongs in separate managed wiki pages linked through related.

For release documentation, 4dt-wiki export --target <path> renders managed SQLite pages as Markdown into an explicit target under workspace sources/. Export prepares source-shipped documentation but does not bypass release approval gates for staging, committing, pushing, tagging, or publishing. If exported docs contradict current source behavior, update the managed wiki first and export again; direct edits to exported docs will be overwritten by the next managed export.

## Evidence

- `sources/4DreamTeam/4dreamteam/references/wiki/shared/page-shape.md`
- `sources/4DreamTeam/packages/wiki/tests/test_cli.py`
- `TASK-0023` quality acceptance

## Decisions

- Use 4dt-search query for wiki/source discovery before broad reads.
- Use 4dt-wiki for all managed wiki page writes and exact wiki reads.
- Choose the page layer before writing so product, workflow, architecture, domain, contract, and schema facts stay separated.
- Use 4dt-sources for source registry, inventory, exact snippets, and boundary validation.
- Keep managed wiki English-only and agent-facing.
- Treat docs/ as exported release documentation; fix stale content in managed wiki and re-export.

## Open Questions

- Whether post-acceptance wiki updates should automatically include page source refs from related task evidence.
- Whether wiki validation should detect unresolved `TBD` placeholders after bootstrap.

## Related

- [Overview](../start/overview.md)
- [Overview](../product/overview.md)
- [Overview](../architecture/overview.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Documentation Domain](../domains/documentation.md)
