# 4DreamTeam

Languages: [English](README.md) | [Russian](README.ru.md)

4DreamTeam is a Codex skill for people who have ideas and want help turning them into clear, reviewable, finished work.

Instead of asking one AI agent to do everything in one long conversation, 4DreamTeam gives Codex a small team of roles: product, analyst, developer, quality reviewer, wiki maintainer, marketing specialist, DevOps operator, and release manager. The result is a workflow where ideas become briefs, briefs become tasks, tasks become checked work, accepted work becomes clean project history, and important knowledge stays in files instead of disappearing into chat history.

## Why It Exists

Most people do not start with a perfect technical task. They start with something closer to:

```txt
I have an idea.
Can we build this?
What should happen first?
How do I know it is done?
Can this be explained clearly to users?
Can we keep the documentation up to date?
```

4DreamTeam helps Codex slow down just enough to make the work concrete:

- what are we trying to achieve;
- who is it for;
- what is in scope now;
- what can wait;
- what files or systems are affected;
- how the result will be checked;
- what should be documented when it is accepted.

That makes 4DreamTeam useful for a founder, product thinker, operator, developer, or curious builder who wants structure without needing to become a project manager first.

## The Core Promise

4DreamTeam turns an idea into a traceable workflow:

```txt
idea -> product brief -> technical task -> implementation -> quality review -> documentation -> release
```

It can also help with project knowledge bases, infrastructure notes, README positioning, press releases, market-facing materials, and continuing work across sessions.

The main entrypoint is `$4DreamTeam`. You do not need to remember role names; the lead role routes the request.

## Why It Is Called 4DreamTeam In Codex

The skill id is `4dreamteam`, and the product name is 4DreamTeam.

In Codex, the display name is `4DreamTeam` so it is quick to select after typing `$`: on many keyboards, `$` is on the `4` key, so pressing `4` again jumps straight to the skill.

## Who It Is For

4DreamTeam is for:

- people with product ideas who need a clear next step;
- builders who want Codex to avoid jumping straight into code;
- maintainers who want tasks, reports, and docs to survive beyond one chat;
- teams that want acceptance criteria and independent quality before calling work done;
- operators who need careful DevOps notes based on verified facts;
- projects that need README, launch, or product messaging grounded in real capabilities.

It is especially useful when the work matters enough that you want decisions, assumptions, and acceptance to be visible.

## What 4DreamTeam Can Do

4DreamTeam helps Codex:

- turn a raw idea or business request into a product brief;
- decompose a feature into an implementation-ready task;
- implement scoped changes through a developer workflow;
- run an independent quality check before work is accepted;
- create, audit, sync, and deepen project documentation;
- maintain structured source maps and local wiki indexes for faster source navigation;
- summarize and validate a workspace;
- update workspace rules after a skill upgrade;
- improve 4DreamTeam itself through a simplified self-improvement lifecycle;
- package accepted work into changelogs, commit plans, and git commits after explicit approval;
- prepare press releases, README positioning, product messaging, and market-facing analytical materials;
- document servers, deployments, SSH access, diagnostics, migrations, and runbooks with DevOps safety gates.

## The Roles

| Role | What it does |
|---|---|
| `product` | Clarifies what should be built, for whom, why it matters, what is in scope, and how to accept it from a product standpoint. |
| `analytic` | Converts product briefs or direct requests into technical tasks with affected areas, requirements, risks, and checkable acceptance criteria. |
| `developer` | Implements approved tasks, updates tests when needed, runs checks, and writes implementation reports. |
| `quality` | Independently verifies implementation and documentation work against acceptance criteria. |
| `wiki` | Creates and maintains source-backed project knowledge bases. |
| `marketing` | Turns confirmed product value into press releases, README positioning, product messaging, launch materials, and market-facing analysis. |
| `devops` | Handles infrastructure documentation, server cards, deployment diagnostics, SSH access rules, and operational runbooks. |
| `release` | Packages accepted work into workspace/source changelog entries, a commit plan, and a git commit after explicit approval. |

## A Typical Journey

Start with an idea:

```txt
Run $4DreamTeam.

Goal:
I want to build a lightweight booking system for a small studio.

Context:
The owner takes reservations manually and loses track of changes.
```

4DreamTeam can turn that into:

1. a product brief with users, scope, scenarios, and acceptance criteria;
2. a technical task with implementation requirements;
3. code changes and a developer report;
4. an independent quality report;
5. documentation updates if the accepted behavior changes the project;
6. release packaging with changelog entries and a commit plan when the work should be committed.

In controlled mode, 4DreamTeam stops at important gates so the user can approve the next step.

## Why Files Matter

4DreamTeam intentionally stores workflow state in files:

```txt
tasks/
reports/
docs/
```

This gives you:

- product briefs you can review before implementation;
- technical tasks that can be resumed later;
- developer reports separate from quality reports;
- rejected work with clear correction paths;
- project knowledge in Markdown;
- DevOps facts documented only after verification.
- release plans that show branches, included files, excluded dirty files, changelog entries, and commit messages before git changes are staged.

The point is not ceremony. The point is continuity, auditability, and fewer hidden assumptions.

## Quick Start

Install this repository as a Codex skill from its GitHub repo or local checkout.

After installation, restart Codex and check that the skill is available:

```txt
Is the 4DreamTeam skill available?
```

Then use it from any folder:

```txt
Run $4DreamTeam.
```

If the folder is empty or not yet a 4DreamTeam workspace, the skill should ask before creating workspace files.

## Quick Commands

Use these short requests when the workspace already contains 4DreamTeam artifacts:

```txt
$4DreamTeam init workspace
$4DreamTeam connect project <project-name> from <source-path>
$4DreamTeam status
$4DreamTeam continue
$4DreamTeam validate workspace
$4DreamTeam self-update workspace
$4DreamTeam check docs for <project-name>
$4DreamTeam search docs for <project-name> <query>
$4DreamTeam prepare release for <project-name>
$4DreamTeam write a press release for <project-name>
$4DreamTeam improve README positioning for <project-name>
$4DreamTeam improve <project-name>
$4DreamTeam improve 4DreamTeam itself from ../codex/4DreamTeam
```

`status`, `continue`, and `validate workspace` are read-only by default. 4DreamTeam should explain the next lifecycle step and wait for approval before changing files.

`prepare release` runs the `release` role. It is available only for accepted work. It updates `docs/<project-name>/CHANGELOG.md`, updates an approved source `CHANGELOG.md` when the source changelog policy applies, prepares a commit plan, and stages or commits only after explicit approval. It never pushes without a separate explicit approval.

`self-update workspace` replaces only the workspace root `AGENTS.md` from the installed skill template and then asks the user to restart Codex.

## Local Wiki Index

Project wikis can include a structured source map:

```txt
docs/<project-name>/source-map.md
```

`source-map.md` is the editable source of truth for semantic navigation across approved sources. Generated `.index` files are derived from it and should not be edited by hand.

The repository includes a dependency-free Bun/TypeScript CLI:

```bash
bun skill/tools/wiki.ts index build docs/<project-name>
bun skill/tools/wiki.ts index check docs/<project-name>
bun skill/tools/wiki.ts search docs/<project-name> "release changelog"
```

The index is intentionally lightweight. It searches source roots, semantic groups, file descriptions, keywords, and related wiki pages before an agent reads larger source files.

When a project wiki has a current `.index/source-map.json`, 4DreamTeam roles use index-first navigation before broad project wiki or approved-source reading. They search first, then read the relevant wiki pages and source files from the top semantic groups. Exact file/page tasks and missing or stale indexes can skip this step.

## Workspace Shape

A normal 4DreamTeam workspace does not contain the `skill/` directory. After initialization, it contains:

```txt
AGENTS.md
docs/index.md
tasks/
  product/
  analytic/
  developer/
  quality/
  wiki/
  release/
  done/
  rejected/
reports/
  product/
  tasks/
  quality/
  release/
```

`tasks/` is a role-based virtual Kanban board. A task file lives in the folder of the role that owns the next action.

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

## Common Workflows

### Product To Implementation

Use this when the request starts from business intent, product direction, or a feature idea:

```txt
Run $4DreamTeam.

Mode:
controlled

Goal:
Develop the product in the direction of <direction>.

Context:
<what is known about users, the problem, and constraints>

Expected result:
Product brief, then task specification, implementation, quality review, and docs update if needed.
```

In `controlled` mode, 4DreamTeam stops for approval after product and analytic stages.

### Direct Task

Use this when the request is already implementation-shaped:

```txt
Run $4DreamTeam.

Mode:
controlled

Goal:
Add support for X in module Y.

Constraints:
Do not change the public API.
Do not add dependencies unless necessary.

Expected result:
X works, is covered by tests, and quality review is accepted.
```

The normal route is:

```txt
analytic -> developer -> quality -> wiki if needed
```

### Release Packaging

Use this after work has accepted quality or product acceptance and should be committed:

```txt
Run $4DreamTeam.

Goal:
Prepare release for <project-name>.

Context:
Use the accepted task/report for <change>.
```

The `release` role:

1. checks the current branch and dirty tree;
2. separates included files from unrelated dirty files;
3. updates `docs/<project-name>/CHANGELOG.md`;
4. updates approved source `CHANGELOG.md` when the source changelog policy applies;
5. proposes a commit message and exact file staging plan;
6. asks for approval before `git add` and `git commit`;
7. never pushes without a separate explicit approval.

`quality` is not optional for implementation workflows.

### Workspace Status

Use this when returning to a workspace or deciding what should happen next:

```txt
Run $4DreamTeam status.
```

The status workflow summarizes workspace preflight, the role board (`product`, `analytic`, `developer`, `quality`, `wiki`, `release`, `done`, `rejected`), developer reports, quality reports, known project wikis, missing `sources.md`, blockers, and the recommended next action.

Status does not change files by default.

### Workspace Validation

Use this to find structural or lifecycle problems in the workspace:

```txt
Run $4DreamTeam validate workspace.
```

Validation checks required folders, task/report consistency, orphan reports, rejected tasks without actionable quality reports, project wikis without `sources.md`, invalid page statuses, and missing `wiki-meta` on managed pages.

Validation returns findings and a repair plan. It does not repair files unless the user explicitly approves the specific changes.

### Workspace Self-Update

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

### Wiki Bootstrap

Use this to create a project knowledge base from approved source paths:

```txt
Run $4DreamTeam: wiki bootstrap.

Knowledge base name:
northstar-ledger

Sources:
- ../northstar-ledger/src
- ../northstar-ledger/tests
- ../northstar-ledger/package.json
```

The skill treats each approved source path as a hard read boundary. It must not infer access to parent directories, sibling projects, `.env` files, secrets, dumps, or unrelated user files.

Output path:

```txt
docs/<project-name>/
```

### Wiki Audit

Use this for a read-only check of existing documentation against approved sources:

```txt
Run $4DreamTeam wiki audit for northstar-ledger.

Documentation:
- docs/northstar-ledger

Sources:
- ../northstar-ledger/src
- ../northstar-ledger/tests
```

### Marketing

Use the marketing route for external-facing communication and product narrative:

```txt
Run $4DreamTeam marketing.

Goal:
Rewrite the README so new users understand what the product is, who it is for, why it matters, and how to try it.

Sources:
- docs/northstar-ledger
- ../northstar-ledger/README.md
```

Marketing can create press releases, launch announcements, README positioning, product messaging, FAQs, case studies, and market-facing analytical briefs.

Marketing must use confirmed sources. It must not invent metrics, customers, benchmarks, certifications, security claims, or roadmap commitments.

### Self-Improvement

Use this when a 4DreamTeam workspace is managing improvements to the `4DreamTeam` skill itself:

```txt
Run $4DreamTeam.

Goal:
Improve 4DreamTeam itself.

Knowledge base:
4DreamTeam

Approved source:
../codex/4DreamTeam
```

Self-improvement follows a simplified controlled lifecycle:

```txt
product -> developer -> wiki -> product acceptance
```

The only required human-in-the-loop approval point is between `product` and `developer`: the human decides exactly what goes into the developer task.

The source repository is the approved source boundary. Typical write targets are `skill/SKILL.md`, `skill/references/`, `skill/assets/templates/`, `skill/agents/openai.yaml`, `README.md`, and repository `AGENTS.md`.

Markdown documentation and templates in the skill repository remain English-only unless the repository rules explicitly change.

### DevOps

Use the DevOps route for infrastructure work:

```txt
Run $4DreamTeam devops.

Project:
northstar-ledger

Goal:
Inspect the production server and update the server card with verified facts only.
```

Server docs are stored here:

```txt
docs/<project-name>/devops/servers/
```

SSH keys are looked up only in the workspace root:

```txt
keys/
```

`keys/` is a local secret area. The skill must not print key contents, copy keys into documentation, or commit them.

DevOps follows a stricter operational sequence:

```txt
inspect -> explain -> wait for approval -> change -> verify -> document
```

Risky operations always require explicit approval, including deploys, restarts, migrations, environment changes, nginx/systemd/Docker changes, database writes, firewall changes, and DNS changes.

## Safety Guarantees

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

## Repository Structure

This repository contains the skill itself:

```txt
4DreamTeam/
  AGENTS.md
  README.md
  skill/
    SKILL.md
    agents/
      openai.yaml
    references/
    assets/
      templates/
```

Important files:

- `skill/SKILL.md` - skill metadata, trigger surface, entrypoint, hard guarantees.
- `skill/references/` - detailed role and workflow rules.
- `skill/assets/templates/` - templates copied or adapted into user workspaces.
- `skill/agents/openai.yaml` - Codex UI metadata.
- `AGENTS.md` - development rules for this repository.

## Development

This repository is for developing the `4DreamTeam` skill, not for running external project tasks through 4DreamTeam itself.

Before changing the skill, check which layer is affected:

- `skill/SKILL.md` for trigger surface and hard guarantees;
- `skill/agents/openai.yaml` for Codex UI metadata;
- `skill/references/` for detailed role behavior;
- `skill/assets/templates/` for generated workspace artifacts;
- `README.md` for user-facing skill documentation;
- `AGENTS.md` for repository development rules.

Keep `SKILL.md` concise and move detailed behavior into references. Keep templates aligned with the rules that mention them.
