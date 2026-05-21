# <project-name> Sources

<!-- wiki-meta
status: actual
mode: bootstrap
backing: operator-confirmed-sources
source_state: source-registry
-->

## Status

actual

## Purpose

Human-readable registry of approved source boundaries for this managed wiki. Generated low-token source inventory lives under `.index/sources/` and must not be edited manually.

## Operator Confirmation

- First-touch status: confirmed / denied / absent / pending
- Confirmed by: <operator>
- Confirmed at: YYYY-MM-DD
- Confirmation scope: all current `sources/` contents / explicit external source path
- Rescan required for new files: yes

## Source Roots

| Source ID | Workspace Alias | Resolved Path | Type | Confirmation Status | Inventory Manifest | Access |
|---|---|---|---|---|---|---|
| `<source-id>` | `sources/<path>` | `<resolved-path>` | directory / file / symlink | confirmed | `.index/sources/<source-id>.json` | read-only |

## Standard Ignore Policy

Use the standard 4DreamTeam wiki ignore list from `references/wiki/shared/source-boundaries.md`.

## Additional Forbidden Paths

- none

## Requested Sources

| Requested Path | Reason | Status |
|---|---|---|
| `<path>` | `<why needed>` | requested / approved / denied |

## Notes

- Source inventory records path metadata only and does not read file contents.
- Symlinked sources must record both the workspace alias and resolved target.
- New files added after confirmation require separate rescan/actualization confirmation.
