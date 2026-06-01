# Lead Lifecycle

Use this file when moving tasks between board columns or checking lifecycle state.

## Board Interface

The board is managed through `4dt-board`.

Agents must not read or write the board storage directly. Use the script for every operation:

- `4dt-board status` for column summary.
- `4dt-board list` or `4dt-board find` for discovery.
- `4dt-board get`, `4dt-board section get`, and `4dt-board comments list/latest` for task details.
- `4dt-board create epic` and `4dt-board create task` for new work.
- `4dt-board move` and `4dt-board set-status` for lifecycle movement.
- `4dt-board comment add` for product, analytic, developer, quality, wiki, release, and lead timeline entries.
- `4dt-board validate` before handoff, acceptance, release packaging, or workspace status summaries.

Supported columns: `backlog`, `analytic`, `developer`, `quality`, `wiki`, `release`, `released`, `done`, and `rejected`.

The current column determines the next owner role. Do not use `next_owner`.

## Board Status Contract

Board columns are the role ownership contract. Status is a narrower lifecycle note and must use the exact values accepted by `4dt-board validate`.

Supported epic statuses: `shaping`, `ready_for_analytic`, `ready_for_developer`, `in_delivery`, `blocked`, `done`, and `rejected`.

Supported task statuses: `proposed`, `ready`, `in_progress`, `blocked`, `needs_input`, `needs_rework`, `accepted`, `done`, and `rejected`.

Do not invent aliases such as `working`, `in-delivery`, `ready-for-analytic`, `ready-for-developer`, `quality_accepted`, or `quality_rejected` as item statuses. `quality_acceptance` and `quality_rejection` are timeline entry types, not task statuses.

## Movement Rules

1. `product` creates and shapes epics and task candidates with `4dt-board`.
2. Every epic contains only tasks as child work items. Do not create Product or Item entities.
3. `product` may keep an epic in `backlog`, hand its tasks to `analytic`, or hand clear delivery tasks directly to `developer`.
4. `analytic` moves implementation-ready task specs to `developer` only after required documentation alignment is complete or explicitly not required.
5. When analytic decisions require pre-development documentation alignment, `wiki sync` updates managed docs with `proposed` status before developer handoff.
6. `developer` appends a `developer_implementation` timeline entry and moves completed implementation work to `quality`.
7. `quality` appends `quality_acceptance` or `quality_rejection`.
8. Accepted work moves to `wiki` for post-acceptance documentation review before it can move to `done` or `release`.
9. Rejected work moves to `rejected`.
10. Rework moves from `rejected` to `developer`, then back to `quality`.
11. `release` moves work from `done` to `release` only after an explicit user request for release, changelog, staging, commit, or release packaging.
12. `release` moves work from `release` to `released` only after the release branch is pushed and the chosen release publication step is complete.
13. Before an epic is closed as done or the next epic becomes the active implementation focus, lead appends a `lead_handoff` timeline entry.

## Task Lifecycle State Machine

Use `4dt-board` metadata and current column as the state source of truth. Use the task status field for finer lifecycle notes.

| State | Owner | Required evidence | Valid next transitions |
|---|---|---|---|
| `draft` | product | Product goal and audience are visible. | `product-approved`, `blocked`, `rejected` |
| `product-approved` | product | Epic has scope, non-goals, task candidates, and product acceptance criteria. | `analytic-ready`, `developer-ready`, `blocked` |
| `analytic-ready` | analytic | Technical impact can be analyzed from approved docs/sources. | `docs-alignment`, `developer-ready`, `blocked`, `needs-product` |
| `docs-alignment` | analytic / wiki | Managed docs are aligned as `proposed`, or alignment is explicitly not required/deferred. | `developer-ready`, `blocked` |
| `developer-ready` | developer | Affected areas, acceptance criteria, validation plan, and documentation alignment evidence are visible. | `developer-in-progress`, `blocked` |
| `developer-in-progress` | developer | Task status marked `in_progress`, implementation plan exists, and operator plan approval or scoped auto implementation is recorded. | `developer-done`, `blocked` |
| `developer-done` | developer | `developer_implementation` timeline entry includes checks and acceptance coverage. | `quality-review` |
| `quality-review` | quality | Quality can compare implementation to every acceptance criterion. | `accepted`, `rejected` |
| `rejected` | quality / developer | `quality_rejection` timeline entry gives actionable fixes. | `fixed`, `blocked`, `done` if abandoned |
| `fixed` | developer | Developer revision entry explains the fix. | `quality-review` |
| `accepted` | quality | `quality_acceptance` timeline entry marks every criterion `pass`. | `wiki-update` |
| `wiki-update` | wiki | Docs update is source-backed or explicitly not needed. | `release-ready`, `done` |
| `release-ready` | release | Accepted quality or product acceptance exists. | `release-planned` |
| `release-planned` | release | Release plan timeline entry lists included/excluded files and approval requirements. | `released`, `blocked` |
| `released` | release | Release timeline entry includes pushed release evidence. | `done` |
| `done` | lead | No active next role remains. | none |

Never move a task forward by changing only the status text. The required timeline evidence must exist.

## Internal Artifact Policy

Internal artifacts are for agents, not end users.

1. Write tasks, briefs, timeline entries, release plans, and managed wiki pages in English.
2. Keep internal artifacts concise, structured, evidence-oriented, and free of user-facing narration.
3. Prefer pointers to source artifacts and changed files over repeating the full story.
4. `$4DreamTeam` lead translates and summarizes results for the user in the user's language.

## Epic Completion Handoff

Create a `lead_handoff` timeline entry for every completed epic.

The handoff is durable inter-session memory for the next agent, next session, or next epic. It should be high-signal and can be long when the project is large or complex.

Rules:

1. Use `4dt-board comment add --type lead_handoff`.
2. Create the handoff before starting the next epic as the active implementation focus.
3. Include the most important accepted changes, changed files, validation evidence, workflow notes, project nuances, open threads, and suggested next starting points.
4. Prefer pointers to tasks, timeline entries, wiki pages, commits, and source files over copied source text.
5. Do not include secrets, credentials, raw logs, dumps, or large source excerpts.
6. Distinguish accepted facts from suggestions, risks, and open questions.
