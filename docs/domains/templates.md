---
id: domains-templates
kind: domain
title: Templates Domain
status: actual
created_at: 2026-05-23T07:32:19Z
updated_at: 2026-05-23T08:39:55Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/lead/contracts.md", "sources/4DreamTeam/4dreamteam/assets/templates/analytic/task.md", "sources/4DreamTeam/4dreamteam/assets/templates/product/epic.md", "sources/4DreamTeam/4dreamteam/assets/templates/workspace/AGENTS.md"]
task_refs: []
---

# Templates Domain

## Summary


Templates define artifact shape for epics, tasks, reports, wiki pages, marketing artifacts, DevOps docs, release plans, lead handoffs, and workspace bootstrap files. They do not replace behavior rules.

## Content


`SKILL.md` lists the bundled templates under `assets/templates/`. The list covers analytic task specs, product epics, lead epic handoffs, marketing artifacts, release plans, wiki starter pages, DevOps server docs, workspace `AGENTS.md`, and `sources/.gitignore`.

The instruction/template boundary is explicit. Role instructions define mandatory behavior. Templates define artifact shape. A required behavior must live in role instructions or shared lead rules; a template may add structure but cannot be the only place a required behavior exists. Instructions should point to templates they expect agents to use.

Workspace bootstrap templates are special. In an empty workspace, after confirmation, the skill may create only `AGENTS.md` from the workspace template, `sources/.gitignore` from the sources template, and tool-managed artifacts through board/wiki/sources/memory tools. It must not create a local `skill/` folder in a normal workspace.

Marketing templates are selected by mode: value review, README positioning review, release narrative, GTM brief, and claim audit each have specific entry conditions. Wiki templates include project, product overview, architecture overview, ADR, and sources. DevOps templates include server index and server card.

When changing a template that affects behavior, treat it as a framework behavior change requiring corresponding reference updates and quality review. When changing workspace bootstrap behavior, update related templates.

## Evidence



- `sources/4DreamTeam/4dreamteam/SKILL.md` lists bundled templates.
- `sources/4DreamTeam/4dreamteam/references/lead/contracts.md` defines template and artifact expectations.
- `sources/4DreamTeam/4dreamteam/assets/templates/analytic/task.md` defines analytic task structure.
- `sources/4DreamTeam/4dreamteam/assets/templates/product/epic.md` defines product epic structure.
- `sources/4DreamTeam/4dreamteam/assets/templates/workspace/AGENTS.md` defines workspace instruction bootstrap content.

## Decisions


- Templates shape artifacts; references define behavior.
- Bootstrap templates must stay aligned with the hard guarantee that normal workspaces do not get a local `skill/` folder.
- Behavior-affecting template changes require reference alignment and quality review.

## Open Questions


- Whether every template should include a short source comment pointing to the role reference that governs it.
- Whether template validation should check for outdated role names or legacy standalone report-file wording.

## Related


- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Documentation Domain](documentation.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Task Lifecycle Flow](../flows/task-lifecycle.md)
