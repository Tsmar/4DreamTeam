# Wiki Mode: Deepening

Deepen an existing managed wiki based on the current implementation.

## Purpose

Expand documentation in depth by clarifying details and nuances of the current implementation.

Deepening does not replace `bootstrap` and is not a post-acceptance update. It adds depth 2-3 to an existing wiki based on approved sources.

## Typical Requests

Use this mode when the user asks to:

1. deepen the wiki;
2. describe current implementation in more detail;
3. cover edge cases, flows, contracts, schemas, or modules;
4. add implementation notes;
5. connect product workflows with handlers, components, storage, state, or tests;
6. clarify architecture nuances of existing behavior.

## Required Inputs

1. Existing `docs/<project-name>`.
2. Approved sources for the area being deepened.
3. Deepening scope: whole project or a specific area.

If scope is missing, propose a safe plan based on the most important gaps and wait for confirmation before writing.

## Allowed Without Accepted Quality

Deepening may run without an accepted quality report if it documents already existing implementation from approved sources.

Do not use deepening to document a new feature before an accepted quality report exists. Use `post-acceptance` for new accepted changes.

## Intake

Collect:

1. project name or path to `docs/<project-name>`;
2. approved sources;
3. deepening scope;
4. desired depth: `depth 2`, `depth 3`, or mixed;
5. language and technical detail style if the existing wiki does not define them;
6. forbidden paths beyond the standard ignore list.

## Deepening Plan Gate

Before writing, show the deepening plan:

1. project wiki path;
2. approved sources;
3. areas to deepen;
4. pages to create;
5. pages to update;
6. expected status for pages;
7. unknowns and required extra sources, if any.

Do not create or update files before user confirmation, except with explicit auto permission.

## What To Deepen

Allowed deepening targets:

1. `architecture/` - runtime, entrypoints, module responsibilities, dependency direction.
2. `domains/` - bounded contexts, domain rules, invariants.
3. `flows/` - step-by-step behavior, branching, failure paths, retries, transactions.
4. `contracts/` - APIs, events, CLI contracts, request/response shapes.
5. `schemas/` - database schema, validation schema, serialization formats.
6. `frontend/` - routes, components, state, data fetching, UX states.
7. `backend/` - handlers, services, jobs, storage, auth, permissions.
8. `integrations/` - external systems, protocols, adapters, error handling.
9. `entities/` - stable entities, lifecycle, relationships.
10. `product/workflows/` - drilldown links to implementation details.
11. `source-map.md` - semantic navigation across approved source roots, areas, groups, and source-of-truth files.

Create only pages backed by approved sources. If a useful page cannot be backed, list it under `requires source access` instead of creating unsupported detail.

## Depth Rules

Depth 2 pages should answer:

1. What system area exists?
2. What responsibility does it own?
3. What contracts or flows touch it?
4. Where is it implemented?

Depth 3 pages should answer:

1. Which entrypoints, handlers, components, or tests prove the behavior?
2. What important branches and edge cases exist?
3. What state, storage, or external systems are involved?
4. What constraints should future developers preserve?

Do not document line-by-line implementation. Deepening is an architectural map, not a code mirror.

## Source Map Deepening

When deepening adds or clarifies architecture areas, roles, endpoints, schemas, templates, integrations, infrastructure units, or release-relevant artifacts:

1. Update `docs/<project-name>/source-map.md` with semantic groups and update triggers.
2. Rebuild `.index/source-map.json` and `.index/manifest.json` with Bun wiki tooling when available.
3. Run `bun skill/tools/wiki.ts index check <docs-project-path>` when available.

Do not add every file. Add only source files that help agents locate the source of truth.

## Status

Use:

- `actual` when backed by approved sources.
- `unknown` when the relationship is suspected but not visible.
- `proposed` only for explicit future documentation ideas, separated from actual content.

## Stop Conditions

Stop if:

1. Existing wiki cannot be found.
2. Approved sources are missing.
3. Requested scope requires reading outside approved boundaries.
4. The user asks to document behavior that sources do not confirm.
5. Deepening would overwrite accepted/proposed content with a different status without confirmation.
