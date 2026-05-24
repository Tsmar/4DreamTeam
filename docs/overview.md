---
id: overview
kind: overview
title: Workspace Overview
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-24T10:42:37Z
owner: wiki
source_refs: ["sources/4DreamTeam/README.md", "sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md", "sources/4DreamTeam/packages/search/src/fourdt_search/cli.py"]
task_refs: ["EPIC-0001-TASK-0008", "EPIC-0001-TASK-0013", "EPIC-0002-TASK-0014"]
---

# Workspace Overview

## Summary




This workspace wiki documents the 4DreamTeam Codex skill source repository: its purpose, runtime entrypoint, role workflow, documentation system, search facade, tool contracts, templates, and maintenance rules. It complements the public README and source files without replacing them as source of truth.

## Content




4DreamTeam is a Codex skill for turning rough product intent, half-finished work, stale documentation, and release pressure into a traceable file-based workflow. The README describes the promise as a path from idea to epic, task, implementation, quality review, documentation, and release.

The skill exposes one main entrypoint, `$4DreamTeam`. The installed skill should let the operator ask for work in natural language while the lead role chooses the smallest relevant route and loads only the required references. The user should not need to remember individual role names.

The source repository is not a normal downstream project workspace. `AGENTS.md` states that requests inside this repository default to skill development, improvement, review, testing, or documentation work for 4DreamTeam itself. That means source changes should be made as skill maintenance, while the managed workspace wiki here documents the skill source for future continuation.

Repository structure is split between the installable skill package and tool development. `4dreamteam/` carries `SKILL.md`, role references, workflow references, templates, agent metadata, and helper scripts. Root `packages/` carries board, wiki, source, memory, and search CLI source and tests. `docs/` and README files carry public documentation exports.

4dt-search is the unified discovery interface for agents. It searches wiki, approved sources, board history, and live SQLite-backed memory through explicit domains, then returns authoritative `getCommand` values for exact reads through the owning domain tools.

## Evidence





- `sources/4DreamTeam/README.md` states the public product promise and landing-page positioning.
- `sources/4DreamTeam/4dreamteam/SKILL.md` defines the installed skill entrypoint, role references, and hard guarantees.
- `sources/4DreamTeam/AGENTS.md` describes workspace-specific instructions.
- `sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md` summarizes repository structure and self-improvement lifecycle.
- EPIC-0001 accepted work backs 4dt-search as the unified discovery interface and memory retrieval backend.
- EPIC-0002-TASK-0014 accepted work backs root `packages/` separation from the installed skill package.

## Decisions




- This wiki documents the skill source repository rather than a downstream application using the skill.
- Managed wiki pages are written in English for agents; the lead role can summarize them to the operator in the user's language.
- Source claims in this wiki should point back to approved files under the workspace `sources/` boundary.
- Tool source and tests belong under root `packages/`, not inside the installed skill package.

## Open Questions




- Contract memory defaults can be tuned further for this workspace as the workflow stabilizes.
- CI quality gates should be added so push and pull-request checks enforce the local validation suite.

## Related




- [Product Overview](product/overview.md)
- [Architecture Overview](architecture/overview.md)
- [Search Domain](domains/search.md)
- [Documentation Domain](domains/documentation.md)
- [Workspace Tools Contract](contracts/workspace-tools.md)
- [Memory Domain](domains/memory.md)
