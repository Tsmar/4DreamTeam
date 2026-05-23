# Workspace Model

4DreamTeam workspaces are script-managed overlays for project work.

Agents use scripts as the stable API:

- `4dt-board` manages epics, tasks, columns, metadata, and timeline entries.
- `4dt-wiki` manages the single workspace wiki.
- `4dt-sources` manages approved source boundaries and source inventory.
- `4dt-memory` manages workspace-local memory.

The underlying Markdown files remain human-readable storage, but agents do not read or write board or wiki storage directly.

## Required Artifacts

- `AGENTS.md`
- script-managed `tasks/`
- script-managed `docs/`
- workspace-local `.4dt/`
- git-ignored `sources/`

## Board

The board is role-based. Use `4dt-board status`, `4dt-board list`, `4dt-board get`, `4dt-board move`, and `4dt-board comment add` for all task work.

Supported columns: `backlog`, `analytic`, `developer`, `quality`, `wiki`, `release`, `released`, `done`, and `rejected`.

Reports are timeline entries on tasks. There is no active standalone report-file workflow for new work.

## Wiki

The workspace has one wiki, managed by `4dt-wiki`.

Baseline pages include overview, product overview, architecture overview, changelog, and source registry integration.

Use `4dt-wiki search/get` before broad source reading.

## Sources

The workspace `sources/` folder is readable by default.

External source boundaries are added explicitly with `4dt-sources registry add --operator-approved`. The registry is the single source of truth for approved external source access.

## Runtime

Workspace runtime and memory live in `.4dt/` so a workspace can be archived or moved with its local state.
