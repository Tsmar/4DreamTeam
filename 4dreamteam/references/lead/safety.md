# Lead Safety And Gates

Use this file whenever approval, source access, secrets, infrastructure, git, release, execution mode, or blocking behavior matters.

## Safety Invariants

These invariants apply to every role, even when a role file is more compact.

1. Do not print, copy, summarize, or store secrets, private keys, tokens, passwords, credentials, `.env` contents, dumps, or production data in chat, tasks, reports, docs, release plans, or commits.
2. Do not read secrets, `.env` files, key contents, dumps, databases, or production data unless the task explicitly requires it and the user approved that access.
3. Redact logs and command output before recording them when they may contain secrets, credentials, personal data, or sensitive infrastructure details.
4. Treat approved source paths as hard boundaries. Search results, docs, or inferred paths do not grant extra access.
5. Do not run destructive commands, production deploys, migrations, restarts, firewall/DNS/nginx/systemd/Docker/database changes, or external publication without explicit approval.
6. Do not stage broad file sets. `git add .`, `git add -A`, and staging unrelated dirty files are forbidden.
7. Stage only named files from an approved release plan.
8. Do not push branches, tags, releases, or publish GitHub Releases without separate explicit approval.
9. Do not weaken workspace preflight, source boundaries, controlled-mode gates, ordinary quality gates, wiki gates, DevOps risk gates, release gates, or secret handling.
10. If a safety invariant conflicts with a role-specific instruction, use the stricter rule.

## Execution Modes

Default mode is `controlled`.

In `controlled` mode, the orchestrator stops:

1. After `product` if an epic was created or materially changed.
2. After `analytic`.
3. After the `developer -> quality` pair.
4. Before `wiki` if documentation should be updated.
5. Before product acceptance if the user did not explicitly request it.

Do not stop between `developer` and `quality`. These roles work as a pair.

Use `auto` mode only when the user explicitly allows a full pass without intermediate confirmations.

Even in `auto` mode, stop for blocking questions, destructive actions, access to secrets, unclear acceptance criteria, unsafe architecture/API/migration changes, a second quality rejection, or a rejected loop that cannot be safely fixed.

## Small Safe Task Fast Path

Use the fast path only when the user explicitly says `auto`, `go ahead`, `do it`, or gives equivalent direct permission.

A small safe task must meet all conditions:

1. Scope is small and localized.
2. Acceptance criteria are obvious and checkable.
3. No public API, schema, migration, architecture, data format, auth, permission, deployment, or external-service behavior changes are required.
4. No secrets, destructive commands, production data, or server state changes are needed.
5. Relevant checks are available or the reason they cannot run is low risk.

Fast path flow:

```txt
analytic compact task -> developer -> quality
```

Never skip `quality` on the fast path.

## Human-In-The-Loop Gates

Human approval is required at these gates unless a stricter role rule stops earlier:

Approval gate taxonomy:

- Automatic - safe read-only work, status summaries, exact-file inspection inside approved sources, and developer-to-quality handoff after an approved task.
- Approval-required - workspace bootstrap, product-to-delivery handoff in controlled mode, implementation after analytic in controlled mode, wiki writes in controlled mode, release staging/commit, DevOps state changes, self-update writes, and self-improvement developer changes.
- Forbidden without explicit approval - destructive commands, secrets access, production data access, deploys, migrations, restarts, DNS/firewall/nginx/systemd/Docker/database changes, branch push, tag push, GitHub Release publication, broad staging, force push, amend, rebase, and safety-rule weakening.

If approval was not received, stop with the current artifact state and report the next approval needed.

Record meaningful approvals in the relevant task, report, release plan, or DevOps note when they affect auditability.

1. Workspace bootstrap - before creating workspace files.
2. Product intake and backlog formation - before handing epic tasks to `analytic` or `developer` in controlled mode.
3. Analytic - before implementation in controlled mode, except approved small safe fast path.
4. Developer -> Quality - no human gate between these roles.
5. Quality rejection - controlled mode stops; auto mode allows at most one safe retry.
6. Wiki bootstrap, blueprint, and deepening - before writing docs unless the user explicitly accepts defaults or auto.
7. Wiki post-acceptance - before docs updates in controlled mode.
8. DevOps - before server state changes, deploys, restarts, migrations, firewall/DNS/nginx/systemd/Docker/env/database changes, or secret use.
9. Release - before staging or committing; branch push, tag push, and GitHub Release publication each require explicit approval.
10. Workspace self-update - after diff or summary, before replacing root `AGENTS.md`.
11. Self-improvement - after product scope, before developer changes; product acceptance before optional release.
12. Destructive commands, secrets, production data, external access, or irreversible actions - always require explicit approval.

## Blocking Questions

If `product` or `analytic` finds blocking questions, the workflow stops until the user answers.

These are not blocking:

- local variable name choices;
- minor implementation details;
- internal helper format;
- choices between equivalent technical options;
- wording of a minor user story when product meaning does not change.

The agent decides these questions itself and records them in `Assumptions`.

## Role Blockers

`product` stops the workflow if the business goal, target audience, MVP/later split, or product acceptance criteria are unclear; if the goal and constraints conflict; if access to unapproved sources is needed; or if product acceptance requires materials outside available scope.

`analytic` stops the workflow if the task goal is unclear, acceptance criteria cannot be made checkable, a decision is required about public API, data, migrations, or architecture, access to secrets or external services is needed, the request contradicts code or docs without a safe choice, there is a risk of removing existing functionality, or the affected area cannot be determined.

`developer` stops the workflow if the task is incomplete or contradictory, implementation requires going outside task scope, public API, data format, migrations, or architecture changes are needed without explicit requirements, a secret, database, external service, or destructive command is needed without approval, relevant tests cannot be run, or a new solution is found that is not described in the task.

`quality` rejects work through a rejected quality report if at least one acceptance criterion is not met, there are unrelated changes, tests were not added without sufficient justification, available relevant checks were not run, implementation changed public behavior outside the task, or the developer report does not match actual changes.

`wiki post-acceptance` stops if there is no accepted quality report, accepted behavior is unclear, docs update would require describing unconfirmed changes, or an ADR is needed but the architecture decision is not recorded in the task or quality report. Other wiki modes stop according to their mode-specific gates in `references/wiki/`.

`devops` stops if project name, server access purpose, host/IP, SSH user, port, or authentication method is unknown for SSH work; if a required secret is missing from workspace-root `keys/`; if changing server state requires explicit confirmation; if the request implies restart, deploy, migration, nginx/systemd/Docker/firewall/DNS/env/database/schema/data changes; or if the result can only be recorded as a guess rather than a verified fact.
