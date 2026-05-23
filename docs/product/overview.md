---
id: product-overview
kind: product
title: Product Overview
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-23T08:40:12Z
owner: wiki
source_refs: ["sources/4DreamTeam/README.md", "sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/product.md", "sources/4DreamTeam/4dreamteam/references/lead/routing.md"]
task_refs: []
---

# Product Overview

## Summary


4DreamTeam's product model is a controlled multi-role workflow for Codex. It trades one long opaque chat for explicit roles, visible artifacts, operator approvals, and source-backed documentation.

## Content


The public promise is continuity: the operator can return later, inspect what happened, see which work is accepted, and choose the next safe step. The workflow makes state visible through files and tool-managed artifacts rather than relying on chat memory alone.

The role set is product, analytic, developer, quality, wiki, marketing, devops, and release. The operator sits above the workflow and controls source access, role-transition gates, auto mode, file writes, git, infrastructure, and publication. The lead role routes the request so the operator can use `$4DreamTeam` instead of remembering all role names.

The normal product-to-release path is `idea -> epic -> task -> implementation -> quality review -> documentation -> release`. Product shapes user goals, scope, non-goals, task candidates, and acceptance criteria. Analytic turns approved intent into implementation-ready tasks. Developer implements. Quality independently accepts or rejects. Wiki updates source-backed documentation. Release packages only accepted work after explicit approval.

The product is conservative by design. Safety guarantees include hard source boundaries, independent quality for implementation workflows, explicit approval for auto-mode role transitions, no secret exposure, no destructive or infrastructure actions without approval, and no unsupported marketing or DevOps claims.

## Evidence



- `sources/4DreamTeam/README.md` states the public product promise.
- `sources/4DreamTeam/4dreamteam/SKILL.md` defines roles and hard guarantees.
- `sources/4DreamTeam/4dreamteam/references/product.md` defines product role responsibilities.
- `sources/4DreamTeam/4dreamteam/references/lead/routing.md` defines request routing into product, analytic, developer, quality, wiki, marketing, devops, and release flows.

## Decisions


- Product value is defined around traceability, continuity, and controlled delegation rather than raw automation speed.
- The operator remains the approval authority for sensitive transitions and irreversible actions.
- Role separation is a product feature: developer cannot self-accept, quality cannot fix code, release cannot package unaccepted work.

## Open Questions


- Which default workflow modes should this workspace persist in contract memory?
- Which future README examples best demonstrate the skill without making it feel heavy or ceremonial?

## Related


- [Task Lifecycle Flow](../flows/task-lifecycle.md)
- [README Maintenance Flow](../flows/readme-maintenance.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
