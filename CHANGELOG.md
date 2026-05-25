# Changelog

## Unreleased

- No unreleased changes yet.

## 0.5.2 - 2026-05-25

- Added self-learning memory policy for operator memory-intent phrases, durable English memory, scope/type placement, and role-scoped recall.
- Added bounded startup/task recall guidance so agents apply contract defaults first and fetch only relevant memory previews/details.
- Added stale/conflicting memory handling and workflow-rule validation anchors/tests for the new memory guarantees.
- Refreshed exported memory documentation and README positioning for operator-guided self-learning.
- Bumped the skill metadata version to `0.5.2`.

## 0.5.1 - 2026-05-24

- Strengthened the workspace `AGENTS.md` template with startup orientation through memory defaults and managed workspace validation.
- Added explicit `4dt-search` discovery guidance for wiki, sources, board, and memory domains before broad reading.
- Bumped the skill metadata version to `0.5.1`.

## 0.5.0 - 2026-05-24

- Added `4dt-search` as the universal search CLI for `sources`, `wiki`, `board`, and `memory` domains, including persistent indexes, advanced query controls, validation coverage, and agent-facing usage guidance.
- Replaced `4dt-memory` retrieval with a SQLite-authoritative `4dt-search` backend and removed the previous vector-index implementation and references from active code and documentation.
- Moved CLI source packages and tests out of the installable skill package into repository-level `packages/` trees for board, wiki, sources, memory, and search.
- Added self-contained installed-skill runtime wrappers under `4dreamteam/scripts`, including the generated `4dt-tools.pyz` archive used when the skill is installed by copy or URL.
- Added local and GitHub Actions quality gates for tool tests, Python compilation, workflow rules, package structure, installed-runtime smoke checks, managed workspace validation, and search quality validation.
- Updated managed wiki exports and agent instructions for unified search, memory startup, source boundaries, package layout, installed runtime scripts, and workspace tool contracts.
- Cleaned README, instruction, and wiki wording so the installable package is consistently named `4dreamteam/` and normal workspaces do not imply a local skill-folder copy.
- Bumped the skill metadata version to `0.5.0`.

## 0.4.0 - 2026-05-23

- Added `.gitignore`-aware `4dt-sources` exclusions and shared index/get path policy so ignored or forbidden paths are omitted from source inventories and rejected before content reads.
- Added `4dt-wiki` section workflows, including `get --section`, `page section-set`, and `page apply` for section-scoped and atomic managed wiki updates.
- Added `4dt-wiki export --target <path>` to export managed wiki Markdown pages into an explicit `sources/` target for release documentation.
- Updated workflow rules so developer implementation plans are compared with the operator before patching, and accepted quality always routes through wiki review before done or release.
- Reworked `README.md` as a product landing page with simpler positioning, existing-project setup guidance, and exported docs links.
- Replaced hand-written `docs/` pages with documentation exported from the managed wiki.
- Updated release/rules validation for the exported docs structure and bumped affected tool package metadata for `fourdt-sources` and `fourdt-wiki`.

## 0.3.0 - 2026-05-23

- Added script-managed workspace tooling with `4dt-board`, `4dt-sources`, and `4dt-wiki` for board, source registry, and single-workspace wiki operations.
- Added 4DT Memory contract keys and startup defaults via `4dt-memory defaults load`, plus `keys`, `mode`, and onboarding repair commands.
- Updated new-session startup so ready memory defaults apply current project rules, operator preferences, active mode, git policy, and validation policy without asking the operator to repeat context.
- Added SQLite schema v2 for contract memory entries, migration coverage, safety checks, and audit entries for contract updates.
- Added an English-first agent memory search protocol for supplemental semantic recall, including bounded typed query variants and artifact verification guidance.
- Extended the retrieval-quality benchmark with a raw user query vs English-first agent protocol comparison without changing `4dt-memory search` runtime behavior.
- Moved managed runtime storage toward `.4dt`, updated workspace setup guidance, and strengthened rules that agents use scripts instead of reading or writing managed board/wiki storage directly.
- Bumped skill and memory package version metadata to `0.3.0`.

## 0.2.0 - 2026-05-22

- Added bundled local 4DT Memory tooling with `4dt-memory` CLI commands for SQLite-backed memory storage, safe `remember`/`forget`, search/reindex, JSONL import/export, session state, and benchmark harness output.
- Documented SQLite as the authoritative memory store and LanceDB as a rebuildable optional index with degraded lexical fallback.
- Replaced primary memory documentation with `docs/memory.md` and removed the legacy memory page.
- Updated lead memory policy to preserve source-of-truth order, source-boundary rules, no-secret save rules, preview-first search, and no-memory/degraded fallback behavior.
- Updated README and README.ru to describe optional local 4DT Memory instead of external memory tooling.
- Bumped skill and memory package version metadata to `0.2.0`.

## 0.1.8 - 2026-05-21

- Added a lead context budget policy for route-first loading, staged expansion, pointer-over-payload behavior, artifact handoff, and bulk-load guardrails.
- Added workspace `sources/` as a git-ignored local source staging boundary with first-touch operator confirmation before listing, statting, resolving, inventorying, indexing, or reading.
- Defined `framework user` as the product-meaning owner and `operator` as the above-workflow execution authority for source access, role transitions, scoped auto mode, writes, git, infrastructure, and publication.
- Added scoped auto-mode and major role-transition gates while preserving automatic `developer -> quality` after approved developer work.
- Added low-token source inventory support with `wiki_index.py sources build/check/search`, generated `.index/sources/*` manifests, symlink target recording, ignore/forbidden states, and lightweight path metadata fingerprints.
- Added a human-readable wiki `sources.md` template and clarified the split between source registries, raw generated source inventory, and semantic `source-map.md` navigation.
- Added required epic-completion handoffs under `reports/handoffs/EPIC-XXXX-handoff.md` plus a reusable `assets/templates/lead/epic-handoff.md` template.
- Updated README and skill metadata to document version `0.1.8`.

## 0.1.6 - 2026-05-20

- Added an analytic documentation-alignment gate before developer handoff when confirmed decisions would make managed docs stale or contradictory.
- Added pre-development wiki sync guidance for confirmed requirements using `proposed` status without weakening post-acceptance docs rules.
- Added DevOps server-card mirrors in `~/server-card`, including first-connection context recovery, server-local git history, automatic mirror updates after management approval, and secret-safe failure reporting.
- Added a DevOps pre-task server-card version check so server work starts from the server-side card when it is available.
- Corrected repository path documentation from obsolete package-folder and local-checkout examples to the actual `4dreamteam/` source layout and portable local-checkout wording.
- Added explicit skill installation instructions for the GitHub `4dreamteam` folder in README and workflow docs.
- Bumped the skill version to `0.1.6`.

## 0.1.5 - 2026-05-17

- Reworked the English and Russian README files into lighter product landing pages focused on real user situations, value, roles, quick start, and safety.
- Moved detailed English documentation into repository `docs/` pages for examples, workflows, workspace structure, wiki index behavior, `agentmemory`, and development notes.
- Documented the `agentmemory` and wiki fallback relationship in the README with results from a curated wiki-seeding benchmark.
- Clarified that `agentmemory` is optional, useful for continuity, and not a replacement for wiki, task, report, or approved-source verification.
- Bumped the skill version to `0.1.5`.

## 0.1.4 - 2026-05-17

- Added an optional lead memory policy for using `agentmemory` as a non-authoritative recall layer.
- Defined wiki/tasks/reports fallback behavior when `agentmemory` is unavailable, slow, empty, low-signal, or contradictory.
- Added safe memory save rules that prohibit secrets, credentials, `.env` contents, production data, large copied artifacts, and unaccepted speculation.
- Added a benchmark pattern for comparing wiki-only, memory-only, and memory-plus-wiki fallback workflows.
- Bumped the skill version to `0.1.4`.

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
- Added a release plan template at `4dreamteam/assets/templates/release/plan.md`.
- Updated README documentation to include the `release` role and accepted-work packaging flow.
- Bumped the skill version to `0.0.3`.

## 0.0.2 - 2026-05-13

- Added a project-question workflow for the lead role: answer direct project questions from the smallest relevant documentation set first, and inspect approved sources only when documentation is insufficient or verification is explicitly needed.
- Simplified the self-improvement lifecycle from `product -> analytic -> developer -> quality` to `product -> developer -> wiki -> product acceptance`.
- Defined the only required self-improvement human-in-the-loop gate as the approval point between `product` and `developer`, where the human decides the exact developer task scope.
- Updated README self-improvement documentation to match the new lifecycle.
- Added the repository rule that skill behavior, metadata, template, reference, or user-facing documentation changes must update the skill version before commit.
- Bumped the skill version to `0.0.2`.
