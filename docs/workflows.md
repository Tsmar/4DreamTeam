# Workflows

This page holds the operational workflow details that used to live in the main README.

## Install

Open a new chat and write: install the skill from [Tsmar/4DreamTeam](https://github.com/Tsmar/4DreamTeam/tree/main/4dreamteam).

Restart Codex after installation so the skill is loaded in a clean session.

## Quick Commands

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
$4DreamTeam improve 4DreamTeam itself from your local checkout of https://github.com/Tsmar/4DreamTeam, for example /Users/Tsmar/Projects/4DreamTeam
```

`status`, `continue`, and `validate workspace` are read-only by default. 4DreamTeam should explain the next lifecycle step and wait for approval before changing files.

## Product To Implementation

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
Epic, then task specification, implementation, quality review, and docs update if needed.
```

In `controlled` mode, 4DreamTeam stops for approval after product and analytic stages.

## Direct Task

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

## Workspace Status

Use this when returning to a workspace or deciding what should happen next:

```txt
Run $4DreamTeam status.
```

The status workflow summarizes workspace preflight, the role board, developer reports, quality reports, known project wikis, missing `sources.md`, blockers, and the recommended next action.

Status does not change files by default.

## Workspace Validation

Use this to find structural or lifecycle problems in the workspace:

```txt
Run $4DreamTeam validate workspace.
```

Validation checks required folders, task/report consistency, orphan reports, rejected tasks without actionable quality reports, project wikis without `sources.md`, invalid page statuses, and missing `wiki-meta` on managed pages.

Validation returns findings and a repair plan. It does not repair files unless the user explicitly approves the specific changes.

## Wiki Bootstrap

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

## Wiki Audit

Use this for a read-only check of existing documentation against approved sources:

```txt
Run $4DreamTeam wiki audit for northstar-ledger.

Documentation:
- docs/northstar-ledger

Sources:
- ../northstar-ledger/src
- ../northstar-ledger/tests
```

## Marketing

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

## Release Packaging

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

## Self-Improvement

Use this when a 4DreamTeam workspace is managing improvements to the `4DreamTeam` skill itself:

```txt
Run $4DreamTeam.

Goal:
Improve 4DreamTeam itself.

Knowledge base:
4DreamTeam

Approved source:
your local checkout of https://github.com/Tsmar/4DreamTeam, for example /Users/Tsmar/Projects/4DreamTeam
```

Self-improvement follows a controlled lifecycle:

```txt
product -> developer -> quality -> wiki when needed -> product acceptance
```

The human approval point between `product` and `developer` decides exactly what goes into the developer task. Risky framework changes then require independent quality before wiki, product acceptance, or release packaging.

## DevOps

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

Risky operations always require explicit approval, including deploys, restarts, migrations, environment changes, nginx/systemd/Docker changes, database writes, firewall changes, and DNS changes.
