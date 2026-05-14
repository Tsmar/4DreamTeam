# Wiki Mode: Blueprint

Design a future wiki or future documentation state.

## Purpose

Create a proposed documentation architecture before code-backed implementation or an accepted quality report exists.

Blueprint is useful for:

1. a future project;
2. a future major refactor;
3. a planned domain model;
4. designing the knowledge base structure;
5. aligning the product and technical documentation map before implementation.

## Source Model

Blueprint may rely on:

1. user brief;
2. existing docs if the user approved reading them;
3. approved planning documents;
4. approved source code if it exists, while unconfirmed future claims remain `proposed`.

Do not present proposed content as confirmed implementation.

## Intake

Collect:

1. project name;
2. blueprint goal;
3. audience;
4. expected product capabilities;
5. expected technical areas;
6. known constraints;
7. allowed input docs or sources, if any.

If project name is missing, stop and ask for it.

## Blueprint Gate

Before writing, show a blueprint summary:

1. project name;
2. output path `docs/<project-name>`;
3. backing: `user-brief`, `planning-docs`, `mixed`, or another precise description;
4. status policy: all created pages start as `proposed`;
5. pages to create or update;
6. known unknowns;
7. sources or briefs used.

Do not create or update files before user confirmation, except with explicit auto permission.

## Write Scope

Allowed writes:

- `docs/<project-name>/`
- `docs/index.md`, if a new wiki entry is created.

## Page Requirements

Each blueprint page must contain:

```md
<!-- wiki-meta
status: proposed
mode: blueprint
backing: user-brief
source_state: not-backed-by-code
-->

## Status

proposed
```

If part of the page is confirmed by sources and part is proposed, separate the sections explicitly:

```md
## Confirmed by sources

...

## Proposed

...
```

## Stop Conditions

Stop if:

1. The user expects code-backed facts but did not provide approved sources.
2. The blueprint would conflict with an existing actual/accepted wiki without an explicit user decision.
3. The project name is invalid and the user has not confirmed normalization.
