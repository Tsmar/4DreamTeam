# Wiki Mode: Sync

Update a managed wiki from accepted changes, confirmed workspace source changes, explicitly approved external source changes, or confirmed pre-development requirements.

## Purpose

Bring an existing wiki into alignment with the current confirmed state.

## Allowed Triggers

1. Accepted quality report.
2. Confirmed workspace source changes or explicitly approved external source changes.
3. The user explicitly asks to synchronize an existing wiki with approved sources.
4. `analytic` has a user-confirmed decision that must align managed docs before developer handoff.

## Required Inputs

1. Project name or path to `docs/<project-name>`.
2. Existing managed wiki.
3. Approved sources, accepted report context, or confirmed analytic decision context.

## Workflow

1. Read `docs/<project-name>/sources.md` if it exists.
2. Compare approved sources with current operator-approved boundaries.
3. If workspace `sources/` first-touch confirmation is missing, stop before listing, statting, resolving, inventorying, indexing, or reading it.
4. If confirmed workspace sources changed since the last inventory, ask for rescan/actualization confirmation before inspecting new files.
5. Rebuild or check source inventory before reading source content when source registry state changed.
6. Read relevant wiki pages.
7. Read relevant approved sources.
8. Find stale, missing, and incorrect pages.
9. Before writing, show a sync plan unless the user gave auto permission.
10. Update only pages that actually changed according to approved sources, accepted reports, or confirmed pre-development requirements.
11. If source ownership or navigation changed, update `sources.md`, `source-map.md`, and rebuild the generated `.index` files when bundled Python wiki index tooling is available.
12. When syncing pre-development requirements, use `proposed` status and make clear that the behavior is confirmed as intended scope, not implemented behavior.

## Write Scope

Allowed writes:

- `docs/<project-name>/`
- `docs/index.md`, if the registry entry changes.

## Status

Use:

- `actual` for code-backed current behavior;
- `accepted` only for changes confirmed by an accepted quality report;
- `proposed` for confirmed pre-development requirements that are not yet implemented;
- `unknown` if the source of truth is unavailable.

## Stop Conditions

Stop if:

1. The project wiki cannot be determined.
2. Approved source boundaries cannot be confirmed.
3. Reading sources outside approved scope is required.
4. Sync may overwrite a proposed blueprint without explicit confirmation.
