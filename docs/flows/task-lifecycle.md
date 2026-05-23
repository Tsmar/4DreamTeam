---
id: flows-task-lifecycle
kind: flow
title: Task Lifecycle Flow
status: actual
created_at: 2026-05-23T07:32:10Z
updated_at: 2026-05-23T08:40:33Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/lead/lifecycle.md", "sources/4DreamTeam/4dreamteam/references/lead/routing.md", "sources/4DreamTeam/4dreamteam/references/lead/safety.md", "sources/4DreamTeam/4dreamteam/references/developer.md", "sources/4DreamTeam/4dreamteam/references/quality.md", "sources/4DreamTeam/4dreamteam/references/release.md"]
task_refs: []
---

# Task Lifecycle Flow

## Summary


The task lifecycle is board-column driven and evidence-gated. A task moves through role ownership only when required timeline evidence exists, not merely because status text changed.

## Content



The board columns are `backlog`, `analytic`, `developer`, `quality`, `wiki`, `release`, `released`, `done`, and `rejected`. The current column determines the next owner role. The lifecycle rules explicitly say not to use `next_owner`.

Product creates and shapes epics and task candidates. An epic contains tasks as child work items. Product may keep work in backlog, hand tasks to analytic, or hand clear delivery tasks directly to developer. Analytic moves implementation-ready task specs to developer only after required documentation alignment is complete or explicitly not required.

Developer reads the task and prior timeline evidence through `4dt-board`, marks work as working, inspects relevant source/tests/configs, writes a short implementation plan before the first patch, compares it with the operator, and waits for plan approval or scoped auto implementation approval before patching. After approval, developer implements only task scope, runs checks, appends a developer report, and moves work to quality. Developer cannot accept work and cannot create quality evidence.

Quality independently verifies every acceptance criterion with evidence. It reads the task and developer report, runs pin tests, checks relevant tests, reviews unrelated changes, and appends either accepted or rejected quality evidence. Documentation-oriented work also requires source backing, status correctness, link integrity, product readability, technical precision, scope control, and safety guarantee preservation.

Accepted quality always moves work to wiki for post-acceptance documentation review before done or release. Wiki records documentation updates or explicitly records that no managed wiki change is needed, then moves work onward. Rejected work moves to rejected; rework returns to developer and then quality. Release starts only after an explicit release request and accepted quality or product acceptance exists. Release produces a visible plan and requires explicit approval before staging or committing, with separate approval before pushing or publishing.

Before an epic is closed or the next epic becomes active implementation focus, lead must create a `lead_handoff` timeline entry with accepted changes, evidence, workflow notes, project nuances, open threads, and next starting points.

## Evidence



- `sources/4DreamTeam/4dreamteam/references/lead/lifecycle.md` defines board columns, movement rules, state machine, and handoff requirements.
- `sources/4DreamTeam/4dreamteam/references/lead/routing.md` defines role route selection.
- `sources/4DreamTeam/4dreamteam/references/lead/safety.md` defines approval gates and controlled-mode stops.
- `sources/4DreamTeam/4dreamteam/references/developer.md` defines developer responsibilities, output contract, execution protocol, blockers, and rework loop.
- `sources/4DreamTeam/4dreamteam/references/quality.md` defines independent acceptance, acceptance matrix, documentation-quality checks, and rejection rules.
- `sources/4DreamTeam/4dreamteam/references/release.md` defines release entry conditions, changelog policy, commit plan gate, and git rules.

## Decisions



- Role transitions are evidence-gated and tool-managed.
- Developer implementation requires a visible plan and operator comparison/approval before the first patch unless scoped auto implementation was explicitly approved.
- Quality is mandatory for implementation workflows.
- Accepted quality always routes to wiki for post-acceptance documentation review before done or release.
- Release is explicit-only and cannot package unaccepted work.
- Epic handoff is durable local memory before closing an epic or shifting active focus.

## Open Questions


- This source workspace currently has an empty board; no real skill-improvement epic/task has been created for this wiki bootstrap.
- A future task could decide whether skill-source documentation-only work should always get a formal board lifecycle.

## Related


- [Product Overview](../product/overview.md)
- [Wiki Workflow](wiki-workflow.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [README Maintenance Flow](readme-maintenance.md)
