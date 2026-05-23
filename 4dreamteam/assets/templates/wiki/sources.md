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

Human-readable registry of approved source boundaries for this managed wiki. Low-token source inventory is generated and queried by `4dt-sources`.

## Operator Confirmation

- First-touch status: confirmed / denied / absent / pending
- Confirmed by: <operator>
- Confirmed at: YYYY-MM-DD
- Confirmation scope: all current `sources/` contents / explicit external source path
- Rescan required for new files: yes

## Source Roots

| Source ID | Workspace Alias | Resolved Path | Type | Confirmation Status | Inventory Manifest | Access |
|---|---|---|---|---|---|---|
| `<source-id>` | `sources/<path>` | `<resolved-path>` | directory / file | operator approved | `4dt-sources` | read-only |

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
