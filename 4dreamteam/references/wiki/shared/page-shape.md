# Wiki Page Shape

Use this file when creating, syncing, deepening, or materially reshaping managed wiki pages.

## Language Policy

Managed wiki pages are written in English only, regardless of the user request language, source language, or existing workspace language.

When creating, syncing, deepening, or substantially expanding a knowledge base:

1. Write page titles, headings, summaries, explanations, statuses, notes, and ADR content in English.
2. Translate or summarize non-English user input and source documentation into English.
3. If an existing managed wiki contains non-English prose, keep the workflow focused on the requested scope, migrate touched pages to English, and report remaining mixed-language areas.

Never translate:

- variable names;
- function names;
- class names;
- schema and table names;
- API routes and endpoints;
- event names;
- filenames and directory names;
- package names;
- protocol names and external technical terms when they are part of the source contract.

## Multi-Project Knowledge Base Shape

Create a separate directory for each project:

```txt
docs/<project-name>
  <project-name>.md
  product/
  architecture/
  domains/
  flows/
  entities/
  contracts/
  schemas/
  frontend/
  backend/
  integrations/
  decisions/
  sources.md
```

The minimum bootstrap must create:

1. `docs/<project-name>/<project-name>.md`
2. `docs/<project-name>/product/overview.md`
3. `docs/<project-name>/sources.md`

Create additional sections only if they reflect real approved sources or an explicitly proposed blueprint.

## Audience-Aware Architecture

Documentation is written for two audiences:

1. Product audience - product team, analysts, managers, stakeholders.
2. Technical audience - developers, tech leads, QA, DevOps.

Do not create two independent wikis. Create one connected wiki with different depths:

1. Product layer explains `what`, `why`, `for whom`, main capabilities, workflows, terms, and constraints.
2. System layer explains architecture, runtime, modules, integrations, contracts, schemas, and domain boundaries.
3. Implementation layer explains entrypoints, handlers, components, storage, state, tests, and stable architecture units.

## Documentation Depth

Use three depth levels:

1. Depth 1: product map - capabilities, workflows, glossary, constraints.
2. Depth 2: system map - architecture, modules, integrations, contracts, schemas, domains.
3. Depth 3: implementation map - entrypoints, handlers, components, storage, state, tests.

Create depth 3 only for stable architecture units that genuinely help developers find the right place in code.

## Drilldown Links

Each product workflow should link to technical pages when confirmed by approved sources or explicitly proposed as a blueprint:

```txt
product/workflows/<workflow>.md
  -> flows/<workflow>.md
  -> frontend/... or backend/...
  -> contracts/...
  -> schemas/...
```

Technical pages should link back to product capability or workflow if the relationship is known.

If the relationship is unknown, do not invent it. Mark it as `requires source access`.

## Page Status Policy

Do not add status to ordinary wiki filenames.

Correct:

```txt
product/overview.md
architecture/overview.md
flows/create-order.md
contracts/order-api.md
decisions/ADR-0001-auth-model.md
```

Incorrect:

```txt
product/overview.proposed.md
architecture/overview.accepted.md
flows/create-order.actual.md
```

Record status inside the page:

```md
## Status

proposed / actual / accepted / superseded / deprecated / unknown
```

For managed wiki pages, add a machine-readable block:

```md
<!-- wiki-meta
status: proposed
mode: blueprint
backing: user-brief
source_state: not-backed-by-code
-->
```

Statuses:

- `proposed` - a design assumption not yet confirmed by code or accepted quality report.
- `actual` - behavior confirmed by approved source code.
- `accepted` - change confirmed by an accepted quality report.
- `superseded` - page or decision replaced by newer material.
- `deprecated` - behavior exists but is no longer recommended.
- `unknown` - status cannot be confirmed from approved sources.

Blueprint pages always start with status `proposed`.

Code-backed bootstrap, sync, check, and deepening pages use `actual` when behavior is confirmed by approved sources.

Post-acceptance wiki updates use `accepted` for changes connected to an accepted quality report.
