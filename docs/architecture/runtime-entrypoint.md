---
id: architecture-runtime-entrypoint
kind: architecture
title: Runtime Entrypoint
status: actual
created_at: 2026-05-23T07:31:52Z
updated_at: 2026-05-23T07:35:55Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/lead.md", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/4dreamteam/references/lead/routing.md", "sources/4DreamTeam/4dreamteam/references/lead/context-budget.md"]
task_refs: []
---

# Runtime Entrypoint

## Summary


The runtime entrypoint is `$4DreamTeam`. It starts with `SKILL.md`, then `references/lead.md`, then preflight, route selection, and the smallest role-specific reference set needed for the request.

## Content


The first-step sequence is explicit: read `references/lead.md`; for a new session, read `references/lead/preflight.md` and run command-based onboarding; follow the lead module map; confirm the current folder is a 4DreamTeam workspace before writing; route the request; then load only the selected role reference and any mode-specific references.

The lead file is intentionally compact. It establishes context economy: do not load all references by default; prefer exact task ids, timeline entry ids, wiki slugs, and tool search results; use `4dt-wiki` and `4dt-sources` before broad source reading; load detailed modules only when their route or gate applies; and treat approved source repositories as source of truth during self-improvement.

Preflight is command-based. A new session reads `AGENTS.md` when present, checks memory readiness, loads contract defaults when memory is ready, runs board/source/wiki/memory startup checks, reports each tool status, names the workspace state, and offers safe next actions. Repair commands need explicit operator confirmation.

Routing is reference-driven. Product, analytic, developer, quality, wiki, marketing, devops, and release each have a role reference. Wiki then has its own mode map: bootstrap, post-acceptance, sync, audit, check, blueprint, and deepening. Context-budget rules apply when broad reading, large files, unfamiliar source areas, or long-running state may expand the context.

The entrypoint is conservative. It cannot bypass 4DreamTeam workflow where a route applies, cannot write before preflight or explicit workspace confirmation, cannot read/write managed board or wiki storage directly, and cannot run release, destructive, infrastructure, or publication actions without the required approval gates.

## Evidence


- `sources/4DreamTeam/4dreamteam/SKILL.md` defines first steps and hard guarantees.
- `sources/4DreamTeam/4dreamteam/references/lead.md` defines context economy, module map, role routing, default flow, and framework-wide hard guarantees.
- `sources/4DreamTeam/4dreamteam/references/lead/preflight.md` defines startup checks, memory defaults, workspace states, and source-boundary bootstrap behavior.
- `sources/4DreamTeam/4dreamteam/references/wiki/index.md` defines wiki mode selection.

## Decisions


- Load references progressively rather than copying the whole framework into context.
- Use command outputs, exact ids, and wiki/source search results before broad file reads.
- Treat preflight status as part of the user-facing startup response.

## Open Questions


- Contract memory defaults still need operator-approved values for this development workspace.
- The local PATH currently lacks global `4dt-board`, `4dt-sources`, and `4dt-wiki`; source-local npm scripts are used here.

## Related


- [Architecture Overview](overview.md)
- [Task Lifecycle Flow](../flows/task-lifecycle.md)
- [Wiki Workflow](../flows/wiki-workflow.md)
- [Memory Domain](../domains/memory.md)
- [Source Boundaries Domain](../domains/source-boundaries.md)
