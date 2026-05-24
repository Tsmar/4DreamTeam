# 4DreamTeam

Languages: [English](README.md) | [Russian](README.ru.md)

4DreamTeam is a magic wand for people who want to work on real projects with AI superpowers, without turning every project into one endless fragile chat.

Tell Codex what you want to build, fix, check, document, or ship. 4DreamTeam turns that request into a small working team: product thinks about the goal, analytic shapes the task, developer changes the code, quality checks the result, wiki keeps the project memory, and release helps you ship safely.

You bring the idea, the mess, the half-finished feature, or the "is this actually done?" feeling. 4DreamTeam gives the work a path, writes down what happened, keeps the documentation alive, and asks before dangerous actions.

## Try It When

- You have an idea, but not a spec.
- You opened an old project and forgot what was next.
- You want Codex to change code, but also want a second pass that checks whether the work is really done.
- Your docs are stale and nobody trusts them anymore.
- You are close to release and want a clean plan before touching git.
- You want AI help that feels less like a single overworked chat and more like a careful project team.

## The Simple Promise

```txt
idea -> plan -> implementation -> quality -> wiki -> release
```

4DreamTeam does not try to make you memorize a process. You start with:

```txt
$4DreamTeam
```

The lead role routes the work to the right role and keeps the next step visible.

## Why It Feels Different

### It gives Codex a project brain

Work does not live only in the chat scroll. 4DreamTeam stores tasks, decisions, reports, quality results, docs, and release plans in the workspace so the project can be resumed later.

### It separates doing from checking

The developer role implements scoped work. The quality role independently accepts or rejects it against the task. That makes "done" less vibes-based.

### It keeps docs close to reality

The wiki role maintains a source-backed project knowledge base. Detailed documentation can be exported into `docs/` with `4dt-wiki export`, so the README can stay simple while the project docs stay useful.

### It keeps you in control

4DreamTeam asks before risky transitions, file writes, release steps, infrastructure changes, destructive commands, commits, pushes, tags, and publication. You can work fast without handing over the steering wheel.

## Real Situations

### "I have an idea, not a spec."

```txt
I want a booking system for a small yoga studio.
Right now everything is handled in WhatsApp and changes get lost.
```

4DreamTeam turns the idea into users, goals, scope, non-goals, task candidates, and acceptance criteria before Codex jumps into code.

### "I came back after a week."

```txt
Continue the project. What is next?
```

4DreamTeam reads the board, timeline evidence, wiki, and memory when available, then tells you the next safe action.

### "I need to know if this is really done."

```txt
This feature is implemented, but I am not sure it is actually finished.
```

4DreamTeam routes to quality, checks the work against acceptance criteria, and records an accepted or rejected result.

### "The docs are probably stale."

```txt
The app changed, but the docs are probably wrong.
```

4DreamTeam can audit, sync, deepen, and export source-backed docs without reading unrelated files or inventing missing facts.

### "I need to ship without making a mess."

```txt
Prepare the accepted work for release.
```

4DreamTeam checks accepted evidence, reviews changed files, updates release documentation when needed, and proposes an exact plan before any git action.

## What You Get

- Product shaping for raw ideas.
- Technical task planning before implementation.
- Developer work with visible evidence.
- Independent quality review.
- A source-backed project wiki.
- Exported documentation in `docs/`.
- README positioning, launch copy, release narratives, and claim audits.
- DevOps notes and runbooks with safety gates.
- Release plans and changelog preparation after explicit approval.
- A way to improve 4DreamTeam itself through the same controlled workflow.

## Quick Start

Install the `4dreamteam/` skill package from [Tsmar/4DreamTeam](https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam).

Restart Codex, then ask:

```txt
Is the 4DreamTeam skill available?
```

From any project folder:

```txt
Run $4DreamTeam.
```

If the folder is not yet a 4DreamTeam workspace, 4DreamTeam asks before creating workspace files.

### Working With An Existing Project

You do not need a complicated setup. Create a clean folder for the 4DreamTeam workspace, put your project repository inside `sources/`, then run `$4DreamTeam`.

```txt
my-4dt-workspace/
  sources/
    your-project/
```

After initialization, 4DreamTeam can build the project knowledge base from the approved source folder and you are ready to work: ask it to understand the project, plan changes, check work, update docs, or prepare an accepted release.

## Useful Prompts

```txt
$4DreamTeam status
$4DreamTeam continue
$4DreamTeam validate workspace
$4DreamTeam turn this idea into a plan
$4DreamTeam check whether this feature is really done
$4DreamTeam update the project docs from source
$4DreamTeam prepare this accepted work for release
```

Read-only status and validation are safe by default. Release staging, commits, pushes, tags, deployments, migrations, and destructive actions require explicit approval.

## Documentation

This README is the landing page. It explains why you might want to try 4DreamTeam.

Detailed documentation lives in [docs/](docs/) and is exported from the managed 4DreamTeam wiki:

- [Workspace Overview](docs/overview.md)
- [Product Overview](docs/product/overview.md)
- [Task Lifecycle Flow](docs/flows/task-lifecycle.md)
- [Wiki Workflow](docs/flows/wiki-workflow.md)
- [Workspace Tools Contract](docs/contracts/workspace-tools.md)
- [Source Boundaries Domain](docs/domains/source-boundaries.md)

## Safety In Plain English

4DreamTeam is designed to be useful without being reckless:

- it does not skip quality review for implementation work;
- it treats approved source paths as hard boundaries;
- it does not expose `.env` files, secrets, credentials, or private keys;
- it asks before risky file writes, infrastructure changes, release actions, and publication;
- it does not invent marketing, DevOps, or security claims that are not backed by confirmed sources.

## Status

Current documented version: `0.5.0`.

See [CHANGELOG.md](CHANGELOG.md) for release history.
