---
id: architecture-overview
kind: architecture
title: Architecture Overview
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-24T10:42:37Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/package.json", "sources/4DreamTeam/4dreamteam/agents/openai.yaml", "sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0002-TASK-0014"]
---

# Architecture Overview

## Summary




The installable skill is a compact `4dreamteam/` bundle with entrypoint instructions, references, templates, agent metadata, and helper scripts. Repository-level tool development lives separately under root `packages/`.

## Content




The repository root contains repository-level development rules (`AGENTS.md`), public documentation (`README.md`, `README.ru.md`, `docs/`), release history (`CHANGELOG.md`), root tool source (`packages/`), and the installable skill package (`4dreamteam/`). The package is the installed skill unit.

`4dreamteam/SKILL.md` is the top-level skill contract. It holds frontmatter metadata (`name`, `description`, license, version, repository), first-step instructions, role reference routing, template inventory, reference-loading guidance, and hard guarantees. It intentionally points deeper behavior into `references/` rather than carrying every workflow detail directly.

`4dreamteam/references/` is the operational brain of the framework. `lead.md` is compact and routes into detailed lead modules only when needed. Role references define product, analytic, developer, quality, wiki, marketing, devops, and release behavior. Wiki references further split into mode files such as bootstrap, audit, sync, check, blueprint, and deepening.

`4dreamteam/assets/templates/` contains artifact templates for workspace bootstrap, product epics, analytic tasks, wiki pages, marketing artifacts, release plans, DevOps server cards, and lead handoffs. Templates shape files, while references define mandatory behavior.

`packages/` contains local command-line tools and their tests. `package.json` exposes npm scripts for board, memory, search, sources, 4dt-wiki, legacy wiki index, and workflow rules. These tools are the API for managed workspace artifacts; agents should use 4dt-search for discovery and domain tools for exact reads, writes, validation, and administration.

`4dreamteam/agents/openai.yaml` defines the Codex UI surface: display name, short description, logo assets, brand color, and default prompt.

## Evidence





- `sources/4DreamTeam/4dreamteam/SKILL.md` defines installed skill entrypoint, role references, templates, and hard guarantees.
- `sources/4DreamTeam/package.json` exposes repository-level development scripts.
- `sources/4DreamTeam/packages/` contains board, wiki, sources, memory, and search tool source and tests.
- `sources/4DreamTeam/4dreamteam/agents/openai.yaml` points Codex agents at the skill entrypoint.
- `sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md` defines self-improvement lifecycle and source repository update flow.
- EPIC-0002-TASK-0014 accepted quality evidence backs separation of tool source from the skill package.

## Decisions




- Keep `SKILL.md` compact and route detailed behavior into reference files.
- Treat tools as the stable API for workspace state.
- Keep tool source and tests outside the installable skill package.
- Treat templates as artifact shape, not the only source of mandatory behavior.

## Open Questions




- Whether tool CLIs should be installed globally or remain invoked through source-local npm scripts in this development workspace.
- Whether CI should publish or package tools separately from the skill bundle after validation.

## Related




- [Runtime Entrypoint](runtime-entrypoint.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Search Domain](../domains/search.md)
- [Templates Domain](../domains/templates.md)
- [Documentation Domain](../domains/documentation.md)
