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

Managed wiki pages are English-only agent-facing documentation. `$4DreamTeam` lead handles user-facing explanation and localization.

Main routes:

- `post-acceptance` - update docs after an accepted quality report.
- `audit` - read-only audit of docs and sources.
- `bootstrap` - create a managed wiki from approved sources.
- `sync` - update a managed wiki from accepted changes or approved source changes.
- `check` - read-only check that wiki matches approved sources.
- `blueprint` - design a future wiki without code-backed claims.
- `deepening` - deepen an existing wiki based on current implementation.
- source map and local index work - maintain `docs/<project-name>/source-map.md` and generated `.index/*` files when the selected mode changes source navigation.

## Wiki Mode Entry Conditions

Use the smallest mode that matches the request:

| Mode | Entry condition | Writes allowed | Approval boundary |
|---|---|---|---|
| `bootstrap` | New managed wiki from explicitly approved source paths. | New `docs/<project-name>/` plus `docs/index.md`. | Intake summary before writing unless defaults/auto are accepted. |
| `post-acceptance` | Accepted quality report plus related task and developer report. | Docs that reflect accepted behavior. | Controlled mode stops before writing unless already approved. |
| `sync` | Existing managed wiki must align with accepted changes or explicitly approved source changes. | Existing project wiki pages and source map. | Requires approved sources and write scope. |
| `audit` | User asks for gaps, stale docs, missing sources, or update plan. | None. | Read-only. |
| `check` | User asks whether wiki matches sources. | None. | Read-only. |
| `blueprint` | Future documentation or future project structure without source-backed facts. | Proposed docs only. | Must label unimplemented behavior as proposed. |
| `deepening` | Existing wiki needs more implementation detail from current approved sources. | Existing project wiki pages and source map. | Requires approved sources and controlled write approval. |

## Write And Approval Boundaries

1. `audit` and `check` are read-only.
2. `bootstrap`, `blueprint`, and `deepening` require a visible write plan or intake summary before writing unless the user explicitly approved auto/defaults.
3. `post-acceptance` requires an accepted quality report before it can document implemented behavior as actual.
4. `sync` must identify whether it is syncing from accepted reports or explicitly approved source changes.
5. Wiki may update `source-map.md` when source navigation changes, but generated `.index/*` files must be rebuilt, not edited by hand.
6. Wiki must report stale, conflicting, or unresolved docs instead of silently inventing missing facts.
7. Source-of-truth claims must point back to approved sources, accepted reports, or explicit blueprint assumptions.

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
