# Lead Lifecycle

Use this file when moving tasks between columns or checking lifecycle state.

## Role Board

The `tasks/` directory is a virtual Kanban board. A task file lives in the folder of the role that currently owns the next action.

Board columns:

```txt
tasks/backlog/      # epics, product backlog, discovery, grouped task planning
tasks/analytic/     # needs technical analysis before implementation
tasks/developer/    # ready for implementation or developer rework
tasks/quality/      # implementation complete, ready for independent quality
tasks/wiki/         # accepted work that needs wiki documentation
tasks/release/      # accepted work selected for release packaging
tasks/released/     # work included in a pushed release
tasks/done/         # closed, no active next role
tasks/rejected/     # rejected work awaiting a decision or correction
```

Movement rules:

1. `product` creates and shapes epics in `tasks/backlog/`.
2. Every epic contains only tasks as child work items. Do not create Product or Item entities.
3. `product` may keep an epic in `tasks/backlog/`, hand its tasks to `tasks/analytic/`, or hand clear delivery tasks directly to `tasks/developer/`.
4. `analytic` creates or moves implementation-ready task specs to `tasks/developer/`.
5. `developer` moves completed implementation work to `tasks/quality/` and creates a developer report.
6. `quality` moves accepted work to `tasks/wiki/` when docs are needed, otherwise to `tasks/done/`.
7. `quality` moves rejected work to `tasks/rejected/`.
8. Rework moves from `tasks/rejected/` to `tasks/developer/`, then back to `tasks/quality/`.
9. `release` moves work from `tasks/done/` to `tasks/release/` only after an explicit user request for release, changelog, staging, commit, or release packaging.
10. `release` moves work from `tasks/release/` to `tasks/released/` only after the release branch is pushed and the chosen release publication step is complete.

## Task Lifecycle State Machine

Use folder location as the primary state. Use the task's status field for finer lifecycle notes.

| State | Owner | Required artifact or evidence | Required check | Valid next transitions |
|---|---|---|---|---|
| `draft` | product | Epic or draft task in `tasks/backlog/` | Product goal and audience are visible. | `product-approved`, `blocked`, `rejected` |
| `product-approved` | product | Epic with scope, non-goals, task candidates, and product acceptance criteria. | No product blocking questions. | `analytic-ready`, `developer-ready`, `blocked` |
| `analytic-ready` | analytic | Task candidate in epic or `tasks/analytic/`. | Technical impact can be analyzed from approved docs/sources. | `developer-ready`, `blocked`, `needs-product` |
| `developer-ready` | developer | `tasks/developer/TASK-XXXX.md` with affected areas, acceptance criteria, and validation plan. | No analytic blocking questions. | `developer-in-progress`, `blocked` |
| `developer-in-progress` | developer | Task status marked `working`. | Implementation plan exists before patching. | `developer-done`, `blocked` |
| `developer-done` | developer | Developer report in `reports/tasks/`. | Relevant checks run or skipped with reasons. | `quality-review` |
| `quality-review` | quality | Task in `tasks/quality/` and developer report. | Acceptance matrix covers every criterion. | `accepted`, `rejected` |
| `rejected` | quality / developer | Rejected quality report in `reports/quality/rejected/`. | Rejection reason and required fix are actionable. | `fixed`, `blocked`, `done` if abandoned |
| `fixed` | developer | Updated developer report and revision history. | Only failed criteria were changed unless scope was approved. | `quality-review` |
| `accepted` | quality | Accepted quality report in `reports/quality/accepted/`. | Every criterion is `pass`. | `wiki-update`, `release-ready`, `done` |
| `wiki-update` | wiki | Task in `tasks/wiki/` plus accepted quality report. | Docs update is source-backed or not needed. | `release-ready`, `done` |
| `release-ready` | release | Task in `tasks/done/` selected by explicit release request. | Accepted quality or product acceptance exists. | `release-planned` |
| `release-planned` | release | Release plan in `reports/release/`. | Included/excluded files and approval requirements are visible. | `released`, `blocked` |
| `released` | release | Release report with pushed release evidence. | Branch push and requested publication steps succeeded. | `done` |
| `done` | lead | Task in `tasks/done/` or `tasks/released/`. | No active next role remains. | none |

Never move a task forward by changing only the status text. The required artifact and evidence must exist.

## Internal Artifact Policy

Internal files are for agents, not end users.

1. Write tasks, briefs, reports, release plans, and managed wiki pages in English.
2. Keep internal artifacts concise, structured, evidence-oriented, and free of user-facing narration.
3. Prefer pointers to source artifacts and changed files over repeating the full story.
4. `$4DreamTeam` lead translates and summarizes results for the user in the user's language.

## File Contract

Roles pass state only through files:

- `/tasks/backlog/EPIC-XXXX.md`
- `/tasks/analytic/TASK-XXXX.md`
- `/tasks/developer/TASK-XXXX.md`
- `/tasks/quality/TASK-XXXX.md`
- `/tasks/wiki/TASK-XXXX.md`
- `/tasks/release/TASK-XXXX.md`
- `/tasks/released/TASK-XXXX.md`
- `/tasks/done/TASK-XXXX.md`
- `/tasks/rejected/TASK-XXXX.md`
- `/reports/product/EPIC-XXXX-report.md`
- `/reports/product/accepted/EPIC-XXXX-review.md`
- `/reports/product/rejected/EPIC-XXXX-review.md`
- `/reports/tasks/TASK-XXXX-report.md`
- `/reports/quality/accepted/TASK-XXXX-quality.md`
- `/reports/quality/rejected/TASK-XXXX-quality.md`
