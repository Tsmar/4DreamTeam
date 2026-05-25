# 4DreamTeam

Languages: [English](README.md) | [Russian](README.ru.md)

4DreamTeam is a magic wand for people who want to work on real projects with AI superpowers, without turning every project into one endless fragile chat.

Tell Codex what you want to build, fix, check, document, or ship. 4DreamTeam turns that request into a small working team: one part clarifies the goal, another plans the work, another changes the code, another checks the result, another keeps the project notes fresh, and another helps you release safely.

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
idea -> plan -> build -> check -> docs -> release
```

4DreamTeam does not try to make you memorize a process. You start with:

```txt
$4DreamTeam
```

4DreamTeam routes the work and keeps the next step visible.

## Why It Feels Different

### It gives Codex a project brain

Work does not live only in the chat scroll. 4DreamTeam writes down what was decided, what was changed, what was checked, and what still matters so the project can be resumed later.

People wake up each morning with yesterday's noise softened and the important things still within reach: who they are, what matters, and where to continue. 4DreamTeam treats agent sessions the same way. When a chat ends, the useful context can settle into memory, board notes, and wiki pointers; when a new chat starts, Wake Context helps the agent wake up with the next step in mind instead of dragging the whole tired conversation behind it.

### It learns from the operator

When you point out something important, 4DreamTeam can turn it into a lesson for next time. If you say that tests work a certain way, that some logs are just noise, or that a mistake should not be repeated, the agent can remember the lesson and bring it back before similar work.

### It separates doing from checking

The same assistant does not simply change something and declare victory. 4DreamTeam makes a separate check against the original goal, so "done" is based on evidence instead of vibes.

### It keeps docs close to reality

Project notes stay close to the real work. 4DreamTeam can refresh detailed documentation from the project knowledge base, so the README can stay simple while the deeper docs stay useful.

### It keeps you in control

4DreamTeam asks before risky changes, commits, releases, server work, or publication. You can move quickly without handing over the steering wheel.

## Real Situations

### "I have an idea, not a spec."

```txt
I want a booking system for a small yoga studio.
Right now everything is handled in WhatsApp and changes get lost.
```

4DreamTeam helps turn the idea into a clear goal, a first plan, and a simple way to tell whether the work is actually finished before Codex jumps into code.

### "I came back after a week."

```txt
Continue the project. What is next?
```

4DreamTeam checks the saved project state and tells you the next safe action.

### "I need to know if this is really done."

```txt
This feature is implemented, but I am not sure it is actually finished.
```

4DreamTeam checks the work against the original goal and records whether it passed or needs another round.

### "The docs are probably stale."

```txt
The app changed, but the docs are probably wrong.
```

4DreamTeam can compare the docs with the real project, update what changed, and avoid guessing about things it has not checked.

### "I need to ship without making a mess."

```txt
Prepare the accepted work for release.
```

4DreamTeam reviews what changed, updates the release description when needed, and proposes an exact plan before touching git.

## What You Get

- Help turning raw ideas into clear work.
- A plan before code changes begin.
- Code changes with visible notes about what happened.
- A separate check before work is called done.
- Project notes that stay connected to the real source.
- Operator-guided memory for lessons, preferences, project habits, and mistakes to avoid.
- Documentation you can export into `docs/`.
- README help, launch text, release descriptions, and promise checks.
- Server notes and operating instructions with safety checks.
- A release plan and change list after your approval.
- A way to improve 4DreamTeam itself through the same careful process.

## Quick Start

Ask Codex to install the `4dreamteam/` skill package directly from the repository:

```txt
установи скилл расположенный по этой ссылке [https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam](https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam)
```

Restart Codex, then ask:

```txt
Is the 4DreamTeam skill available?
```

From a new project workspace, start the skill:

```txt
привет $4DreamTeam
```

If the folder is not ready for 4DreamTeam yet, it asks before creating project files.

### Working With An Existing Project

You do not need a complicated setup. Create a clean working folder, put your project repository inside `sources/`, then run `$4DreamTeam`.

```txt
my-4dt-workspace/
  sources/
    your-project/
```

After setup, 4DreamTeam can learn the approved project folder and you are ready to work: ask it to understand the project, plan changes, check work, update docs, or prepare a release.

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

Status checks are safe by default. Commits, pushes, tags, releases, server changes, database changes, and actions that delete data require your clear approval.

## Documentation

Documentation is available in [docs/](docs/) in English:

- [Workspace Overview](docs/overview.md)
- [Product Overview](docs/product/overview.md)
- [Task Lifecycle Flow](docs/flows/task-lifecycle.md)
- [Wiki Workflow](docs/flows/wiki-workflow.md)
- [Workspace Tools Contract](docs/contracts/workspace-tools.md)
- [Memory Domain](docs/domains/memory.md)
- [Memory Human Analogy](docs/domains/memory-human-analogy.md)
- [Source Boundaries Domain](docs/domains/source-boundaries.md)

## Safety In Plain English

4DreamTeam is designed to be useful without being reckless:

- it does not skip the separate check before calling work done;
- it only reads project folders that you have approved;
- it does not expose `.env` files, secrets, credentials, or private keys;
- it asks before risky file changes, server work, releases, and publication;
- it does not invent marketing, operations, or security claims that are not backed by checked sources.

## Thanks

I am grateful to my colleagues and friends for their belief in 4DreamTeam, for entrusting their projects to a team of agents who work with them on real tasks. It is incredibly inspiring and motivates me to keep developing this project!

## Status

Current documented version: `0.5.3`.

See [CHANGELOG.md](CHANGELOG.md) for release history.
