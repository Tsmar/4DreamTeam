---
id: contracts-workspace-tools
kind: contract
title: Workspace Tools Contract
status: actual
created_at: 2026-05-23T07:32:07Z
updated_at: 2026-05-24T10:42:38Z
owner: wiki
source_refs: ["sources/4DreamTeam/package.json", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/4dreamteam/references/lead/lifecycle.md", "sources/4DreamTeam/packages/board/src/fourdt_board/cli.py", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/wiki/src/fourdt_wiki/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0010", "EPIC-0001-TASK-0013", "EPIC-0002-TASK-0014"]
---

# Workspace Tools Contract

## Summary




Workspace tools are the stable API for managed state. Agents use 4dt-search for discovery and domain tools for exact reads, writes, administration, and validation instead of directly reading or writing managed storage.

## Content





The workspace model is a script-managed overlay. The underlying files are human-readable, but agents operate through commands and JSON contracts. This keeps lifecycle movement, source boundaries, wiki page shape, validation, search, and memory safety centralized.

`4dt-search` is the unified discovery facade. Agents use `4dt-search query` with explicit domains (`wiki`, `sources`, `board`, or `memory`) before broad reading. Search results include snippets, locators, freshness metadata, and `getCommand` values that point back to authoritative domain tools.

`4dt-board` manages epics, tasks, board columns, metadata, sections, timeline comments, validation, and repair. Its source defines supported columns such as backlog, analytic, developer, quality, wiki, release, released, done, and rejected. It also defines task/epic statuses, role values, timeline types, and required board sections.

`4dt-wiki` manages the single workspace wiki. It owns page frontmatter, stable sections, page kinds, statuses, initialization, validation, indexing, search, get, page creation, page updates, section-scoped updates, atomic page application, export, and ADR creation. Agents can read one stable section with `4dt-wiki get <page-or-id> --section <section>`, replace one section with `4dt-wiki page section-set <page-or-id> <section> --content <text>` or stdin, and use `4dt-wiki page apply <page-or-id>` for metadata plus multiple section updates from JSON. `4dt-wiki export --target <path>` copies only files under `.4dt/wiki/pages` into an explicit target under workspace `sources/`, preserving relative paths for release documentation.

`4dt-sources` manages the approved source registry, inventory, stats, search, and safe snippet reads. It includes ignore and forbidden patterns for names such as `.env`, private-key-like suffixes, dumps, dependency directories, caches, and build outputs. The same exclusion policy is used for indexing and `get`, and project `.gitignore` rules are honored for workspace and registered directory sources. Workspace `sources/` is the built-in source boundary; external boundaries require operator approval.

`4dt-memory` manages local memory status, initialization, recall, saving, import/export, session state, contract defaults, onboarding questions, mode definitions, and benchmark behavior. SQLite is authoritative; retrieval uses the shared 4dt-search runtime backend over live SQLite rows.

The source repository exposes local development scripts in `package.json`: `npm run board`, `npm run memory`, `npm run search`, `npm run search:validate`, `npm run sources`, `npm run 4dt-wiki`, `npm run wiki`, and `npm run rules`. Tool source and tests live under root `packages/`; the installable skill package lives under `4dreamteam/`.

## Evidence






- `sources/4DreamTeam/package.json` exposes local npm scripts for the tools.
- Tool source files under `sources/4DreamTeam/packages/` define command behavior and JSON outputs.
- `sources/4DreamTeam/4dreamteam/references/lead/preflight.md` defines startup checks.
- `sources/4DreamTeam/4dreamteam/references/lead/lifecycle.md` defines the role-board lifecycle.
- EPIC-0001 accepted tasks back 4dt-search, advanced query controls, unified integration, and memory search backend replacement.
- EPIC-0002-TASK-0014 accepted quality evidence backs root `packages/` source separation from the installable skill package.

## Decisions




- Treat command output as the interface for managed workspace state.
- Do not inspect or edit managed board/wiki storage directly in agent workflows.
- Use 4dt-search for discovery; use domain tools for exact reads, writes, validation, and administration.
- Keep memory as recall below current request, workspace artifacts, board/wiki evidence, and approved sources.

## Open Questions




- Global shell commands for board/sources/wiki/search/memory are not available in this environment; source-local npm scripts are currently used.
- CI should make the local validation surface mandatory on push and pull request.

## Related




- [Search Domain](../domains/search.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
- [Memory Domain](../domains/memory.md)
- [Wiki Workflow](../flows/wiki-workflow.md)
