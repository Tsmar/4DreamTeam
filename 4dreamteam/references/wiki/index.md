# Wiki Reference Index

This file selects the wiki mode and indicates which rules to read.

## Common Entry

For any wiki request:

1. Read `references/wiki.md`.
2. Read this file.
3. Read `shared.md`.
4. Determine the mode.
5. Read only the mode file.

## Modes

Mode selection is intentionally simple:

1. Need a new source-backed wiki -> `bootstrap`.
2. Need docs updated after accepted work -> `post-acceptance`.
3. Need existing docs aligned with approved current sources -> `sync`.
4. Need a read-only gap/staleness review -> `audit`.
5. Need read-only source conformance -> `check`.
6. Need future proposed docs -> `blueprint`.
7. Need deeper implementation detail in existing docs -> `deepening`.

### post-acceptance

File: `post-acceptance.md`

Use when there is an accepted quality report and docs need to be updated for the accepted change.

Requires:

- accepted quality report;
- related task;
- developer report.

### audit

File: `audit.md`

Read-only check of existing documentation and explicitly specified sources.

Use when the user asks to find gaps, stale pages, missing sources, or propose an update plan.

### bootstrap

File: `bootstrap.md`

Create a new managed wiki for an existing project from approved sources.

Use when the user asks to create a knowledge base for an existing project.

### sync

File: `sync.md`

Update a managed wiki from accepted changes or explicitly approved source changes.

Use when the user asks to synchronize an existing wiki with current sources.

### check

File: `check.md`

Read-only check that a managed wiki matches approved sources.

Use when the user asks to verify wiki correctness without making changes.

### blueprint

File: `blueprint.md`

Design a knowledge base for a future project or future documentation state.

Use when the user wants a preliminary structure, information architecture, proposed workflows, or documentation plan before code-backed sources exist.

### deepening

File: `deepening.md`

Deepen an existing managed wiki based on the current implementation.

Use when the user wants to expand documentation in depth: implementation details, nuances, edge cases, contracts, schemas, flows, handlers, state, storage, integrations, or test-backed behavior.

## Route Selection

If the request is ambiguous:

1. If the user talks about a new knowledge base from code, use `bootstrap`.
2. If the user talks about a future project without code, use `blueprint`.
3. If the user talks about deepening existing docs, use `deepening`.
4. If the user talks about checking without changes, use `audit` or `check`.
5. If the user talks about an accepted task, use `post-acceptance`.
6. If the user talks about aligning wiki with current sources, use `sync`.

If mode selection affects file writes and cannot be safely inferred from the request, stop and clarify the mode.

## File Map

- `shared.md` - rules for sources, statuses, language, page shape, and common write/read restrictions.
- `post-acceptance.md` - docs update after accepted quality.
- `audit.md` - read-only gap analysis.
- `bootstrap.md` - first managed wiki creation from approved sources.
- `sync.md` - managed wiki update.
- `check.md` - read-only source conformity check.
- `blueprint.md` - proposed future docs and architecture map.
- `deepening.md` - implementation-depth expansion of an existing wiki.
