# Lead Preflight

Use this file before writing files in a 4DreamTeam workspace.

## Workspace Preflight

The global `$4DreamTeam` skill is available from any chat, but full framework work expects a 4DreamTeam workspace.

Do not require a `skill/` or `4dreamteam/` folder in a working workspace after the skill is installed. The `4dreamteam/` folder exists in the skill source repository, where `SKILL.md`, `references/`, `assets/`, and `agents/` live.

A normal 4DreamTeam workspace after skill installation contains:

- `AGENTS.md`
- `docs/index.md`
- `tasks/`
- `reports/`

Create `README.md` in a working workspace only if the user asks for user-facing instructions for that folder.

Minimum structure that may be created in an empty folder after explicit user confirmation:

```txt
AGENTS.md
docs/index.md
tasks/backlog/.gitkeep
tasks/analytic/.gitkeep
tasks/developer/.gitkeep
tasks/quality/.gitkeep
tasks/wiki/.gitkeep
tasks/release/.gitkeep
tasks/released/.gitkeep
tasks/done/.gitkeep
tasks/rejected/.gitkeep
reports/product/.gitkeep
reports/product/accepted/.gitkeep
reports/product/rejected/.gitkeep
reports/tasks/.gitkeep
reports/quality/accepted/.gitkeep
reports/quality/rejected/.gitkeep
reports/release/.gitkeep
```

Create `AGENTS.md` from the bundled template:

```txt
assets/templates/workspace/AGENTS.md
```

Create `docs/index.md` from the bundled template:

```txt
assets/templates/wiki/docs-index.md
```

Do not create `skill/`, `skills/`, `4dreamteam/`, `references/`, or `assets/` inside a working workspace. Those resources are already provided by the installed skill.

If the current folder does not look like a 4DreamTeam workspace:

1. Do not create files immediately.
2. Explain that the framework can work here only after explicit confirmation.
3. Ask whether to use the current folder as a 4DreamTeam workspace or open an existing workspace folder.
4. If the user chooses the current empty folder, show the file and directory list from the minimum structure above and wait for confirmation before creating it.

If the user explicitly wants to run `wiki bootstrap` in the current folder, continue after the bootstrap intake gate from `references/wiki.md` and `references/wiki/bootstrap.md`.
