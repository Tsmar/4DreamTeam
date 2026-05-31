# Workspace Preflight

Use this file at the start of a new session and before writing files in a workspace.

## New Session Startup

Start every new session with command-based startup checks. Do not inspect managed storage folders directly.

1. Read `AGENTS.md` if present.
2. Resolve the 4DT tool launcher once, then use that launcher for every startup command in this session. In Codex skill sessions, default to the installed skill wrappers; do not probe global `4dt-*` console commands first.

```bash
# Preferred in Codex from the active installed 4DreamTeam skill package.
# Resolve this package from the active skill path or $CODEX_HOME/skills/4dreamteam;
# do not hardcode user-specific home directories.
python3 <installed-4dreamteam-skill>/scripts/4dt-memory.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-search.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-board.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-sources.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-wiki.py <args>

# Preferred only when intentionally working inside the 4DreamTeam source checkout:
npm run memory -- <args>
npm run search -- <args>
npm run board -- <args>
npm run sources -- <args>
npm run 4dt-wiki -- <args>

# Optional shortcut when console entrypoints are already known to work:
4dt-memory <args>
4dt-search <args>
4dt-board <args>
4dt-sources <args>
4dt-wiki <args>

# Diagnostic fallback:
PYTHONPATH=packages/memory/src:packages/search/src python3 -m fourdt_memory.cli <args>
PYTHONPATH=packages/search/src:packages/sources/src:packages/wiki/src:packages/board/src:packages/memory/src python3 -m fourdt_search.cli <args>
PYTHONPATH=packages/board/src python3 -m fourdt_board.cli <args>
PYTHONPATH=packages/sources/src python3 -m fourdt_sources.cli <args>
PYTHONPATH=packages/wiki/src:packages/sources/src python3 -m fourdt_wiki.cli <args>
```

Launcher order: installed skill wrapper first for normal Codex workspace startup; source-checkout npm scripts when intentionally developing the source repository; known-good console shortcuts only after the launcher is already established; direct `PYTHONPATH=... python3 -m ...` commands only for diagnosis. If the selected launcher fails, retry the next launcher before treating the tool as unavailable.

3. Run memory readiness:

```bash
4dt-memory doctor --workspace . --json
```

If memory is not initialized and the current folder is already a confirmed 4DreamTeam workspace, run:

```bash
4dt-memory init --workspace . --json
```

`init` creates SQLite storage and seeds missing baseline contract keys only; it must not overwrite existing operator/project contract values. In an unconfirmed or empty workspace, ask before initialization.

4. If memory is `ready`, immediately load default project rules, operator preferences, active modes, and workflow constraints from contract memory:

```bash
4dt-memory defaults load --workspace . --json
```

If defaults load as `ready`, apply them without asking the operator to repeat context. If defaults are incomplete or invalid, run `4dt-memory onboarding questions --workspace . --json` and ask only the returned repair or setup questions before treating a mode or rule as active. If memory is degraded, unavailable, empty, or low-signal, report that state and continue from current workspace instructions. Do not invent remembered rules.

After contract defaults are applied, run Wakeup Recall for Wake Context before proposing work. Search memory for pending startup instructions, one-time operator messages, and the latest session handoff; fetch exact records that may change the next action, deliver operator-facing one-time messages, and immediately retire entries whose metadata or content says they must be deleted after delivery. Use Wake Context as compressed continuation context and pointers, then verify facts against board, wiki, sources, or current user input before changing behavior.

Rule: do not dump all memory into context. Outside Wakeup Recall, use bounded supplemental recall only when route, role, continuation state, or the operator's request makes prior lessons relevant. Build a role/task-enriched English `4dt-search query` over explicit domains, read concise previews first, and fetch exact memory records only when they may change the plan.

5. Run the four startup checks:

```bash
4dt-board --workspace . --json validate
4dt-sources --workspace . --json registry validate
4dt-wiki --workspace . --json validate
4dt-memory doctor --workspace . --json
```

6. Report one status line for each tool: `4dt-board`, `4dt-sources`, `4dt-wiki`, and `4dt-memory`.
7. Name the workspace state: `no_workspace`, `uninitialized`, `partially_initialized`, `degraded_tooling`, or `ready`.
8. Offer situation-aware next actions for the operator to choose from.

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
- board artifacts through `4dt-board`;
- wiki artifacts through `4dt-wiki`;
- source registry through `4dt-sources`;
- memory storage through `4dt-memory`.

Do not create a local installed-skill copy in a normal workspace; the installed package is `4dreamteam/`.

## Source Boundary

Workspace `sources/` is readable by default.

All external source paths must be registered explicitly through `4dt-sources registry add --operator-approved`. The registry list is the single source of truth for approved external source access.
