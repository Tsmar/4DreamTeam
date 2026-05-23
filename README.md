# 4DreamTeam

Languages: [English](README.md) | [Russian](README.ru.md)

4DreamTeam is a Codex skill for turning rough ideas, half-finished work, stale documentation, and release pressure into a traceable workflow.

Instead of asking one AI agent to keep everything in one long chat, 4DreamTeam gives Codex a small team of roles: product, analytic, developer, quality, wiki, marketing, devops, and release. An operator sits above the workflow and controls source access, role-transition gates, auto mode, file writes, git, infrastructure, and publication. Work becomes visible in files: epics, tasks, developer reports, quality reports, source-backed docs, release plans, and epic handoffs.

The result is not ceremony. It is continuity: you can come back later, see what happened, understand what is accepted, and decide the next safe step.

## The Promise

```txt
idea -> epic -> task -> implementation -> quality review -> documentation -> release
```

Use the main entrypoint:

```txt
$4DreamTeam
```

You do not need to remember role names. The lead role routes the request.

## Real Situations

### You Have An Idea, Not A Spec

```txt
I want a booking system for a small yoga studio.
Right now everything is handled in WhatsApp and changes get lost.
```

4DreamTeam turns the messy idea into an epic with users, scope, non-goals, task candidates, and acceptance criteria before Codex jumps into code.

### You Came Back A Week Later

```txt
Continue the project. What is next?
```

4DreamTeam reads the role board, reports, wiki, and optional memory, then recommends the next safe action instead of pretending the previous chat context still exists.

### You Need To Know If Work Is Really Done

```txt
This feature is implemented, but I am not sure it is actually finished.
```

4DreamTeam routes to `quality`, checks the result against acceptance criteria, and records an accepted or rejected quality report.

### The Docs Are Probably Stale

```txt
The app changed, but the docs are probably wrong.
```

4DreamTeam can audit or sync a source-backed wiki from approved source paths without reading unrelated files or inventing missing facts.

### You Need To Ship Safely

```txt
Prepare the accepted work for release.
```

4DreamTeam checks accepted evidence, reviews dirty files, updates changelogs when appropriate, and proposes an exact staging plan before any git commit.

## What It Does

- Turns raw product intent into scoped epics and task candidates.
- Converts approved work into implementation-ready technical tasks.
- Implements scoped changes through a developer workflow.
- Runs independent quality review before work is accepted.
- Maintains source-backed project wikis through `4dt-wiki` and source access through `4dt-sources`.
- Uses local 4DT Memory for continuity while keeping current workspace instructions, tool-managed artifacts, and approved sources as the source of truth.
- Prepares README positioning, launch copy, release narratives, and claim audits from confirmed sources.
- Documents infrastructure facts and runbooks with DevOps safety gates.
- Packages accepted work into changelog entries and commit plans after explicit approval.
- Improves 4DreamTeam itself through the same controlled workflow.

## Roles

| Role | Job |
|---|---|
| `product` | Clarifies users, goals, scope, non-goals, and product acceptance. |
| `analytic` | Turns intent into implementation-ready tasks with risks and checks. |
| `developer` | Implements approved tasks and records developer evidence. |
| `quality` | Independently accepts or rejects work against criteria. |
| `wiki` | Builds and maintains source-backed project knowledge bases. |
| `marketing` | Creates source-backed public messaging and claim reviews. |
| `devops` | Documents servers, deployments, diagnostics, and operational facts. |
| `release` | Prepares changelogs, commit plans, and approved git commits. |

## Why Files Matter

4DreamTeam stores state in the workspace through its tools.

That means:

- decisions and assumptions survive beyond one chat;
- tasks can be resumed without guessing;
- developer work and quality review are separate;
- a workspace is a local working area for 4DreamTeam coordination;
- `sources/` stages source materials and is readable by default inside the workspace;
- rejected work has a clear correction path;
- project knowledge lives in Markdown;
- completed epics leave handoff notes for the next session, next agent, or next epic;
- release plans show what will be staged before approved git changes happen when release packaging is requested.

## Quick Start

Open a new chat and write: install the skill from [Tsmar/4DreamTeam](https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam).

Restart Codex, then check that the skill is available:

```txt
Is the 4DreamTeam skill available?
```

From any folder:

```txt
Run $4DreamTeam.
```

If the folder is empty or not yet a 4DreamTeam workspace, the skill asks before creating workspace files.

## Common Commands

```txt
$4DreamTeam init workspace
$4DreamTeam status
$4DreamTeam continue
$4DreamTeam validate workspace
$4DreamTeam connect project <project-name> from <source-path>
$4DreamTeam check docs for <project-name>
$4DreamTeam search docs for <project-name> <query>
$4DreamTeam prepare release for <project-name>
$4DreamTeam improve 4DreamTeam itself from your local checkout of https://github.com/Tsmar/4DreamTeam, for example /Users/Tsmar/Projects/4DreamTeam
```

`status`, `continue`, and `validate workspace` are read-only by default. Release staging, commits, pushes, tags, deployments, migrations, and destructive actions require explicit approval.

## Documentation

Detailed documentation lives in [docs/](docs/):

- [Examples](docs/examples.md) - realistic end-to-end situations.
- [Workflows](docs/workflows.md) - product, task, quality, wiki, release, DevOps, marketing, and self-improvement flows.
- [Workspace](docs/workspace.md) - workspace tool contract, role board, and safety gates.
- [Wiki Index](docs/wiki-index.md) - wiki and source search tooling.
- [4DT Memory](docs/memory.md) - local memory storage, recall, safety, degraded mode, and benchmark behavior.
- [Development](docs/development.md) - repository structure and contribution notes.

## Safety Guarantees

4DreamTeam is conservative by design:

- it does not bypass the framework workflow when a 4DreamTeam route applies;
- it does not skip independent quality review for implementation work;
- it treats approved source paths as hard boundaries;
- it treats confirmed workspace `sources/` descendants as hard boundaries only after operator first-touch confirmation;
- it asks the operator before scoped auto-mode transitions such as `lead -> product`, `product -> analytic`, `analytic -> developer`, and `quality -> wiki`;
- it does not expose secrets, credentials, `.env` contents, or private keys;
- it does not run destructive, infrastructure, release, or publication actions without explicit approval;
- it does not invent marketing or DevOps claims that are not backed by confirmed sources.

## Status

Current documented version: `0.2.0`.

See [CHANGELOG.md](CHANGELOG.md) for release history.
