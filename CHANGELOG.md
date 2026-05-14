# Changelog

## 0.0.11 - 2026-05-14

- Added `tasks/released` as the terminal board column for tasks included in pushed releases.
- Defined the release flow as `done -> release -> released`, with `tasks/release` as the active release queue.
- Expanded release rules and templates to cover branch push, tag push, and optional GitHub Release creation or publication with separate approval gates.
- Required released tasks to have release reports with pushed release evidence.
- Bumped the skill version to `0.0.11`.

## 0.0.10 - 2026-05-14

- Replaced the `tasks/product` board column with `tasks/backlog` for epics and backlog planning.
- Made `EPIC-XXXX` and `TASK-XXXX` the only board entities: epics contain task rows, and executable work is represented only by tasks.
- Added explicit epic statuses for shaping, handoff readiness, delivery, blocked, done, and rejected states.
- Replaced the product brief template with an epic template and updated product, analytic, lead, marketing, release, workspace, and README references.
- Bumped the skill version to `0.0.10`.

## 0.0.9 - 2026-05-14

- Removed all legacy task column references for `tasks/pending` and `tasks/in-progress` from skill rules, workspace templates, and README documentation.
- Kept the role-based task board as the only documented workspace task structure.
- Bumped the skill version to `0.0.9`.

## 0.0.8 - 2026-05-14

- Reworked task flow around a role-based virtual Kanban board: `product`, `analytic`, `developer`, `quality`, `wiki`, `release`, `done`, and `rejected`.
- Added legacy compatibility for `tasks/pending` and `tasks/in-progress` without automatic migration during status, validation, or self-update.
- Added clear routing for direct engineering tasks, small safe task fast path, compact analytic tasks, and explicit release-only behavior.
- Added a centralized human-in-the-loop gate map covering workspace bootstrap, product, analytic, quality rejection, wiki, devops, release, self-update, and safety approvals.
- Optimized internal task, product, developer, quality, and release templates for concise English agent-first artifacts.
- Updated workspace template and README documentation to describe the role board and legacy task columns.
- Bumped the skill version to `0.0.8`.

## 0.0.7 - 2026-05-14

- Made managed wiki documentation English-only for agent efficiency and consistency.
- Updated wiki bootstrap, blueprint, and deepening rules so knowledge base language is no longer a user-selected parameter.
- Added guidance to translate or summarize non-English inputs and migrate touched mixed-language wiki pages to English.
- Bumped the skill version to `0.0.7`.

## 0.0.6 - 2026-05-14

- Improved the self-update workflow to show a concise AGENTS.md change summary or diff before writing.
- Added installed skill version reporting for workspace self-update preflight and completion messages.
- Required self-update completion to report the source template path and target workspace rules file.
- Bumped the skill version to `0.0.6`.

## 0.0.5 - 2026-05-14

- Added Index-First Navigation rules requiring local wiki search before broad project wiki/source reading when a current source-map index exists.
- Added skip conditions for exact file/page tasks, precise approved source scope, workspace status, missing/stale indexes, and pre-bootstrap wikis.
- Added rebuild/check requirements after `source-map.md` changes.
- Added concise index-first reading rules to lead, product, analytic, developer, quality, and devops references.
- Preserved source boundary safety: search results do not grant access outside approved source roots.
- Bumped the skill version to `0.0.5`.

## 0.0.4 - 2026-05-14

- Added a structured source map standard for managed wikis with source roots, areas, semantic groups, primary/supporting files, related wiki pages, and update triggers.
- Added Bun/TypeScript wiki tooling at `skill/tools/wiki.ts` for local `index build`, `index check`, and `search` commands.
- Added generated `.index/source-map.json` and `.index/manifest.json` rules as derived artifacts from `source-map.md`.
- Updated wiki bootstrap, deepening, sync, and check rules to maintain source maps and local indexes.
- Updated the source map template to represent semantic navigation instead of source boundary policy.
- Bumped the skill version to `0.0.4`.

## 0.0.3 - 2026-05-14

- Added the `release` role for packaging accepted work into changelog entries, commit plans, and approved git commits.
- Added release routing in the lead rules for accepted work, changelog, branch, staging, and commit requests.
- Added release rules covering workspace changelogs, source changelog policy, skill-development changelog requirements, commit plan gates, and git safety boundaries.
- Added a release plan template at `skill/assets/templates/release/plan.md`.
- Updated README documentation to include the `release` role and accepted-work packaging flow.
- Bumped the skill version to `0.0.3`.

## 0.0.2 - 2026-05-13

- Added a project-question workflow for the lead role: answer direct project questions from the smallest relevant documentation set first, and inspect approved sources only when documentation is insufficient or verification is explicitly needed.
- Simplified the self-improvement lifecycle from `product -> analytic -> developer -> quality` to `product -> developer -> wiki -> product acceptance`.
- Defined the only required self-improvement human-in-the-loop gate as the approval point between `product` and `developer`, where the human decides the exact developer task scope.
- Updated README self-improvement documentation to match the new lifecycle.
- Added the repository rule that skill behavior, metadata, template, reference, or user-facing documentation changes must update the skill version before commit.
- Bumped the skill version to `0.0.2`.
