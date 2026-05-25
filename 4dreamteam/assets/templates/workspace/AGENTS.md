# 4DreamTeam Workspace Rules

## Purpose

This folder is a working `4DreamTeam workspace`.

It is a local working area for project work, source materials, decisions, tasks, wiki knowledge, memory, and role coordination.

## Main Entrypoint

All working requests are routed through `$4DreamTeam`.

If a request concerns a business request, product development, a task, implementation, acceptance, wiki, a knowledge base, or continuing existing work, use the `$4DreamTeam` framework.

## Startup Orientation

This file is the workspace-level operating contract. At the start of a new session, do not infer project identity from folder names alone. Discover the concrete workspace state through managed tools before choosing a route.

Run:

1. `4dt-memory doctor --workspace . --json`
2. `4dt-memory defaults load --workspace . --json` when memory is ready
3. Wakeup Recall for Wake Context: search memory for pending startup instructions, one-time operator messages, and the latest session handoff; read exact records before acting; deliver one-time messages; retire delivered records that say they should be deleted after delivery
4. `4dt-board --workspace . --json validate`
5. `4dt-sources --workspace . --json registry validate`
6. `4dt-wiki --workspace . --json validate`
7. `4dt-memory doctor --workspace . --json`

Use the results to identify project purpose, source boundaries, current mode, operator preferences, approval policy, git policy, and validation expectations. If memory is unavailable, degraded, or empty, do not invent remembered rules; continue from this file and report that memory defaults were unavailable.

Use Wake Context as compressed continuation context: it may point to board tasks, wiki pages, source files, commands, decisions, and next actions. It does not override current user requests, workspace instructions, tool-managed artifacts, or approved source truth.

## Tool Launch Contract

For startup checks, prefer the installed 4DreamTeam skill wrappers as the default launcher. Resolve the installed skill package from the active skill path or `$CODEX_HOME/skills/4dreamteam`; do not hardcode user-specific home directories, and do not probe global `4dt-*` commands first.

```bash
python3 <installed-4dreamteam-skill>/scripts/4dt-memory.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-search.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-board.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-sources.py <args>
python3 <installed-4dreamteam-skill>/scripts/4dt-wiki.py <args>
```

From the 4DreamTeam source checkout, prefer the matching npm scripts when intentionally working on the source repository. Treat console `4dt-*` commands as optional shortcuts only after they are known to work in the current shell. Use direct `PYTHONPATH=... python3 -m ...` module fallbacks only for diagnosis after wrappers and source scripts fail.

## Framework-First Rule

Do not bypass the `$4DreamTeam` process with ad-hoc work when the request can be handled through the framework.

## Script-Managed Artifacts

Agents do not read or write managed board storage directly. Use `4dt-board` for board status, task lookup, section reads, creation, movement, metadata updates, timeline comments, validation, and repair.

Agents do not read or write managed wiki storage directly. Use `4dt-wiki` for wiki pages and `4dt-sources` for source registry and approved-source inventory.

Storage layout is an implementation detail owned by the tools. The scripts are the only supported mutation and query interface for agents.

Allowed workspace artifacts:

- `AGENTS.md` as the workspace rule entrypoint
- tool-managed board, wiki, source registry, memory, cache, and runtime state
- `sources/` as the local source staging area
- `keys/` as the local DevOps key lookup area when infrastructure work requires it

## Role Board

The board is role-based and is managed only through `4dt-board`.

Supported columns:

- `backlog`
- `analytic`
- `developer`
- `quality`
- `wiki`
- `release`
- `released`
- `done`
- `rejected`

A task's current column determines which role owns the next action. `next_owner` is not used.

## Timeline Model

Tasks are living timelines. Product description, analytic questions, developer reports, quality decisions, wiki notes, release notes, and lead handoffs are appended as timeline entries through `4dt-board comment add`.

Agents do not rewrite another role's comment. They append their own role-scoped timeline entry with a fixed `roleName_actionName` type.

## Internal Artifact Policy

Internal tasks, briefs, timeline entries, release plans, and managed wiki pages are written in English for agents. `$4DreamTeam` lead summarizes results to the user in the user's language.

## Operator And Framework User

The `framework user` owns product meaning: goals, audience, value, scope, priorities, roadmap intent, and product acceptance intent.

The `operator` is the above-workflow 4DreamTeam role that controls execution permission in the current session: external source access, role transitions, auto mode, file writes, git actions, infrastructure actions, publication, and other safety gates.

The operator role is currently human-led and still forming. Future agentic operator behavior is experimental and must be opt-in, scoped, auditable, and quality-reviewed before use.

## Source Access

`sources/` is the workspace-local source staging area. It may contain source copies, exports, screenshots, extracted materials, or links to external projects and file collections.

The `sources/` folder and all descendants are readable by default for this workspace.

All other source boundaries must be added explicitly through `4dt-sources registry add --operator-approved`. The registry list is the single source of truth for approved external sources: if a path is listed, it is approved; if it is removed, it is no longer approved.

An approved source is a hard boundary: do not read parent directories, sibling directories, inferred project roots, or neighboring projects without separate approval.

Do not read secrets, `.env`, credentials, private keys, dumps, or unrelated user files.

DevOps SSH keys are looked up only in `keys/` at the workspace root. Do not print key contents and do not copy them into documentation, tasks, timeline entries, or reports.

## Discovery And Search

Before broad reading, use `4dt-search query` with explicit domains.

Use the smallest useful query first:

- `4dt-search query "<question>" --workspace . --domain wiki --json`
- `4dt-search query "<question>" --workspace . --domain sources --json`
- `4dt-search query "<question>" --workspace . --domain board --json`
- `4dt-search query "<question>" --workspace . --domain memory --json`

Prefer `wiki` first for project knowledge, `sources` for implementation/source truth, `board` for task status and timeline evidence, and `memory` for durable decisions, operator preferences, and prior-session context.

Preserve exact ids, command names, filenames, paths, and technical terms in search queries. Translate vague operator intent into concise English search terms when useful.

Use `--match any` for exploratory or fuzzy queries. Use `--match all` only when all terms must be present. If `--index readonly` reports a stale index, report it and use the appropriate managed validation or rebuild flow before trusting missing results.

After discovery, use each result's `getCommand` or the domain tool for exact reads. Do not replace exact reads with broad filesystem inspection.

## Confirmation Policy

Before changing files, explain what will be changed and wait for user approval unless there is explicit `auto` mode or direct confirmation.

For wiki bootstrap, first show the intake summary and wait for confirmation. Source registry changes for paths outside workspace `sources/` require explicit operator approval.

## Workspace Self-Update

When the user asks to update this workspace to the currently installed 4DreamTeam skill version, replace only this root `AGENTS.md` from the installed skill template `assets/templates/workspace/AGENTS.md`.

Do not change tool-managed storage, `keys/`, approved source repositories, or installed skill files during workspace self-update.

Before replacing `AGENTS.md`, show a concise change summary or diff and wait for explicit approval.

After replacing `AGENTS.md`, report the source template, target path, and installed skill version, then ask the user to restart Codex so the updated skill and workspace instructions are loaded in a clean session.

## Safety

Do not run destructive commands without explicit approval.

Do not expose secrets in tasks, timeline entries, reports, documentation, or responses.

Do not perform unrelated refactoring.
