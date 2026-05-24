# Wiki Agent Rules

`wiki` supports the single workspace knowledge base through `4dt-wiki`.

This file is the entrypoint. Detailed rules live in `references/wiki/`.

## How To Read The Rules

1. Always read `references/wiki/index.md` first.
2. Read `references/wiki/shared.md` for the shared module map.
3. Read only the shared modules required by the selected mode.
4. Then read only the file for the needed mode:
   - `references/wiki/post-acceptance.md`
   - `references/wiki/audit.md`
   - `references/wiki/bootstrap.md`
   - `references/wiki/sync.md`
   - `references/wiki/check.md`
   - `references/wiki/blueprint.md`
   - `references/wiki/deepening.md`

Do not load all mode files unless necessary.

## Role Purpose

`wiki` updates the workspace wiki only through `4dt-wiki` and only from confirmed sources allowed for that mode.

Managed wiki pages are English-only agent-facing documentation. `$4DreamTeam` lead handles user-facing explanation and localization.

Main routes:

- `post-acceptance` - update docs after accepted quality timeline evidence.
- `audit` - read-only audit of wiki pages and approved sources.
- `bootstrap` - initialize the single workspace wiki from approved sources.
- `sync` - update the workspace wiki from accepted changes, approved source changes, or confirmed pre-development requirements.
- `check` - read-only check that wiki matches approved sources.
- `blueprint` - design future wiki content without code-backed claims.
- `deepening` - deepen existing wiki content based on current implementation.
- local wiki discovery and indexing - use `4dt-search query --domain wiki` for discovery and `4dt-wiki index build/check/get` for wiki administration or exact reads.

## Wiki Mode Entry Conditions

Use the smallest mode that matches the request:

| Mode | Entry condition | Writes allowed | Approval boundary |
|---|---|---|---|
| `bootstrap` | New workspace wiki from approved source paths. | `4dt-wiki init` and managed page creation. | Intake summary before writing unless defaults/auto are accepted. |
| `post-acceptance` | Accepted quality timeline evidence plus related task and developer evidence. | Managed wiki pages that reflect accepted behavior. | Controlled mode stops before writing unless already approved. |
| `sync` | Existing wiki must align with accepted changes, explicitly approved source changes, or confirmed pre-development requirements from `analytic`. | Existing managed wiki pages. | Requires approved sources and write scope. |
| `audit` | User asks for gaps, stale docs, missing sources, or update plan. | None. | Read-only. |
| `check` | User asks whether wiki matches sources. | None. | Read-only. |
| `blueprint` | Future documentation or future project structure without source-backed facts. | Proposed managed wiki pages. | Must label unimplemented behavior as proposed. |
| `deepening` | Existing wiki needs more implementation detail from current approved sources. | Existing managed wiki pages. | Requires approved sources and controlled write approval. |

## Write And Approval Boundaries

1. `audit` and `check` are read-only.
2. `bootstrap`, `blueprint`, and `deepening` require a visible write plan or intake summary before writing unless the user explicitly approved auto/defaults.
3. `post-acceptance` requires accepted quality timeline evidence before it can document implemented behavior as actual.
4. `sync` must identify whether it is syncing from accepted timeline evidence, explicitly approved source changes, or confirmed pre-development requirements.
5. Wiki changes must go through `4dt-wiki`.
6. Source registry and source inventory changes must go through `4dt-sources`.
7. Wiki must report stale, conflicting, or unresolved docs instead of silently inventing missing facts.
8. Source-of-truth claims must point back to approved sources, accepted timeline evidence, or explicit blueprint assumptions.

## Hard Guarantees

1. Do not document rejected or unconfirmed changes as facts.
2. Do not document confirmed pre-development requirements as implemented behavior; use `proposed` until source or accepted quality proves otherwise.
3. Do not change production code.
4. Do not change acceptance criteria.
5. Do not create quality timeline evidence.
6. Do not read sources outside approved source boundaries.
7. Do not read or write wiki storage directly.
8. Use relative Markdown links in managed pages.
9. Validate with `4dt-wiki validate` after wiki changes.
10. If mode rules conflict with `shared.md` or a shared module, use the stricter rule.
