---
id: flows-wiki-workflow
kind: flow
title: Wiki Workflow
status: actual
created_at: "2026-05-23T07:32:13Z"
updated_at: "2026-06-01T00:00:00Z"
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/wiki.md", "sources/4DreamTeam/4dreamteam/references/wiki/index.md", "sources/4DreamTeam/4dreamteam/references/wiki/shared/page-shape.md", "sources/4DreamTeam/4dreamteam/references/wiki/bootstrap.md", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py"]
task_refs: ["TASK-0023"]
tags: ["fts", "sqlite", "tags", "wiki", "workflow"]
---

# Wiki Workflow

## Summary

The wiki workflow maintains the single workspace knowledge base through `4dt-wiki`, using `4dt-sources` for approved source navigation and mode-specific rules for bootstrap, sync, audit, check, blueprint, and deepening.

## Content

Wiki work starts by reading `references/wiki.md`, then `references/wiki/index.md`, then shared modules, then the smallest mode file needed for the request. The role supports a single workspace wiki; old multi-project wiki registry and source-map workflows are legacy for new work.

Mode selection is simple. Use bootstrap for a new source-backed wiki. Use post-acceptance when accepted quality evidence exists and docs need updating. Use sync to align existing wiki pages with accepted changes or explicitly approved current sources. Use audit or check for read-only review. Use blueprint for proposed future documentation. Use deepening to add implementation detail to existing docs from current sources.

Discovery should start with `4dt-search query` using explicit `wiki` or `sources` domains. For `--domain wiki`, `4dt-search` uses the wiki FTS5 table as its candidate source when available while preserving shared search result payloads and `getCommand` values. Use result `getCommand` values or exact `4dt-wiki`/`4dt-sources` commands for full reads. Use `4dt-wiki index build/check` for wiki administration and validation, not as the first broad discovery surface.

Bootstrap flow requires an intake summary before writing unless defaults or auto mode are explicitly accepted. It checks approved sources with `4dt-sources registry list`, initializes wiki storage with `4dt-wiki init`, creates or updates managed pages through `4dt-wiki`, assigns durable semantic tags to imported pages, builds and checks the index, and validates with `4dt-wiki validate`.

The wiki role must not read or write wiki storage directly. It must not document rejected or unconfirmed changes as facts. Confirmed pre-development requirements must be marked proposed until source or accepted quality proves implementation. Source-of-truth claims should point to approved sources, accepted timeline evidence, or explicit blueprint assumptions.

Managed pages have stable frontmatter and required sections: Summary, Content, Evidence, Decisions, Open Questions, and Related. Section keys are `summary`, `content`, `evidence`, `decisions`, `open_questions`, and `related`. SQLite is the authoritative wiki store, and old Markdown page files are only a legacy import source or export output. For focused edits, agents should prefer `4dt-wiki get <page-or-id> --section <section>` and `4dt-wiki page section-set <page-or-id> <section> --content <text>` or stdin instead of full-page reads or rewrites. `section-set` does not echo replacement content; use a focused `get --section` only when read-back is needed. Use `4dt-wiki page apply <page-or-id>` when metadata, tags, and multiple sections need to change together from one JSON payload. Manage semantic labels with `4dt-wiki page create --tag`, `page apply` tags, or `4dt-wiki page tags add/remove/set`; inspect the controlled tag set with `4dt-wiki tags list`. Tags should describe durable domain, component, workflow, source-area, or decision topics, and wiki agents must keep them aligned when importing, adding, or changing pages. For agent-generated JSON payloads, omit `--file` and pass JSON through stdin; use `--file` only when the payload already exists as a reusable, reviewed, or operator-provided artifact. SQLite transactions serialize concurrent wiki writes; for one logical same-page change, combine section and tag changes into one `page apply` payload so readers see them as one update. Each wiki section is limited to 32,000 UTF-8 bytes. Larger material belongs in separate managed wiki pages linked through the `related` section.

For release documentation, `4dt-wiki export --target <path>` renders managed SQLite pages as Markdown into an explicit target under workspace `sources/`, preserving relative paths. Export prepares source-shipped documentation but does not bypass release approval gates for staging, committing, pushing, tagging, or publishing.

Before release packaging, use `4dt-wiki export --target sources/4DreamTeam/docs` to render the current managed SQLite wiki into source-shipped Markdown. If exported docs contradict current source behavior, update the managed wiki first and export again; direct edits to exported docs will be overwritten by the next managed export. Full JSON export/import is available for wiki backup or workspace transfer, with import dry-run by default and `--apply` required to replace pages.

## Evidence

- `sources/4DreamTeam/4dreamteam/references/wiki/shared/page-shape.md`
- `sources/4DreamTeam/packages/wiki/tests/test_cli.py`
- `TASK-0023` quality acceptance

## Decisions

- Use `4dt-search query` for wiki/source discovery before broad reads.
- Use `4dt-wiki` for all managed wiki page writes and exact wiki reads.
- Use `4dt-sources` for source registry, inventory, exact snippets, and boundary validation.
- Keep managed wiki English-only and agent-facing.
- Treat `docs/` as exported release documentation; fix stale content in managed wiki and re-export.

## Open Questions

- Whether post-acceptance wiki updates should automatically include page source refs from related task evidence.
- Whether wiki validation should detect unresolved `TBD` placeholders after bootstrap.

## Related

- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Documentation Domain](../domains/documentation.md)
