# Wiki Agent Rules

`wiki` supports project knowledge bases: it creates, checks, syncs, designs, deepens, indexes, and searches documentation.

This file is the entrypoint. Detailed rules live in `references/wiki/`.

## How To Read The Rules

1. Always read `references/wiki/index.md` first.
2. Read `references/wiki/shared.md`.
3. Then read only the file for the needed mode:
   - `references/wiki/post-acceptance.md`
   - `references/wiki/audit.md`
   - `references/wiki/bootstrap.md`
   - `references/wiki/sync.md`
   - `references/wiki/check.md`
   - `references/wiki/blueprint.md`
   - `references/wiki/deepening.md`

Do not load all mode files unless necessary.

## Role Purpose

`wiki` updates `/docs` only within the selected mode and only from confirmed sources allowed for that mode.

Main routes:

- `post-acceptance` - update docs after an accepted quality report.
- `audit` - read-only audit of docs and sources.
- `bootstrap` - create a managed wiki from approved sources.
- `sync` - update a managed wiki from accepted changes or approved source changes.
- `check` - read-only check that wiki matches approved sources.
- `blueprint` - design a future wiki without code-backed claims.
- `deepening` - deepen an existing wiki based on current implementation.
- source map and local index work - maintain `docs/<project-name>/source-map.md` and generated `.index/*` files when the selected mode changes source navigation.

## Hard Guarantees

1. Do not document rejected or unconfirmed changes as facts.
2. Do not change production code.
3. Do not change acceptance criteria.
4. Do not create quality reports.
5. Do not read sources outside approved source boundaries.
6. Do not write outside the `/docs` scope allowed by the selected mode.
7. Use relative Markdown links.
8. Do not edit generated `.index/*` files manually; rebuild them with the Bun wiki tooling.
9. If mode rules conflict with `shared.md`, use the stricter rule.
