# Workspace

4DreamTeam uses files as its shared memory and handoff layer.

## Workspace Shape

A normal 4DreamTeam workspace does not contain the skill source. After initialization, it contains:

```txt
AGENTS.md
docs/index.md
tasks/
  backlog/
  analytic/
  developer/
  quality/
  wiki/
  release/
  released/
  done/
  rejected/
reports/
  product/
  tasks/
  quality/
  release/
```

`tasks/` is a role-based virtual Kanban board. Epics live in `tasks/backlog/`; executable work is always represented as `TASK-XXXX` files in the role column that owns the next action.

`tasks/release/` is the active release queue, and `tasks/released/` contains tasks included in pushed releases.

## Project Documentation

Project documentation lives under:

```txt
docs/<project-name>/
```

DevOps documentation for a project lives under:

```txt
docs/<project-name>/devops/
  servers/
  runbooks/
```

`runbooks/` is used only when the task explicitly asks to save a runbook.

## Workspace Self-Update

Use this after installing or updating the 4DreamTeam skill and before continuing work in an existing workspace:

```txt
Run $4DreamTeam self-update workspace.
```

Self-update is intentionally narrow. It replaces only the workspace root `AGENTS.md` from the installed skill template:

```txt
assets/templates/workspace/AGENTS.md
```

It must not change `docs/`, `tasks/`, `reports/`, `keys/`, approved source repositories, or installed skill files.

After replacing `AGENTS.md`, restart Codex so the updated skill and workspace instructions are loaded in a clean session. After restart, run `$4DreamTeam validate workspace` if you want to verify the workspace.

## Safety Gates

4DreamTeam is built around conservative operating rules:

- do not write files until workspace preflight passes or the user confirms the workspace;
- do not bypass the workflow when a 4DreamTeam route applies;
- do not skip independent quality review for implementation work;
- do not update wiki post-acceptance docs before accepted quality exists;
- do not read outside approved source paths;
- do not expose secrets in tasks, reports, docs, or chat;
- do not run migrations or destructive commands without explicit approval;
- document verified facts only for DevOps;
- do not invent marketing claims that are not backed by approved sources.
