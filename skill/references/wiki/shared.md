# Wiki Shared Rules

Common rules are mandatory for all wiki modes.

## Source Boundaries

An approved source is a hard boundary.

Read only descendants of the specified source path.

Forbidden:

1. parent directories;
2. sibling directories;
3. inferred project roots;
4. neighboring projects;
5. files outside approved sources, even if they seem obviously related.

If a file outside an approved source is needed for a correct wiki, stop and request access to that exact path.

## Ignore List

Approved sources are read recursively, excluding:

```txt
.git
node_modules
dist
build
out
coverage
.cache
.next
.nuxt
.vite
.turbo
.vercel
.DS_Store
*.log
*.tmp
*.bak
.env
.env.*
*.pem
*.key
*.p12
*.sqlite
*.db
*.dump
vendor
target
.gradle
.idea
.vscode
__pycache__
.pytest_cache
.mypy_cache
```

The user may add forbidden paths beyond the standard list.

## Source Truth

Code in approved sources is the primary source of truth.

Do not invent behavior that does not exist in approved code sources.

If behavior is not visible from approved sources, mark it as `unknown` or `requires source access`.

Documentation, tests, and comments are used only if they are inside approved sources.

## Language Policy

When creating or substantially expanding a knowledge base, clarify:

1. Which language to use for the knowledge base.
2. How to write technical details:
   - fully in English;
   - in the general knowledge base language, preserving only terms from code and sources in English.

If the user does not specify a language, use the language of the request or existing documentation.

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

## Project Name Rules

`project name` is used as the directory name in `docs/<project-name>`.

Allowed format:

```txt
^[a-z0-9]+(-[a-z0-9]+)*$
```

Rules:

1. Lowercase Latin letters, digits, and hyphens only.
2. No spaces.
3. No `_`.
4. No dots.
5. Must not start or end with a hyphen.
6. Must not contain `..`, `/`, or `\`.
7. Length from 2 to 64 characters.

If the user provides an invalid name, propose a normalized version and ask for confirmation.

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

## Source Map

Managed wikis may include a semantic source map:

```txt
docs/<project-name>/source-map.md
```

`source-map.md` is a navigation layer over approved sources, not a raw file manifest. It answers:

```txt
Where is the source of truth for this behavior, contract, workflow, role, schema, integration, or release artifact?
```

Keep `sources.md` and `source-map.md` separate:

1. `sources.md` records approved source boundaries, denied paths, requested sources, and ignore policy.
2. `source-map.md` groups files by semantic purpose and points agents to the right source files and related wiki pages.

Use this hierarchy:

```txt
approved source root
-> source area
-> semantic group
-> primary/supporting files
-> related wiki pages
-> update triggers
```

Each source map must support multiple approved source roots and project shapes such as `frontend`, `backend`, `fullstack`, `skill-development`, `docs`, `infra`, `library`, `mixed`, or `unknown`.

Do not mirror the full file tree. Include only files that help an agent answer a meaningful question or locate a source of truth.

## Local Wiki Index

Generated index files may live under:

```txt
docs/<project-name>/.index/
  source-map.json
  manifest.json
```

Rules:

1. `source-map.md` is the editable source of truth.
2. `.index/source-map.json` and `.index/manifest.json` are generated artifacts.
3. Agents must not edit `.index/*` manually.
4. Rebuild the index after source map changes with:

```bash
bun skill/tools/wiki.ts index build <docs-project-path>
```

5. Check the index with:

```bash
bun skill/tools/wiki.ts index check <docs-project-path>
```

6. Search the index with:

```bash
bun skill/tools/wiki.ts search <docs-project-path> "<query>"
```

If the tooling is unavailable in the current workspace, keep `source-map.md` updated and report that local index generation was not run.

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
