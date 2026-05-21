# Wiki Mode: Bootstrap

Create a managed wiki for an existing project from confirmed workspace sources or explicitly specified approved external sources.

## Required User Inputs

The user must specify at least:

```txt
Knowledge base name:
<project-name>

Sources:
- sources/ after operator first-touch confirmation, or
- <explicit-approved-external-source-path>
```

Do not ask the user for the output path. It is always computed automatically:

```txt
docs/<project-name>
```

## Optional Inputs

If the user does not specify optional inputs, use these defaults:

1. Project type: `unknown`, then infer from approved sources.
2. Audience: `product + technical`.
3. Detail depth: depends on audience.
4. Document discovered flows/contracts/schemas/integrations: `yes` if confirmed by approved sources.
5. Knowledge base language: English.
6. Technical details style: English prose, while code terms, variable names, functions, classes, schemas, APIs, endpoints, files, and directories stay as in sources.

## Intake

Before creating the knowledge base, collect missing parameters. Do not ask questions if the user already provided the answer.

Minimum parameters:

1. Knowledge base name or project name.
2. Approved sources, or operator confirmation that the workspace `sources/` directory may be used.
3. Project type: `backend`, `frontend`, `fullstack`, `library/SDK`, `mixed`, `unknown`.
4. Audience: `product + technical`, `product only`, `technical only`.
5. Whether to document discovered `flows`, `contracts`, `schemas`, `integrations`.
6. Forbidden paths beyond the standard ignore list.

If project name and approved sources are missing, stop and ask. If the user wants to use workspace `sources/`, first ask the operator to personally inspect and confirm the `sources/` first-touch gate before any listing, stat, resolution, inventory, indexing, or reading.

During intake, the agent must clearly show:

1. which answers are required;
2. which parameters will use defaults;
3. a short description of each item;
4. an example valid answer the user can send next.

## Intake Gate

First perform bootstrap intake and show a summary.

Do not create or update files before user confirmation.

Before confirmation, it is forbidden to:

1. create or update `docs/<project-name>`;
2. update `docs/index.md`;
3. create `sources.md`;
4. read approved sources deeper than needed for a minimal check of explicitly specified paths;
5. list, stat, resolve, inventory, index, or read workspace `sources/` before operator first-touch confirmation.

The summary must include:

1. project name;
2. computed output path `docs/<project-name>`;
3. approved sources or the required `sources/` first-touch confirmation state;
4. project type;
5. audience;
6. detail depth computed from audience;
7. knowledge base language: English;
8. technical details style: English prose with source identifiers preserved;
9. discovered flows/contracts/schemas/integrations policy;
10. additional forbidden paths.

After the summary, stop and wait for confirmation.

The only exception is when the user explicitly writes: `I accept intake defaults`, `proceed without confirmation`, or equivalent direct permission.

## Bootstrap Rules

1. Read only approved sources for the specific project.
2. Each approved source is a recursive read boundary.
3. If `sources/` is confirmed, run the source inventory before reading source content and record the registry in `sources.md`.
4. If `../project-a/src` is specified, read only `../project-a/src/**` subject to the ignore list.
5. Do not read parent directories, sibling directories, or inferred project roots outside the specified source.
6. If an additional source is needed, stop and ask for access.
7. Do not mix sources from different projects.
8. Write only to `docs/<project-name>` and update `docs/index.md` when needed.
9. Do not read secrets, `.env`, credentials, private keys, dumps, or unrelated user files.
10. Build the wiki as an architecture map of the project, not a folder mirror.
11. Mark unknown areas as `unknown` or `requires source access`.
12. Use relative Markdown links.

## Minimum Output

The minimum bootstrap must create:

1. `docs/<project-name>/<project-name>.md`
2. `docs/<project-name>/product/overview.md`
3. `docs/<project-name>/sources.md`

Recommended bootstrap output:

1. `docs/<project-name>/source-map.md` when approved sources contain meaningful source areas or multiple important artifact types.
2. `docs/<project-name>/.index/source-map.json` and `docs/<project-name>/.index/manifest.json` when bundled Python wiki index tooling is available.
3. `docs/<project-name>/.index/sources/manifest.json` and `docs/<project-name>/.index/sources/<source-id>.json` when source inventory tooling is available and confirmed sources are used.

Create additional sections only if they reflect real approved sources.
