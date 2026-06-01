---
id: architecture-overview
kind: architecture
title: Overview
status: actual
created_at: "2026-05-23T07:31:46Z"
updated_at: "2026-06-01T04:02:35Z"
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/package.json", "sources/4DreamTeam/4dreamteam/agents/openai.yaml", "sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py", "sources/4DreamTeam/packages/db/src/fourdt_db/cli.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0002-TASK-0014"]
tags: ["architecture", "skill-package", "sqlite", "tooling"]
---

# Overview

## Summary

Architecture knowledge owns the repository shape, installed skill package, runtime packaging, and tool package boundaries. It explains where code lives and why packages are separated, while product value stays in product pages and table-level details stay in schema pages.

## Content

The repository root contains repository-level development rules, public documentation, release history, root tool source, and the installable skill package. The package under 4dreamteam is the installed skill unit; root packages contain local command-line tools and tests.

Architectural boundaries:

- 4dreamteam/SKILL.md is the compact top-level skill contract and route map. It should stay small and point to references for detailed behavior.
- 4dreamteam/references owns operational workflow rules for lead, product, analytic, developer, quality, wiki, marketing, devops, release, memory, safety, and lifecycle behavior.
- 4dreamteam/assets/templates owns artifact shape for bootstrap, epics, tasks, wiki pages, marketing artifacts, release plans, DevOps docs, and handoffs. Templates do not replace role behavior rules.
- packages owns tool source and tests. Domain tools manage state contracts; browser surfaces live in packages/web so domain CLIs stay focused.
- 4dreamteam/scripts contains installed wrappers and the generated runtime archive used by installed skill commands.

Architecture pages should explain package boundaries, runtime entrypoints, dependency direction, and separation of concerns. They should link to domain pages for subsystem behavior and to schema pages for table-level storage authority.

## Evidence

- `sources/4DreamTeam/4dreamteam/SKILL.md` defines installed skill entrypoint, role references, templates, and hard guarantees.
- `sources/4DreamTeam/package.json` exposes repository-level development scripts.
- `sources/4DreamTeam/packages/` contains board, wiki, sources, memory, and search tool source and tests.
- `sources/4DreamTeam/4dreamteam/agents/openai.yaml` points Codex agents at the skill entrypoint.
- `sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md` defines self-improvement lifecycle and source repository update flow.
- EPIC-0002-TASK-0014 accepted quality evidence backs separation of tool source from the skill package.
- `sources/4DreamTeam/packages/db/src/fourdt_db/cli.py` defines shared database backup, schema status, and controlled migration commands.

## Decisions

- Keep SKILL.md compact and route detailed behavior into reference files.
- Treat tools as the stable API for workspace state.
- Keep tool source and tests outside the installable skill package.
- Keep browser UI in 4dt-web instead of expanding domain management CLIs.
- Treat templates as artifact shape, not the only source of mandatory behavior.

## Open Questions

- Whether tool CLIs should be installed globally or remain invoked through source-local npm scripts in this development workspace.
- Whether CI should publish or package tools separately from the skill bundle after validation.

## Related

- [Overview](../start/overview.md)
- [Runtime Entrypoint](runtime-entrypoint.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Search Domain](../domains/search.md)
- [Templates Domain](../domains/templates.md)
- [Documentation Domain](../domains/documentation.md)
