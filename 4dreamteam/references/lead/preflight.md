# Workspace Preflight

Use this file before writing files in a workspace.

## Existing Workspace

A current workspace should have:

- `AGENTS.md`;
- script-managed board storage reachable through `4dt-board`;
- script-managed wiki storage reachable through `4dt-wiki`;
- source registry reachable through `4dt-sources`;
- workspace-local memory reachable through `4dt-memory`;
- git-ignored `sources/`.

Run:

```bash
4dt-board validate
4dt-wiki validate
4dt-sources registry validate
4dt-memory doctor
```

If a tool reports incompatible or unreadable artifacts, stop and report the issue before proceeding.

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
