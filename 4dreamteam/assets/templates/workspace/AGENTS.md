# 4DreamTeam Workspace Rules

## Purpose

This folder is a working `4DreamTeam workspace`.

It is a git repository overlay above current projects, file dumps, images, exported documents, and other source materials.

It stores epics, tasks, reports, knowledge bases, and the local `sources/` source staging boundary.

## Main Entrypoint

All working requests are routed through `$4DreamTeam`.

If a request concerns a business request, product development, a task, implementation, acceptance, wiki, a knowledge base, or continuing existing work, use the `$4DreamTeam` framework.

## Framework-First Rule

Do not bypass the `$4DreamTeam` process with ad-hoc work when the request can be handled through the framework.

## Workspace Artifacts

Allowed working artifacts:

- `tasks/`
- `reports/`
- `docs/index.md`
- `docs/<project-name>/`
- `docs/<project-name>/devops/servers/`
- `docs/<project-name>/devops/runbooks/` only when a runbook is explicitly requested
- `sources/` as a git-ignored local source staging area

## Role Board

`tasks/` is a virtual Kanban board by role. A task file lives in the folder of the role that owns the next action:

- `tasks/backlog/` - epics, product backlog, discovery, and grouped task planning
- `tasks/analytic/` - needs technical analysis
- `tasks/developer/` - ready for implementation or developer rework
- `tasks/quality/` - ready for independent quality
- `tasks/wiki/` - accepted work needing documentation
- `tasks/release/` - accepted work selected for release packaging
- `tasks/released/` - work included in a pushed release
- `tasks/done/` - closed with no active next role
- `tasks/rejected/` - rejected work awaiting decision or correction

## Internal Artifact Policy

Internal tasks, briefs, reports, release plans, and managed wiki pages are written in English for agents. `$4DreamTeam` lead summarizes results to the user in the user's language.

## Operator And Framework User

The `framework user` owns product meaning: goals, audience, value, scope, priorities, roadmap intent, and product acceptance intent.

The `operator` is the above-workflow 4DreamTeam role that controls execution permission in the current session: source access, role transitions, auto mode, file writes, git actions, infrastructure actions, publication, and other safety gates.

The operator role is currently human-led and still forming. Future agentic operator behavior is experimental and must be opt-in, scoped, auditable, and quality-reviewed before use.

## Source Access

`sources/` is the workspace-local source staging area. It may contain source copies, exports, screenshots, extracted materials, or symlinks to external projects and file collections.

Do not list, stat, resolve symlinks, inventory, index, or read anything inside `sources/` until the operator personally inspects it and confirms either:

1. all current `sources/` contents may be used as workspace-approved sources; or
2. access is denied or no usable sources are present.

`sources/` approval is all-or-nothing for current contents. New files added later require a separate rescan/actualization confirmation. Creating or repairing `sources/.gitignore` is allowed without reading any other `sources/` contents.

After first-touch confirmation, descendants of `sources/` are approved source boundaries for the workspace, subject to ignore and secret-handling rules. Read files outside `sources/` only as explicitly approved external sources.

An approved source is a hard boundary: do not read parent directories, sibling directories, inferred project roots, or neighboring projects without separate approval. Symlinks inside confirmed `sources/` must be resolved before use; record both the workspace alias and resolved target when the source is indexed.

Do not read secrets, `.env`, credentials, private keys, dumps, or unrelated user files.

DevOps SSH keys are looked up only in `keys/` at the workspace root. Do not print key contents and do not copy them into documentation, tasks, or reports.

## Confirmation Policy

Before changing files, explain what will be changed and wait for user approval unless there is explicit `auto` mode or direct confirmation.

For wiki bootstrap, first show the intake summary and wait for confirmation. If `sources/` has not had first-touch confirmation, ask the operator to inspect it before reading source contents.

## Workspace Self-Update

When the user asks to update this workspace to the currently installed 4DreamTeam skill version, replace only this root `AGENTS.md` from the installed skill template `assets/templates/workspace/AGENTS.md`.

Do not change `docs/`, `tasks/`, `reports/`, `keys/`, approved source repositories, or installed skill files during workspace self-update.

Before replacing `AGENTS.md`, show a concise change summary or diff and wait for explicit approval.

After replacing `AGENTS.md`, report the source template, target path, and installed skill version, then ask the user to restart Codex so the updated skill and workspace instructions are loaded in a clean session.

## Safety

Do not run destructive commands without explicit approval.

Do not expose secrets in tasks, reports, documentation, or responses.

Do not perform unrelated refactoring.
