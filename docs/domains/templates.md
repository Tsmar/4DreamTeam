---
id: domains-templates
kind: domain
title: Templates Domain
status: actual
created_at: "2026-05-23T07:32:19Z"
updated_at: "2026-06-01T00:00:00Z"
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/lead/contracts.md", "sources/4DreamTeam/4dreamteam/assets/templates/analytic/task.md", "sources/4DreamTeam/4dreamteam/assets/templates/product/epic.md", "sources/4DreamTeam/4dreamteam/assets/templates/workspace/AGENTS.md"]
task_refs: []
tags: ["bootstrap", "instructions", "templates"]
---

# Templates Domain

## Summary

Templates define artifact shape for epics, tasks, reports, wiki pages, marketing artifacts, DevOps docs, release plans, lead handoffs, and workspace bootstrap files. They do not replace behavior rules.

## Content

`SKILL.md` lists the bundled templates under `assets/templates/`. The list covers analytic task specs, product epics, lead epic handoffs, marketing artifacts, release plans, wiki starter pages, DevOps server docs, and workspace `AGENTS.md`.

The instruction/template boundary is explicit. Role instructions define mandatory behavior. Templates define artifact shape. A required behavior must live in role instructions or shared lead rules; a template may add structure but cannot be the only place a required behavior exists. Instructions should point to templates they expect agents to use.

Workspace bootstrap templates are special. In an empty workspace, after confirmation, 4DreamTeam may create only `AGENTS.md` from the workspace template and tool-managed artifacts through board/wiki/sources/memory tools. It must not create a local installed-skill copy in a normal workspace; the installed package is `4dreamteam/`. Bootstrap must not create `sources/.gitignore`; project-provided ignore files are honored only when they already exist.

Marketing templates are selected by mode: value review, README positioning review, release narrative, GTM brief, and claim audit each have specific entry conditions. Wiki templates include project, product overview, architecture overview, and ADR. They follow the current managed wiki page contract: frontmatter plus the stable Summary, Content, Evidence, Decisions, Open Questions, and Related sections. Source registry and source inventory artifacts are managed through `4dt-sources`, not through a wiki `sources.md` template. DevOps templates include server index and server card.

When changing a template that affects behavior, treat it as a framework behavior change requiring corresponding reference updates and quality review. When changing workspace bootstrap behavior, update related templates.

## Evidence

- `sources/4DreamTeam/4dreamteam/SKILL.md` lists bundled templates.
- `sources/4DreamTeam/4dreamteam/references/lead/contracts.md` defines template and artifact expectations.
- `sources/4DreamTeam/4dreamteam/assets/templates/analytic/task.md` defines analytic task structure.
- `sources/4DreamTeam/4dreamteam/assets/templates/product/epic.md` defines product epic structure.
- `sources/4DreamTeam/4dreamteam/assets/templates/wiki/project.md` defines the current managed wiki starter shape.
- `sources/4DreamTeam/4dreamteam/assets/templates/workspace/AGENTS.md` defines workspace instruction bootstrap content.
- `sources/4DreamTeam/4dreamteam/references/wiki/shared/source-boundaries.md` documents that bootstrap must not create `sources/.gitignore` automatically.

## Decisions

- Templates shape artifacts; references define behavior.
- Wiki templates must stay aligned with `4dt-wiki` managed frontmatter and stable sections; old `wiki-meta`, `sources.md`, and source-map template shapes are legacy.
- Bootstrap templates must stay aligned with the hard guarantee that normal workspaces do not get a local installed-skill copy; the installed package is `4dreamteam/`.
- Behavior-affecting template changes require reference alignment and quality review.

## Open Questions

- Whether every template should include a short source comment pointing to the role reference that governs it.
- Whether template validation should check for outdated role names or legacy standalone report-file wording.

## Related

- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Documentation Domain](documentation.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Task Lifecycle](../workflows/task-lifecycle.md)
