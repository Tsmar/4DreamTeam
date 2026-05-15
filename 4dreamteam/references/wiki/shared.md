# Wiki Shared Rules

Common wiki rules are modular. Read this file first, then load only the shared module required by the selected wiki mode.

## Shared Module Map

- `shared/source-boundaries.md` - approved source boundaries, ignore list, source truth, and project name rules.
- `shared/page-shape.md` - language policy, multi-project wiki shape, audience-aware architecture, documentation depth, drilldown links, and page status policy.
- `shared/source-map.md` - source-map purpose and structure.
- `shared/indexing.md` - generated local index rules, Python index commands, and index-first navigation.

## Mode-To-Module Guide

Use the smallest shared rule set that protects the selected mode:

| Mode or need | Shared modules to read |
|---|---|
| Source access, bootstrap, sync, check, audit, deepening | `source-boundaries.md` |
| Creating or materially reshaping pages | `page-shape.md` |
| Updating `source-map.md` | `source-map.md` and `indexing.md` |
| Searching an existing wiki/source map | `indexing.md` |
| Status-only or exact page review | only the exact module needed by the check |

All wiki modes still follow `references/wiki.md` and the selected mode file. If modules conflict, use the stricter rule.

## Hard Guarantees

1. Approved source paths are hard read boundaries.
2. Generated `.index/*` files are derived artifacts and must not be edited manually.
3. Use the bundled Python wiki index tooling when rebuilding or checking generated indexes.
4. Search results do not expand source permissions.
5. Do not document rejected or unconfirmed behavior as fact.
6. Managed wiki prose is English-only unless repository rules explicitly change.
7. Factual claims must be backed by approved sources, accepted reports, or explicit blueprint assumptions.
