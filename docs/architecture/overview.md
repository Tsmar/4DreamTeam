---
id: architecture-overview
kind: architecture
title: Architecture Overview
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-23T08:39:55Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/package.json", "sources/4DreamTeam/4dreamteam/agents/openai.yaml", "sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md"]
task_refs: []
---

# Architecture Overview

## Summary


The skill is packaged as a self-contained `4dreamteam/` bundle with a compact entrypoint, route-specific references, templates, agent UI metadata, and local Python CLIs for managed workspace state.

## Content


The repository root contains repository-level development rules (`AGENTS.md`), public documentation (`README.md`, `README.ru.md`, `docs/`), release history (`CHANGELOG.md`), and the skill package (`4dreamteam/`). The package is the installable skill unit.

`4dreamteam/SKILL.md` is the top-level skill contract. It holds frontmatter metadata (`name`, `description`, license, version, repository), first-step instructions, role reference routing, template inventory, reference-loading guidance, and hard guarantees. It intentionally points deeper behavior into `references/` rather than carrying every workflow detail directly.

`4dreamteam/references/` is the operational brain of the framework. `lead.md` is compact and routes into detailed lead modules only when needed. Role references define product, analytic, developer, quality, wiki, marketing, devops, and release behavior. Wiki references further split into mode files such as bootstrap, audit, sync, check, blueprint, and deepening.

`4dreamteam/assets/templates/` contains artifact templates for workspace bootstrap, product epics, analytic tasks, wiki pages, marketing artifacts, release plans, DevOps server cards, and lead handoffs. Templates shape files, while references define mandatory behavior.

`4dreamteam/tools/` contains local command-line tools. `package.json` exposes npm scripts for board, memory, sources, 4dt-wiki, legacy wiki index, and workflow rules. These tools are the API for managed workspace artifacts; agents should not read or write managed board or wiki storage directly.

`4dreamteam/agents/openai.yaml` defines the Codex UI surface: display name, short description, logo assets, brand color, and default prompt.

## Evidence



- `sources/4DreamTeam/4dreamteam/SKILL.md` defines installed skill entrypoint, role references, templates, and hard guarantees.
- `sources/4DreamTeam/package.json` exposes repository-level development scripts.
- `sources/4DreamTeam/4dreamteam/agents/openai.yaml` points Codex agents at the skill entrypoint.
- `sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md` defines self-improvement lifecycle and source repository update flow.

## Decisions


- Keep `SKILL.md` compact and route detailed behavior into reference files.
- Treat tools as the stable API for workspace state.
- Treat templates as artifact shape, not the only source of mandatory behavior.

## Open Questions


- Whether tool CLIs should be installed globally or remain invoked through source-local npm scripts in this development workspace.
- Whether the wiki CLI should grow richer page-editing commands beyond `page apply` after this bootstrap.

## Related


- [Runtime Entrypoint](runtime-entrypoint.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Templates Domain](../domains/templates.md)
- [Documentation Domain](../domains/documentation.md)
