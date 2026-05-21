# Lead Preflight

Use this file before writing files in a 4DreamTeam workspace.

## Workspace Preflight

The global `$4DreamTeam` skill is available from any chat, but full framework work expects a 4DreamTeam workspace.

Do not require a `skill/` or `4dreamteam/` folder in a working workspace after the skill is installed. The `4dreamteam/` folder exists in the skill source repository, where `SKILL.md`, `references/`, `assets/`, and `agents/` live.

A normal 4DreamTeam workspace after skill installation is a git repository overlay for coordinating work across current projects, file dumps, images, exported documents, and other source materials. It contains:

- `AGENTS.md`
- `docs/index.md`
- `tasks/`
- `reports/`
- `sources/.gitignore`

`sources/` is the workspace-local source staging area. Do not list, stat, resolve symlinks, inventory, index, or read anything inside `sources/` during preflight or initialization. The first workflow that needs source access must ask the operator to personally inspect `sources/` and confirm either that all current contents may be used or that access is denied/absent.

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
sources/.gitignore
```

Create `AGENTS.md` from the bundled template:

```txt
assets/templates/workspace/AGENTS.md
```

Create `docs/index.md` from the bundled template:

```txt
assets/templates/wiki/docs-index.md
```

Create `sources/.gitignore` from the bundled template:

```txt
assets/templates/workspace/sources.gitignore
```

If `sources/` already exists but `sources/.gitignore` is missing, initialization or validation may create only `sources/.gitignore` from the template. This repair does not count as first-touch source access and must not list, stat, resolve, inventory, index, or read any other `sources/` contents.

Do not create `skill/`, `skills/`, `4dreamteam/`, `references/`, or `assets/` inside a working workspace. Those resources are already provided by the installed skill.

If the current folder does not look like a 4DreamTeam workspace:

1. Do not create files immediately.
2. Explain that the framework can work here only after explicit confirmation.
3. Ask whether to use the current folder as a 4DreamTeam workspace or open an existing workspace folder.
4. If the user chooses the current empty folder, show the file and directory list from the minimum structure above and wait for confirmation before creating it.

If the user explicitly wants to run `wiki bootstrap` in the current folder, continue after the bootstrap intake gate from `references/wiki.md` and `references/wiki/bootstrap.md`.
