# Wiki Mode: Check

Read-only check that a managed wiki matches approved sources.

## Purpose

Verify that documentation does not contradict approved source code and correctly marks unknown/proposed areas.

## Rules

1. May run without an accepted quality report.
2. Do not change files.
3. Read only the existing wiki and approved sources.
4. Do not draw conclusions from sources outside approved boundaries.

## Workflow

1. Identify `docs/<project-name>`.
2. Read `sources.md` if it exists.
3. Check that user-approved sources match listed sources, or explicitly record the mismatch.
4. Compare key wiki claims with approved sources.
5. Separately check statuses and `wiki-meta`.
6. Check relative links for local wiki pages that should exist.
7. Check whether product-facing pages are understandable without reading implementation details first.
8. If `source-map.md` exists, check that it is not a raw file manifest and that primary links point to approved sources.
9. If `.index/source-map.json` exists, run or recommend `python3 <resolved-skill-path>/scripts/wiki_index.py index check <docs-project-path>` to detect stale generated index state.
10. Report findings by severity.

## Output

Return:

1. Checked scope.
2. Findings: contradictions, stale claims, unsupported claims, missing links, missing sources, invalid statuses, missing `wiki-meta`, unclear product-facing pages, stale source map or generated index.
3. Residual risk.
4. Recommended next mode: `sync`, `deepening`, `audit`, or no action.
