---
name: 4dreamteam
description: Coordinate the 4DreamTeam file-based agent framework for Codex. Use when the user wants product, analytic, developer, quality, wiki, marketing, devops, or release roles; task intake, feature decomposition, implementation, independent quality, changelog and commit prep; press releases or product messaging; project knowledge-base bootstrap, audit, sync, blueprint, deepening, indexing, or search; infrastructure, deployment, logs, migrations, SSH, or runbook documentation; or 4DreamTeam workspace initialization, validation, summaries, and skill improvements.
license: MIT
metadata:
  author: Tsmar
  version: 0.1.8
  repository: https://github.com/Tsmar/4DreamTeam
---

# 4DreamTeam

Use this skill as the main entrypoint for the 4DreamTeam framework. The user should be able to talk to `$4DreamTeam` instead of remembering individual role names.

## First Steps

1. Read `references/lead.md`.
2. Follow the lead module map and load only the smallest sufficient detailed reference files for the route.
3. Check whether the current folder is a 4DreamTeam workspace before writing files. Do not require a `skill/` folder in normal workspaces after the skill is installed.
4. Route the request to the relevant role workflow.
5. Load only the role reference and mode-specific references needed for the route.

## Role References

- Product ownership, business intake, feature decomposition, product development, product acceptance: read `references/product.md`.
- Task analysis: read `references/analytic.md`.
- Implementation: read `references/developer.md`.
- Independent acceptance: read `references/quality.md`.
- Knowledge base, docs, source boundaries, source maps, local wiki indexes, bootstrap/audit/sync/check/blueprint/deepening: read `references/wiki.md`, then follow `references/wiki/index.md`.
- Marketing, GTM briefs, value reviews, claim audits, release narratives, press releases, product messaging, README positioning, launch materials, market-facing analysis: read `references/marketing.md`.
- Infrastructure operations, server documentation, deployment diagnostics, SSH access, logs, migrations, and operational runbooks: read `references/devops.md`.
- Release packaging, changelogs, branch checks, commit plans, staging, and commits after accepted work: read `references/release.md`.

## Templates

Use bundled templates from `assets/templates/`:

- `assets/templates/analytic/task.md`
- `assets/templates/product/epic.md`
- `assets/templates/product/report.md`
- `assets/templates/product/review-accepted.md`
- `assets/templates/product/review-rejected.md`
- `assets/templates/developer/report.md`
- `assets/templates/quality/accepted.md`
- `assets/templates/quality/rejected.md`
- `assets/templates/lead/epic-handoff.md`
- `assets/templates/marketing/press-release.md`
- `assets/templates/marketing/market-analysis.md`
- `assets/templates/marketing/value-review.md`
- `assets/templates/marketing/readme-positioning-review.md`
- `assets/templates/marketing/release-narrative.md`
- `assets/templates/marketing/gtm-brief.md`
- `assets/templates/marketing/claim-audit.md`
- `assets/templates/release/plan.md`
- `assets/templates/wiki/docs-index.md`
- `assets/templates/wiki/project.md`
- `assets/templates/wiki/product-overview.md`
- `assets/templates/wiki/architecture-overview.md`
- `assets/templates/wiki/sources.md`
- `assets/templates/wiki/source-map.md`
- `assets/templates/wiki/adr.md`
- `assets/templates/devops/server-index.md`
- `assets/templates/devops/server-card.md`
- `assets/templates/workspace/AGENTS.md`
- `assets/templates/workspace/sources.gitignore`

## Reference Loading

Marketing templates are selected by mode:

- Use `assets/templates/marketing/value-review.md` when accepted work, a feature, UX/API/workflow change, or a release candidate needs user-facing value validation.
- Use `assets/templates/marketing/readme-positioning-review.md` when reviewing README clarity, first-screen promise, audience, proof points, risky claims, and next steps.
- Use `assets/templates/marketing/release-narrative.md` before release when accepted changes need user-facing and developer-facing release communication.
- Use `assets/templates/marketing/gtm-brief.md` during early product, module, or large-epic shaping for ICP, jobs-to-be-done, positioning, messaging, adoption, objections, channels, assumptions, and validation needs.
- Use `assets/templates/marketing/claim-audit.md` before public claims appear in README, landing pages, release notes, pitch decks, press releases, case studies, or launch copy.

Use route-specific references to reduce unnecessary context:

- Read `references/lead.md` as the compact entrypoint and module map.
- Follow the context budget policy in `references/lead/context-budget.md` when a route may require broad reading, staged expansion, or artifact handoff.
- Read `references/lead/memory.md` only when prior session context, saved decisions, user preferences, wiki fallback, or memory effectiveness is relevant.
- Read `references/lead/read-only.md` only for status, continuation, validation, or direct project questions.
- Read `references/lead/self-maintenance.md` only for self-update or self-improvement.
- Read `references/lead/lifecycle.md`, `references/lead/contracts.md`, or `references/lead/safety.md` when their gates or artifacts apply.
- For wiki work, read `references/wiki.md`, `references/wiki/index.md`, `references/wiki/shared.md`, then only the shared modules and mode file selected by the route.

## Hard Guarantees

1. Do not bypass 4DreamTeam workflow with ad-hoc work when a 4DreamTeam route applies.
2. Do not write files until workspace preflight passes or the user explicitly confirms using the current folder as a 4DreamTeam workspace.
3. In an empty folder, create only workspace artifacts after confirmation: `AGENTS.md`, `docs/index.md`, `tasks/`, `reports/`, and `sources/.gitignore`. Use `assets/templates/workspace/AGENTS.md` for `AGENTS.md` and `assets/templates/workspace/sources.gitignore` for `sources/.gitignore`. Do not create a `skill/` skill folder there.
4. Do not skip independent quality for task implementation workflows.
5. Do not run wiki post-acceptance updates before accepted quality report.
6. For wiki bootstrap, show intake summary and wait for confirmation before creating files unless the user explicitly accepts defaults/auto.
7. Treat confirmed workspace `sources/` descendants and explicitly approved external source paths as hard read boundaries.
8. Do not list, stat, resolve, inventory, index, or read workspace `sources/` before operator first-touch confirmation.
9. Ask the operator to confirm scoped auto mode for `lead -> product`, `product -> analytic`, `analytic -> developer`, and `quality -> wiki` transitions unless the exact transition is already approved for the current scope.
10. Create an epic handoff in `reports/handoffs/` before closing a completed epic or starting the next epic as the active implementation focus.
11. DevOps server documentation belongs in `docs/<project-name>/devops/servers/`; DevOps keys are looked up only in workspace-root `keys/`.
12. Release commits require accepted quality or product acceptance, a visible commit plan, and explicit user approval before staging or committing.
13. Wiki source maps are maintained in `docs/<project-name>/source-map.md`; generated `.index/*` files must be rebuilt with the bundled wiki index tooling instead of edited by hand.
14. When a current local wiki index exists, use index-first navigation before broad project wiki or approved-source reading.
15. Report created and changed files at the end.
