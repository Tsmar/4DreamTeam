# Examples

These examples are intentionally close to real user situations. They show how 4DreamTeam turns vague requests into traceable work without pretending every request starts as a perfect ticket.

## Founder MVP

User:

```txt
$4DreamTeam

Goal:
I want a booking system for a small yoga studio.

Context:
The owner takes bookings in WhatsApp. People cancel, reschedule, and forget to pay. The first version should be simple enough to run manually.
```

Likely route:

```txt
product -> analytic -> developer -> quality -> wiki if needed
```

What 4DreamTeam should produce:

1. Product epic with target users, scope, non-goals, assumptions, and product acceptance criteria.
2. Task candidates such as booking request form, admin booking list, and notification copy.
3. Implementation-ready task specs after approval.
4. Developer reports and independent quality reports.

Why this matters:

- The user has a problem and constraints, not a spec.
- 4DreamTeam slows down enough to protect MVP scope before implementation.

## Bug With Unknown Cause

User:

```txt
$4DreamTeam fix the checkout bug. Users say discounts sometimes disappear before payment.
```

Likely route:

```txt
analytic -> developer -> quality
```

What 4DreamTeam should do:

1. Identify affected areas from approved docs or source boundaries.
2. Write a task with checkable acceptance criteria.
3. Implement a minimal fix.
4. Run relevant checks and record what was not run.
5. Let quality accept or reject based on evidence.

Why this matters:

- The symptom is real, but the cause is unknown.
- 4DreamTeam should not guess its way straight into code.

## Half-Finished Work

User:

```txt
I implemented invite emails yesterday. Can you check whether this is actually done?
```

Likely route:

```txt
quality, or developer -> quality if missing work is found
```

What 4DreamTeam should inspect:

- Task or intended behavior.
- Developer report if present.
- Tests/checks that were run.
- User-visible behavior and documentation impact.

Possible result:

- Accepted quality report if every criterion passes.
- Rejected quality report with a concrete correction path if something is missing.

## Returning After Context Loss

User:

```txt
$4DreamTeam continue
```

Likely route:

```txt
status / continuation
```

What 4DreamTeam should read:

- `AGENTS.md`
- `tasks/`
- `reports/`
- `4dt-wiki status`
- relevant wiki pages and optional memory only when useful

Output:

- Current role board.
- Active/rejected/blocked tasks.
- Accepted reports.
- Recommended next safe action.

Why this matters:

- Chat context is fragile.
- Files make the project resumable.

## Docs From An Existing Codebase

User:

```txt
$4DreamTeam wiki bootstrap

Project:
northstar-ledger

Sources:
- ../northstar-ledger/src
- ../northstar-ledger/tests
- ../northstar-ledger/package.json
```

Likely route:

```txt
wiki bootstrap
```

What 4DreamTeam should do:

1. Show an intake summary before writing.
2. Treat each source path as a hard boundary.
3. Create or update the managed wiki through `4dt-wiki`.
4. Build a source map and local index when possible.

What it must not do:

- Read parent directories.
- Read `.env`, secrets, dumps, or unrelated user files.
- Invent facts not backed by approved sources.

## Release Packaging

User:

```txt
$4DreamTeam prepare release for the accepted booking-form work.
```

Likely route:

```txt
release
```

Required evidence:

- Accepted quality report or product acceptance.
- Developer report for implementation work.
- Clear included/excluded file list.

What 4DreamTeam should produce:

- Changelog update plan.
- Dirty tree review.
- Exact staging plan.
- Commit message proposal.
- Approval request before `git add` or `git commit`.

## DevOps Documentation

User:

```txt
$4DreamTeam devops

Project:
northstar-ledger

Goal:
Inspect the production server and update the server card with verified facts only.
```

Likely route:

```txt
devops
```

Operating sequence:

```txt
inspect -> explain -> wait for approval -> change -> verify -> document
```

DevOps must not print key contents, copy secrets into docs, or change server state without explicit approval.

## Improve 4DreamTeam Itself

User:

```txt
$4DreamTeam improve 4DreamTeam itself from your local checkout of https://github.com/Tsmar/4DreamTeam, for example /Users/Tsmar/Projects/4DreamTeam
```

Likely route:

```txt
product -> developer -> quality -> wiki when needed -> product acceptance
```

Why this exists:

- Framework behavior changes can affect safety, routing, lifecycle, and release behavior.
- 4DreamTeam dogfoods its own quality gate instead of editing instructions ad hoc.
