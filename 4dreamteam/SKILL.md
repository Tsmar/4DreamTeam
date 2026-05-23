---
name: 4dreamteam
description: Coordinate the 4DreamTeam file-based agent framework for Codex. Use when the user wants product, analytic, developer, quality, wiki, marketing, devops, or release roles; task intake, feature decomposition, implementation, independent quality, changelog and commit prep; press releases or product messaging; project knowledge-base bootstrap, audit, sync, blueprint, deepening, indexing, or search; infrastructure, deployment, logs, migrations, SSH, or runbook documentation; or 4DreamTeam workspace initialization, validation, summaries, and skill improvements.
license: MIT
metadata:
  author: Tsmar
  version: 0.2.0
  repository: https://github.com/Tsmar/4DreamTeam
---

# 4DreamTeam

Use this skill as the main entrypoint for the 4DreamTeam framework. The user should be able to talk to `$4DreamTeam` instead of remembering individual role names.

## First Steps

1. Read `references/lead.md`.
2. For a new session, read `references/lead/preflight.md` and run command-based onboarding before proposing work.
3. Follow the lead module map and load only the smallest sufficient detailed reference files for the route.
4. Check whether the current folder is a 4DreamTeam workspace before writing files. Do not require a `skill/` folder in normal workspaces after the skill is installed.
5. Route the request to the relevant role workflow.
6. Load only the role reference and mode-specific references needed for the route.

## Role References

- Product ownership, business intake, feature decomposition, product development, product acceptance: read `references/product.md`.
- Task analysis: read `references/analytic.md`.
- Implementation: read `references/developer.md`.
- Independent acceptance: read `references/quality.md`.
- Knowledge base, docs, source boundaries, wiki search, bootstrap/audit/sync/check/blueprint/deepening: read `references/wiki.md`, then follow `references/wiki/index.md`.
- Marketing, GTM briefs, value reviews, claim audits, release narratives, press releases, product messaging, README positioning, launch materials, market-facing analysis: read `references/marketing.md`.
- Infrastructure operations, server documentation, deployment diagnostics, SSH access, logs, migrations, and operational runbooks: read `references/devops.md`.
- Release packaging, changelogs, branch checks, commit plans, staging, and commits after accepted work: read `references/release.md`.

## Templates

Use bundled templates from `assets/templates/`:

- `assets/templates/analytic/task.md`
- `assets/templates/product/epic.md`
- `assets/templates/lead/epic-handoff.md`
- `assets/templates/marketing/press-release.md`
- `assets/templates/marketing/market-analysis.md`
- `assets/templates/marketing/value-review.md`
- `assets/templates/marketing/readme-positioning-review.md`
- `assets/templates/marketing/release-narrative.md`
- `assets/templates/marketing/gtm-brief.md`
- `assets/templates/marketing/claim-audit.md`
- `assets/templates/release/plan.md`
- `assets/templates/wiki/project.md`
- `assets/templates/wiki/product-overview.md`
- `assets/templates/wiki/architecture-overview.md`
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
- Read `references/lead/memory.md` only when prior session context, saved decisions, user preferences, local memory fallback, or memory effectiveness is relevant.
- Read `references/lead/read-only.md` only for status, continuation, validation, or direct project questions.
- Read `references/lead/self-maintenance.md` only for self-update or self-improvement.
- Read `references/lead/lifecycle.md`, `references/lead/contracts.md`, or `references/lead/safety.md` when their gates or artifacts apply.
- For wiki work, read `references/wiki.md`, `references/wiki/index.md`, `references/wiki/shared.md`, then only the shared modules and mode file selected by the route.

## Hard Guarantees

1. Do not bypass 4DreamTeam workflow with ad-hoc work when a 4DreamTeam route applies.
2. Do not write files until workspace preflight passes or the user explicitly confirms using the current folder as a 4DreamTeam workspace.
3. In an empty folder, create only workspace artifacts after confirmation: `AGENTS.md`, tool-managed workspace state, and `sources/.gitignore`. Use `assets/templates/workspace/AGENTS.md` for `AGENTS.md`, `assets/templates/workspace/sources.gitignore` for `sources/.gitignore`, `4dt-board` for board artifacts, `4dt-wiki` for wiki artifacts, and `4dt-sources` for source registry artifacts. Do not create a `skill/` skill folder there.
4. Do not skip independent quality for task implementation workflows.
5. Do not run wiki post-acceptance updates before an accepted quality timeline entry.
6. For wiki bootstrap, show intake summary and wait for confirmation before creating files unless the user explicitly accepts defaults/auto.
7. Treat workspace `sources/` descendants and explicitly approved external source paths registered through `4dt-sources` as hard read boundaries.
8. Workspace `sources/` is available for reading by default, but external source boundaries must be added explicitly with operator approval through `4dt-sources`.
9. Agents must not read or write board storage directly. Use `4dt-board` for listing, reading sections, creating items, moving items, setting metadata, adding timeline entries, and validation.
10. Agents must not read or write wiki storage directly. Use `4dt-wiki` for wiki pages and `4dt-sources` for the source registry and source inventory.
11. Developer, quality, release, product, analytic, wiki, and handoff reports are task timeline entries managed by `4dt-board`, not standalone report files.
12. Ask the operator to confirm scoped auto mode for `lead -> product`, `product -> analytic`, `analytic -> developer`, and `quality -> wiki` transitions unless the exact transition is already approved for the current scope.
13. Create an epic handoff timeline entry before closing a completed epic or starting the next epic as the active implementation focus.
14. DevOps server documentation belongs in the single workspace wiki managed by `4dt-wiki`; DevOps keys are looked up only in workspace-root `keys/`.
15. Release commits require accepted quality or product acceptance, a visible commit plan, and explicit user approval before staging or committing.
16. The old multi-project wiki registry, source-map workflow, generated source inventory files, and standalone report files are legacy. Do not migrate or preserve them; create current artifacts through the tools.
17. When a current `4dt-wiki` or `4dt-sources` index exists, use tool search/get commands before broad wiki or approved-source reading.
18. At the start of a new session, run startup checks and load contract memory defaults for project rules, operator preferences, active modes, and workflow constraints when memory is ready. Ask onboarding questions only when defaults are incomplete or invalid.
19. Report created and changed files at the end.
