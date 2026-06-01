---
id: product-overview
kind: product
title: Overview
status: actual
created_at: "2026-05-23T07:31:46Z"
updated_at: "2026-06-01T04:02:35Z"
owner: wiki
source_refs: ["sources/4DreamTeam/README.md", "sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/product.md", "sources/4DreamTeam/4dreamteam/references/lead/routing.md"]
task_refs: []
tags: ["agents", "product", "workflow"]
---

# Overview

## Summary

4DreamTeam is a controlled multi-role workflow for Codex. Product knowledge owns purpose, users, value, scope, and acceptance meaning; it intentionally avoids package layout, SQLite tables, and runtime wiring except where those details affect user value.

## Content

The product promise is continuity with control. The operator can return later, inspect what happened, see which work is accepted, and choose the next safe step. The framework makes state visible through board timelines, managed wiki pages, approved sources, memory, and release evidence rather than relying on chat memory alone.

Product pages answer five questions:

- Who is the framework for? Operators who want Codex to work through traceable roles instead of one opaque conversation.
- What problem does it solve? It turns rough intent, unfinished work, stale docs, and release pressure into auditable tasks and accepted artifacts.
- What value does it promise? Continuity, source-backed decisions, independent quality, safer delegation, and recoverable context.
- What is in or out of scope? Product pages define user-facing behavior, acceptance intent, roadmap shape, non-goals, and risk posture.
- What counts as done? Accepted work has quality evidence and, when needed, wiki/release evidence.

The role set is product, analytic, developer, quality, wiki, marketing, devops, and release. The operator sits above the workflow and controls source access, role-transition gates, auto mode, file writes, git, infrastructure, and publication. The lead role routes requests so the operator can use $4DreamTeam without remembering all role names.

The normal product-to-release path is idea -> epic -> task -> implementation -> quality review -> documentation -> release. Product shapes goals, scope, non-goals, task candidates, and acceptance criteria. Analytic turns approved intent into implementation-ready tasks. Developer implements. Quality independently accepts or rejects. Wiki updates source-backed documentation. Release packages only accepted work after explicit approval.

Do not put repository layout, CLI flags, database table lists, or migration rules here unless they change product scope or operator-facing behavior. Link to Architecture, Workspace Tools Contract, or Tool Storage Schema for those details.

## Evidence

- `sources/4DreamTeam/README.md` states the public product promise.
- `sources/4DreamTeam/4dreamteam/SKILL.md` defines roles and hard guarantees.
- `sources/4DreamTeam/4dreamteam/references/product.md` defines product role responsibilities.
- `sources/4DreamTeam/4dreamteam/references/lead/routing.md` defines request routing into product, analytic, developer, quality, wiki, marketing, devops, and release flows.

## Decisions

- Product value is traceability, continuity, and controlled delegation rather than raw automation speed.
- The operator remains the approval authority for sensitive transitions and irreversible actions.
- Role separation is a product feature: developer cannot self-accept, quality cannot fix code, release cannot package unaccepted work.
- Product pages define why and what; workflow, architecture, contracts, and schemas define how.

## Open Questions

- Which default workflow modes should this workspace persist in contract memory?
- Which future README examples best demonstrate the skill without making it feel heavy or ceremonial?

## Related

- [Overview](../start/overview.md)
- [Task Lifecycle](../workflows/task-lifecycle.md)
- [README Maintenance](../workflows/readme-maintenance.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Overview](../architecture/overview.md)
