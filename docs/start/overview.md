---
id: start-overview
kind: overview
title: Overview
status: actual
created_at: "2026-05-23T07:31:46Z"
updated_at: "2026-06-01T05:56:55Z"
owner: wiki
source_refs: ["sources/4DreamTeam/README.md", "sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0013", "EPIC-0002-TASK-0014"]
tags: ["overview", "skill", "tool-managed"]
---

# Overview

## Summary

This workspace wiki is the navigation map for the 4DreamTeam skill source. It separates product meaning, workflow behavior, technical architecture, subsystem domains, and tool/storage contracts so agents can find the right layer before acting.

## Content

Use this page as the top-level reading map. It intentionally answers where knowledge belongs before it answers implementation detail.

Layer 1 - Product meaning: Overview explains who the framework is for, what value it promises, and what counts as product acceptance. Product pages should not carry package layouts, table names, or CLI internals unless those details change user value or scope.

Layer 2 - Workflow behavior: Task Lifecycle, Wiki, README Maintenance, and role contracts explain how agents move work through product, analytic, developer, quality, wiki, release, marketing, and devops roles. Workflow pages own handoffs, gates, acceptance rules, and operator-control behavior.

Layer 3 - Technical architecture: Architecture pages explain repository layout, runtime entrypoints, installed package boundaries, and why packages are separated. They should link to domain pages for subsystem detail rather than mixing every tool contract into one overview.

Layer 4 - Domains: Domain pages explain one capability at a time: memory, search, documentation, source boundaries, templates, and similar areas. A domain page should describe purpose, owned commands or files, important decisions, evidence, and neighboring pages.

Layer 5 - Contracts and schemas: Contract pages define stable agent-facing APIs and rules. Schema pages define storage authority, tables, migration expectations, and validation behavior. They are the right place for precise CLI and SQLite details.

Layer 6 - Changelog and release evidence: Changelog captures accepted/released changes. Task timeline evidence remains the source for exact acceptance history.

The local Workspace View is the browser panel over this managed knowledge. It currently shows wiki pages grouped by these boundaries and is launched with 4dt-web.

## Evidence

- `sources/4DreamTeam/README.md` states the public product promise and landing-page positioning.
- `sources/4DreamTeam/4dreamteam/SKILL.md` defines the installed skill entrypoint, role references, and hard guarantees.
- `sources/4DreamTeam/AGENTS.md` describes workspace-specific instructions.
- `sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md` summarizes repository structure and self-improvement lifecycle.
- EPIC-0001 accepted work backs 4dt-search as the unified discovery interface and memory retrieval backend.
- EPIC-0002-TASK-0014 accepted work backs root `packages/` separation from the installed skill package.

## Decisions

- Keep product value and user meaning in Product pages.
- Keep role movement, gates, and handoffs in Workflow and Contract pages.
- Keep package layout and runtime shape in Architecture pages.
- Keep subsystem-specific behavior in Domain pages.
- Keep table names, migration rules, and storage ownership in Schema pages.
- Use Workspace View as the local browser surface for reading managed state while agents work.

## Open Questions

- Contract memory defaults can be tuned further for this workspace as the workflow stabilizes.
- CI quality gates should be added so push and pull-request checks enforce the local validation suite.

## Related

- [Overview](../product/overview.md)
- [Task Lifecycle](../workflows/task-lifecycle.md)
- [Wiki](../workflows/wiki.md)
- [Overview](../architecture/overview.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
- [Search Domain](../domains/search.md)
- [Memory Domain](../domains/memory.md)
