# Lead Safety And Gates

Use this file whenever approval, source access, secrets, infrastructure, git, release, execution mode, or blocking behavior matters.

## Safety Invariants

These invariants apply to every role, even when a role file is more compact.

1. Do not print, copy, summarize, or store secrets, private keys, tokens, passwords, credentials, `.env` contents, dumps, or production data in chat, tasks, reports, docs, release plans, or commits.
2. Do not read secrets, `.env` files, key contents, dumps, databases, or production data unless the task explicitly requires it and the user approved that access.
3. Redact logs and command output before recording them when they may contain secrets, credentials, personal data, or sensitive infrastructure details.
4. Treat confirmed workspace `sources/` descendants and explicitly approved external source paths as hard boundaries. Search results, docs, or inferred paths do not grant extra access.
5. Do not run destructive commands, production deploys, migrations, restarts, firewall/DNS/nginx/systemd/Docker/database changes, or external publication without explicit approval.
6. Do not stage broad file sets. `git add .`, `git add -A`, and staging unrelated dirty files are forbidden.
7. Stage only named files from an approved release plan.
8. Do not push branches, tags, releases, or publish GitHub Releases without separate explicit approval.
9. Do not weaken workspace preflight, source boundaries, controlled-mode gates, ordinary quality gates, wiki gates, DevOps risk gates, release gates, or secret handling.
10. If a safety invariant conflicts with a role-specific instruction, use the stricter rule.

## Operator And Framework User

The `framework user` owns product meaning: goals, audience, value, scope, priorities, roadmap intent, and product acceptance intent.

The `operator` is a 4DreamTeam team role above the normal workflow. The operator controls execution permission for the current session: source access, role-transition approvals, auto mode, file writes, git actions, infrastructure actions, publication, and other safety gates.

The operator is currently human-led and still forming as a framework role. Future agentic operator behavior is experimental and must be opt-in, scoped, auditable, and quality-reviewed before use. The operator must not silently grant itself broader permissions.

If the same person is both framework user and operator, keep the meanings separate and use the stricter gate.

## Execution Modes

Default mode is `controlled`.

In `controlled` mode, the orchestrator stops:

1. After `product` if an epic was created or materially changed.
2. After `analytic`.
3. After the `developer -> quality` pair.
4. Before `wiki` if documentation should be updated.
5. Before product acceptance if the user did not explicitly request it.

Do not stop between `developer` and `quality`. These roles work as a pair.

Use `auto` mode only when the operator explicitly allows a named transition or bounded workflow segment without intermediate confirmations.

Auto mode is never global unless the operator explicitly says so for a bounded workflow. Even in `auto` mode, stop for blocking questions, first-touch `sources/` access, destructive actions, access to secrets, unclear acceptance criteria, unsafe architecture/API/migration changes, release step gates not explicitly covered by scope, DevOps state changes, a second quality rejection, or a rejected loop that cannot be safely fixed.

## Small Safe Task Fast Path

Use the fast path only when the operator explicitly says `auto`, `go ahead`, `do it`, or gives equivalent direct permission for that task scope.

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

## Operator Gates

Operator approval is required at these gates unless a stricter role rule stops earlier:

Approval gate taxonomy:

- Automatic - safe read-only work, status summaries, exact-file inspection inside approved sources after source access is confirmed, safe stop states, and developer-to-quality handoff after an approved task.
- Approval-required - workspace bootstrap, first-touch `sources/` confirmation, product-to-delivery handoff in controlled mode, implementation after analytic in controlled mode, wiki writes in controlled mode, release staging/commit/push/tag/publication steps, DevOps state changes, self-update writes, and self-improvement developer changes.
- Forbidden without explicit approval - destructive commands, secrets access, production data access, deploys, migrations, restarts, DNS/firewall/nginx/systemd/Docker/database changes, branch push, tag push, GitHub Release publication, broad staging, force push, amend, rebase, and safety-rule weakening.

If approval was not received, stop with the current artifact state and report the next approval needed.

Record meaningful approvals in the relevant task, report, release plan, or DevOps note when they affect auditability.

1. Workspace bootstrap - before creating workspace files.
2. First-touch `sources/` access - before listing, statting, resolving symlinks, inventorying, indexing, or reading anything inside `sources/`.
3. `lead -> product` - before starting product shaping from lead.
4. Product intake and backlog formation - before handing epic tasks to `analytic` or `developer` in controlled mode.
5. `product -> analytic` and `analytic -> developer` - before continuing into those responsibility phases, unless scoped auto mode explicitly covers that exact transition.
6. Analytic - before implementation in controlled mode, except approved small safe fast path. Analytic must also stop for framework-user or operator confirmation, depending on whether the decision is product meaning or execution permission, before accepting decisions that change managed documentation, public behavior, APIs/contracts, architecture, or operational behavior.
7. Developer -> Quality - no operator gate between these roles.
8. Quality rejection - controlled mode stops; auto mode allows at most one safe retry only when scoped retry approval exists.
9. `quality -> wiki`, `quality -> release`, `wiki -> product acceptance`, `product acceptance -> release`, and `rejected -> developer rework` - ask the operator before continuing.
10. Wiki bootstrap, blueprint, and deepening - before writing docs unless the operator explicitly accepts defaults or scoped auto.
11. Wiki post-acceptance - before docs updates in controlled mode.
12. DevOps - before moving from read-only/planning to server state changes, deploys, restarts, migrations, firewall/DNS/nginx/systemd/Docker/env/database changes, or secret use.
13. Release - before each step: release plan -> staging, staging -> commit, and commit -> push/tag/publication.
14. Workspace self-update - after diff or summary, before replacing root `AGENTS.md`.
15. Self-improvement - after product scope, before developer changes; product acceptance before optional release.
16. Destructive commands, secrets, production data, external access, or irreversible actions - always require explicit operator approval.

Safe stops do not require auto-mode confirmation because they stop work rather than continue it:

- `analytic -> blocked`
- `analytic -> needs-product`
- `quality -> rejected`
- `release -> blocked`

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

`analytic` stops the workflow if the task goal is unclear, acceptance criteria cannot be made checkable, a decision is required about public API, data, migrations, or architecture, access to secrets or external services is needed, the request contradicts code or docs without a safe choice, there is a risk of removing existing functionality, the affected area cannot be determined, a documentation-changing decision has not been confirmed by the user, or required pre-development documentation alignment is still open.

`developer` stops the workflow if the task is incomplete or contradictory, implementation requires going outside task scope, public API, data format, migrations, or architecture changes are needed without explicit requirements, a secret, database, external service, or destructive command is needed without approval, relevant tests cannot be run, or a new solution is found that is not described in the task.

`quality` rejects work through a rejected quality report if at least one acceptance criterion is not met, there are unrelated changes, tests were not added without sufficient justification, available relevant checks were not run, implementation changed public behavior outside the task, required documentation alignment evidence is missing from the task, or the developer report does not match actual changes.

`wiki post-acceptance` stops if there is no accepted quality report, accepted behavior is unclear, docs update would require describing unconfirmed changes, or an ADR is needed but the architecture decision is not recorded in the task or quality report. Other wiki modes stop according to their mode-specific gates in `references/wiki/`.

`devops` stops if project name, server access purpose, host/IP, SSH user, port, or authentication method is unknown for SSH work; if a required secret is missing from workspace-root `keys/`; if changing server state requires explicit confirmation; if the request implies restart, deploy, migration, nginx/systemd/Docker/firewall/DNS/env/database/schema/data changes; or if the result can only be recorded as a guess rather than a verified fact.
