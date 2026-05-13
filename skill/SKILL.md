---
name: 4dreamteam
version: 0.0.2
description: Coordinate the 4DreamTeam file-based agent framework for Codex. Use when the user wants to run a task through product, analytic, developer, quality, wiki, marketing, and devops roles; turn business requests into product briefs; decompose features; plan product development; create press releases, product messaging, README positioning, and market-facing analytical materials; create, audit, sync, blueprint, or deepen a project knowledge base; inspect or document infrastructure, servers, deployments, logs, SSH access, migrations, or operational runbooks; continue a pending, rejected, or completed task; verify work with independent quality checks; initialize, update, validate, or summarize a 4DreamTeam workspace; improve the 4DreamTeam skill itself; or asks to work with 4DreamTeam workflow, 4DreamTeam lead, tasks, reports, accepted/rejected quality, or per-project docs knowledge bases.
---

# 4DreamTeam

Use this skill as the main entrypoint for the 4DreamTeam framework. The user should be able to talk to `$4DreamTeam` instead of remembering individual role names.

## First Steps

1. Read `references/lead.md`.
2. Check whether the current folder is a 4DreamTeam workspace before writing files. Do not require a `skill/` folder in normal workspaces after the skill is installed.
3. Route the request to the relevant role workflow.
4. Load only the role reference needed for the route.

## Role References

- Product ownership, business intake, feature decomposition, product development, product acceptance: read `references/product.md`.
- Task analysis: read `references/analytic.md`.
- Implementation: read `references/developer.md`.
- Independent acceptance: read `references/quality.md`.
- Knowledge base, docs, source boundaries, bootstrap/audit/sync/check/blueprint/deepening: read `references/wiki.md`, then follow `references/wiki/index.md`.
- Marketing, press releases, product messaging, README positioning, launch materials, market-facing analysis: read `references/marketing.md`.
- Infrastructure operations, server documentation, deployment diagnostics, SSH access, logs, migrations, and operational runbooks: read `references/devops.md`.

## Templates

Use bundled templates from `assets/templates/`:

- `assets/templates/analytic/task.md`
- `assets/templates/product/brief.md`
- `assets/templates/product/report.md`
- `assets/templates/product/review-accepted.md`
- `assets/templates/product/review-rejected.md`
- `assets/templates/developer/report.md`
- `assets/templates/quality/accepted.md`
- `assets/templates/quality/rejected.md`
- `assets/templates/marketing/press-release.md`
- `assets/templates/marketing/market-analysis.md`
- `assets/templates/wiki/docs-index.md`
- `assets/templates/wiki/project.md`
- `assets/templates/wiki/product-overview.md`
- `assets/templates/wiki/architecture-overview.md`
- `assets/templates/wiki/source-map.md`
- `assets/templates/wiki/adr.md`
- `assets/templates/devops/server-index.md`
- `assets/templates/devops/server-card.md`
- `assets/templates/workspace/AGENTS.md`

## Hard Guarantees

1. Do not bypass 4DreamTeam workflow with ad-hoc work when a 4DreamTeam route applies.
2. Do not write files until workspace preflight passes or the user explicitly confirms using the current folder as a 4DreamTeam workspace.
3. In an empty folder, create only workspace artifacts after confirmation: `AGENTS.md`, `docs/index.md`, `tasks/`, and `reports/`. Use `assets/templates/workspace/AGENTS.md` for `AGENTS.md`. Do not create a `skill/` skill folder there.
4. Do not skip independent quality for task implementation workflows.
5. Do not run wiki post-acceptance updates before accepted quality report.
6. For wiki bootstrap, show intake summary and wait for confirmation before creating files unless the user explicitly accepts defaults/auto.
7. Treat approved source paths as hard read boundaries.
8. DevOps server documentation belongs in `docs/<project-name>/devops/servers/`; DevOps keys are looked up only in workspace-root `keys/`.
9. Report created and changed files at the end.
