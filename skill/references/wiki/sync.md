# Wiki Mode: Sync

Update a managed wiki from accepted changes or explicitly approved source changes.

## Purpose

Bring an existing wiki into alignment with the current confirmed state.

## Allowed Triggers

1. Accepted quality report.
2. Explicitly approved source changes.
3. The user explicitly asks to synchronize an existing wiki with approved sources.

## Required Inputs

1. Project name or path to `docs/<project-name>`.
2. Existing managed wiki.
3. Approved sources or accepted report context.

## Workflow

1. Read `docs/<project-name>/sources.md` if it exists.
2. Compare approved sources with current user-approved boundaries.
3. Read relevant wiki pages.
4. Read relevant approved sources.
5. Find stale, missing, and incorrect pages.
6. Before writing, show a sync plan unless the user gave auto permission.
7. Update only pages that actually changed according to approved sources.

## Write Scope

Allowed writes:

- `docs/<project-name>/`
- `docs/index.md`, if the registry entry changes.

## Status

Use:

- `actual` for code-backed current behavior;
- `accepted` only for changes confirmed by an accepted quality report;
- `unknown` if the source of truth is unavailable.

## Stop Conditions

Stop if:

1. The project wiki cannot be determined.
2. Approved source boundaries cannot be confirmed.
3. Reading sources outside approved scope is required.
4. Sync may overwrite a proposed blueprint without explicit confirmation.
