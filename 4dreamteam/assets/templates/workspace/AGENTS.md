# 4DreamTeam Workspace Rules

## Purpose

This folder is a working `4DreamTeam workspace`.

It stores product briefs, tasks, reports, and knowledge bases. Production code usually lives in external approved source paths.

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

## Source Access

Read external source code only as explicitly approved sources.

An approved source is a hard boundary: do not read parent directories, sibling directories, inferred project roots, or neighboring projects without separate approval.

Do not read secrets, `.env`, credentials, private keys, dumps, or unrelated user files.

DevOps SSH keys are looked up only in `keys/` at the workspace root. Do not print key contents and do not copy them into documentation, tasks, or reports.

## Confirmation Policy

Before changing files, explain what will be changed and wait for user approval unless there is explicit `auto` mode or direct confirmation.

For wiki bootstrap, first show the intake summary and wait for confirmation.

## Workspace Self-Update

When the user asks to update this workspace to the currently installed 4DreamTeam skill version, replace only this root `AGENTS.md` from the installed skill template `assets/templates/workspace/AGENTS.md`.

Do not change `docs/`, `tasks/`, `reports/`, `keys/`, approved source repositories, or installed skill files during workspace self-update.

After replacing `AGENTS.md`, ask the user to restart Codex so the updated skill and workspace instructions are loaded in a clean session.

## Safety

Do not run destructive commands without explicit approval.

Do not expose secrets in tasks, reports, documentation, or responses.

Do not perform unrelated refactoring.
