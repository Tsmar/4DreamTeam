# Workspace Preflight

Use this file at the start of a new session and before writing files in a workspace.

## New Session Startup

Start every new session with command-based startup checks. Do not inspect managed storage folders directly.

1. Read `AGENTS.md` if present.
2. Run memory readiness:

```bash
4dt-memory doctor --workspace . --json
```

3. If memory is `ready`, immediately load default project rules, operator preferences, active modes, and workflow constraints from contract memory:

```bash
4dt-memory defaults load --workspace . --json
```

If defaults load as `ready`, apply them without asking the operator to repeat context. If defaults are incomplete or invalid, run `4dt-memory onboarding questions --workspace . --json` and ask only the returned repair or setup questions before treating a mode or rule as active. If memory is degraded, unavailable, empty, or low-signal, report that state and continue from current workspace instructions. Do not invent remembered rules.

4. Run the four startup checks:

```bash
4dt-board --workspace . --json validate
4dt-sources --workspace . --json registry validate
4dt-wiki --workspace . --json validate
4dt-memory doctor --workspace . --json
```

5. Report one status line for each tool: `4dt-board`, `4dt-sources`, `4dt-wiki`, and `4dt-memory`.
6. Name the workspace state: `no_workspace`, `uninitialized`, `partially_initialized`, `degraded_tooling`, or `ready`.
7. Offer situation-aware next actions for the operator to choose from.

Repair commands require explicit operator confirmation. If one tool is broken, propose partial or recovery choices based on the specific state instead of blocking all work by default.

## Available Modes

After onboarding, report only modes that are safe for the current state:

- `read-only/status`
- `product shaping`
- `analytic`
- `developer`
- `quality`
- `wiki`
- `release`
- `devops`
- `recovery`

If `4dt-board` is unavailable, task workflow modes require `recovery`. If `4dt-memory` is degraded, work may continue without memory after reporting the degraded state.

## Empty Workspace Bootstrap

After confirmation, create only:

- `AGENTS.md` from `assets/templates/workspace/AGENTS.md`;
- `sources/.gitignore` from `assets/templates/workspace/sources.gitignore`;
- board artifacts through `4dt-board`;
- wiki artifacts through `4dt-wiki`;
- source registry through `4dt-sources`;
- memory storage through `4dt-memory`.

Do not create a local `skill/` folder in a normal workspace.

## Source Boundary

Workspace `sources/` is readable by default.

All external source paths must be registered explicitly through `4dt-sources registry add --operator-approved`. The registry list is the single source of truth for approved external source access.
