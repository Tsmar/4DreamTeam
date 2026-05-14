# Changelog

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
