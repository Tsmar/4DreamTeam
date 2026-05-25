---
id: flows-wiki-workflow
kind: flow
title: Wiki Workflow
status: actual
created_at: 2026-05-23T07:32:13Z
updated_at: 2026-05-25T11:09:27Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/wiki.md", "sources/4DreamTeam/4dreamteam/references/wiki/index.md", "sources/4DreamTeam/4dreamteam/references/wiki/shared/page-shape.md", "sources/4DreamTeam/4dreamteam/references/wiki/bootstrap.md", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py"]
task_refs: ["TASK-0023"]
---

# Wiki Workflow

## Summary



The wiki workflow maintains the single workspace knowledge base through `4dt-wiki`, using `4dt-sources` for approved source navigation and mode-specific rules for bootstrap, sync, audit, check, blueprint, and deepening.

## Content






Wiki work starts by reading `references/wiki.md`, then `references/wiki/index.md`, then shared modules, then the smallest mode file needed for the request. The role supports a single workspace wiki; old multi-project wiki registry and source-map workflows are legacy for new work.

Mode selection is simple. Use bootstrap for a new source-backed wiki. Use post-acceptance when accepted quality evidence exists and docs need updating. Use sync to align existing wiki pages with accepted changes or explicitly approved current sources. Use audit or check for read-only review. Use blueprint for proposed future documentation. Use deepening to add implementation detail to existing docs from current sources.

Discovery should start with `4dt-search query` using explicit `wiki` or `sources` domains. Use result `getCommand` values or exact `4dt-wiki`/`4dt-sources` commands for full reads. Use `4dt-wiki index build/check` for wiki administration and validation, not as the first broad discovery surface.

Bootstrap flow requires an intake summary before writing unless defaults or auto mode are explicitly accepted. It checks approved sources with `4dt-sources registry list`, initializes wiki storage with `4dt-wiki init`, creates or updates managed pages through `4dt-wiki`, builds and checks the index, and validates with `4dt-wiki validate`.

The wiki role must not read or write wiki storage directly. It must not document rejected or unconfirmed changes as facts. Confirmed pre-development requirements must be marked proposed until source or accepted quality proves implementation. Source-of-truth claims should point to approved sources, accepted timeline evidence, or explicit blueprint assumptions.

Managed pages have stable frontmatter and required sections: Summary, Content, Evidence, Decisions, Open Questions, and Related. Section keys are `summary`, `content`, `evidence`, `decisions`, `open_questions`, and `related`. For focused edits, agents should prefer `4dt-wiki get <page-or-id> --section <section>` and `4dt-wiki page section-set <page-or-id> <section> --content <text>` or stdin instead of full-page reads or rewrites. Use `4dt-wiki page apply <page-or-id>` when metadata and multiple sections need to change together from one JSON payload. For agent-generated JSON payloads, omit `--file` and pass JSON through stdin; use `--file` only when the payload already exists as a reusable, reviewed, or operator-provided artifact.

For release documentation, `4dt-wiki export --target <path>` copies only files from `.4dt/wiki/pages` into an explicit target under workspace `sources/`, preserving relative paths. Export prepares source-shipped documentation but does not bypass release approval gates for staging, committing, pushing, tagging, or publishing.

## Evidence







- `sources/4DreamTeam/4dreamteam/references/wiki/shared/page-shape.md`
- `sources/4DreamTeam/packages/wiki/tests/test_cli.py`
- `TASK-0023` quality acceptance

## Decisions




- Use `4dt-search query` for wiki/source discovery before broad reads.
- Use `4dt-wiki` for all managed wiki page writes and exact wiki reads.
- Use `4dt-sources` for source registry, inventory, exact snippets, and boundary validation.
- Keep managed wiki English-only and agent-facing.

## Open Questions



- Whether post-acceptance wiki updates should automatically include page source refs from related task evidence.
- Whether wiki validation should detect unresolved `TBD` placeholders after bootstrap.

## Related



- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Documentation Domain](../domains/documentation.md)
