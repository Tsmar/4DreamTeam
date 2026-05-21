# <project-name> Source Map

<!-- wiki-meta
status: actual
mode: bootstrap
backing: approved-sources
source_state: backed-by-code
-->

## Status

actual

## Purpose

Semantic navigation map for approved sources. This page helps agents find the source of truth for product behavior, architecture, implementation, documentation, infrastructure, and release history without reading the whole project.

`source-map.md` is the editable source of truth. Generated files under `.index/` are derived from this page and must not be edited manually.

## Source Roots

<!-- source-root
id: <root-id>
path: <approved-source-path>
resolved_path: <resolved-source-path-or-same-as-path>
type: frontend / backend / fullstack / skill-development / docs / infra / library / mixed / unknown
purpose: <why this source root exists>
write_policy: read-only / writable-with-approved-task / requires-confirmation
changelog_policy: none / source-changelog-if-exists / source-changelog-required
-->

| Root | Resolved Path | Type | Purpose | Write Policy | Changelog Policy |
|---|---|---|---|---|---|
| `<approved-source-path>` | `<resolved-source-path-or-same-as-path>` | `<type>` | <purpose> | `<policy>` | `<policy>` |

## Source Areas

### Area: <area-name>

Root:
`<approved-source-path>`

Type:
`<type>`

Purpose:
<what this source area owns>

Primary Questions:
- <question this area answers>
- <question this area answers>

Semantic Groups:
- `<group-id>`

<!-- source-group
id: <group-id>
area: <area-id>
root: <root-id>
type: <type>
used_by: product,analytic,developer,quality,wiki,devops,release
keywords: <keyword>,<keyword>
-->

#### Group: <group-name>

Purpose:
<what an agent learns from this group>

Primary Questions:
- <question this group answers>
- <question this group answers>

Primary Files:
- `<approved-source-path/file>` - <why this file is primary>

Supporting Files:
- `<approved-source-path/file>` - <when to read this file>

Related Wiki Pages:
- `<relative-wiki-page>`

Update Triggers:
- <when this group must be reviewed>

Notes:
- <known limitation, unknown, or boundary>
