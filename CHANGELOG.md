# Changelog

## 0.1.3 - 2026-05-16

- Strengthened `marketing` into a GTM, positioning, value validation, release narrative, README positioning, and claim audit role.
- Added marketing templates for value review, README positioning review, release narrative, GTM brief, and claim audit.
- Expanded lead routing so marketing is used for value reviews, claim audits, release narratives, GTM/positioning, and user-facing release communication, while skipping purely internal work without user-facing impact.
- Clarified self-improvement rules so role, routing, template, lifecycle, safety, and output-contract changes must not bypass product, developer, and quality artifacts.
- Bumped the skill version to `0.1.3`.

## 0.1.2 - 2026-05-15

- Split the large lead reference into route-specific modules for preflight, routing, lifecycle, contracts, safety, read-only workflows, and self-maintenance.
- Split wiki shared rules into focused modules for source boundaries, page shape, source maps, and local indexing.
- Added reference-loading guidance so agents load the smallest sufficient rule set for each route.
- Added README guidance for reducing token and context usage when working with 4DreamTeam.
- Bumped the skill version to `0.1.2`.

## 0.1.1 - 2026-05-15

- Replaced the local wiki index/search tool with a dependency-free Python 3 standard-library script at `4dreamteam/scripts/wiki_index.py`.
- Removed the legacy TypeScript wiki tool.
- Updated wiki rules, README files, and package script to use the bundled Python wiki index script and direct `source-map.md` fallback when tooling is unavailable.
- Fixed wiki tooling path guidance so agents resolve the installed skill path instead of relying on a hardcoded repository path.
- Bumped the skill version to `0.1.1`.

## 0.1.0 - 2026-05-14

- Strengthened `analytic` with an implementation-ready gate, technical impact checklist, validation plan requirement, discovery separation, and blocking question rules.
- Added a `developer` execution protocol requiring a short implementation plan before patching, point-by-point saved changes, relevant checks, and scope discipline.
- Added a `quality` acceptance matrix with `pass`, `fail`, and `not verified` results, plus separated review areas and explicit skipped-check reporting.
- Added mandatory output contracts for all roles in the lead rules.
- Added a routing decision table, incomplete-context policy, approval gate taxonomy, and task lifecycle state machine.
- Simplified wiki mode selection with explicit entry conditions, write boundaries, and approval boundaries.
- Added framework-wide safety invariants for secrets, logs, infrastructure, and git; aligned DevOps and release rules with those invariants.
- Added role instruction quality criteria and explicit instruction-vs-template boundaries.
- Restored a self-improvement quality gate for safety, lifecycle, routing, approval gate, release/devops, source-boundary, role-output-contract, and workflow-template changes.
- Updated analytic, developer, and quality templates to support the stronger role contracts.
- Added end-to-end README examples for bugfix, feature, documentation update, and self-improvement workflows.
- Bumped the skill version to `0.1.0`.

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
- Added local wiki tooling for `index build`, `index check`, and `search` commands.
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
