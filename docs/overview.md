---
id: overview
kind: overview
title: Workspace Overview
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-23T08:40:12Z
owner: wiki
source_refs: ["sources/4DreamTeam/README.md", "sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md"]
task_refs: []
---

# Workspace Overview

## Summary


This workspace wiki documents the 4DreamTeam Codex skill itself: its purpose, runtime entrypoint, role workflow, documentation system, tool contracts, templates, and maintenance rules.

The wiki is an agent-facing knowledge base for continuing skill development without re-reading the whole repository every session. It complements the public README and docs, but it does not replace source files as the source of truth.

## Content


4DreamTeam is a Codex skill for turning rough product intent, half-finished work, stale documentation, and release pressure into a traceable file-based workflow. The README describes the promise as a path from idea to epic, task, implementation, quality review, documentation, and release.

The skill exposes one main entrypoint, `$4DreamTeam`. The installed skill should let the operator ask for work in natural language while the lead role chooses the smallest relevant route and loads only the required references. The user should not need to remember individual role names.

The source repository is not a normal downstream project workspace. `AGENTS.md` states that requests inside this repository default to skill development, improvement, review, testing, or documentation work for 4DreamTeam itself. That means source changes should be made as skill maintenance, while the managed workspace wiki here documents the skill source for future continuation.

Repository structure is centered on `4dreamteam/`: `SKILL.md` carries metadata, trigger surface, entrypoint rules, template inventory, and hard guarantees; `references/` carries detailed role and workflow behavior; `assets/templates/` carries files copied or adapted into user workspaces; `agents/openai.yaml` carries Codex UI metadata; `tools/` carries board, wiki, source, and memory CLIs; `docs/` and README files carry public documentation.

## Evidence



- `sources/4DreamTeam/README.md` states the public product promise and landing-page positioning.
- `sources/4DreamTeam/4dreamteam/SKILL.md` defines the installed skill entrypoint, role references, and hard guarantees.
- `sources/4DreamTeam/AGENTS.md` describes workspace-specific instructions.
- `sources/4DreamTeam/4dreamteam/references/lead/self-maintenance.md` summarizes repository structure and self-improvement lifecycle.

## Decisions


- This wiki documents the skill source repository rather than a downstream application using the skill.
- Managed wiki pages are written in English for agents; the lead role can summarize them to the operator in the user's language.
- Source claims in this wiki should point back to approved files under the workspace `sources/` boundary.

## Open Questions


- Contract memory defaults for this workspace are not fully configured yet.
- The optional LanceDB memory backend currently has a dependency compatibility issue recorded in 4DT Memory.

## Related


- [Product Overview](product/overview.md)
- [Architecture Overview](architecture/overview.md)
- [Documentation Domain](domains/documentation.md)
- [Workspace Tools Contract](contracts/workspace-tools.md)
- [Memory Domain](domains/memory.md)
