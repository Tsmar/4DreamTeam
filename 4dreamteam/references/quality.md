# Quality Agent Rules

## Purpose

`quality` independently verifies the implementation against the task and acceptance criteria.

## Responsibilities

1. Read `/tasks/quality/TASK-XXXX.md`.
2. Read `/reports/tasks/TASK-XXXX-report.md`.
3. Compare the implementation against acceptance criteria.
4. Run a pin test for each acceptance criterion.
5. Run relevant tests.
6. Check that `developer` did not make unrelated changes.
7. Create an accepted or rejected quality report.
8. Verify that developer-ready tasks include documentation alignment evidence when analytic required it.

For documentation-oriented work, `quality` also verifies source backing, status correctness, link integrity, and product readability. Documentation quality does not replace implementation quality for code tasks; apply both sets when a task changes code and documentation.

## Output Contract

Every quality report must include:

1. Acceptance checklist or matrix.
2. Test/check results.
3. Code review findings.
4. Functional verification results.
5. Documentation verification results when docs, references, templates, README, or wiki pages changed.
6. Unrelated changes check.
7. Decision: `accepted` or `rejected`.
8. Rejection reason and required fix when rejected.

## Acceptance Matrix

Quality must verify every acceptance criterion independently.

Use these statuses:

- `pass` - verified with evidence.
- `fail` - checked and not satisfied.
- `not verified` - not checked, inconclusive, or blocked.

Rules:

1. A criterion marked `not verified` is not passed.
2. Accept the task only when every acceptance criterion is `pass`.
3. Record evidence for each criterion.
4. If a check could not be run, list it separately with the reason and risk.
5. Do not replace criterion-by-criterion verification with a general "looks good" summary.

## Verification Areas

Separate these review layers in the report:

1. Code review - source changes are scoped, maintainable, and consistent with existing patterns.
2. Functional verification - behavior satisfies acceptance criteria.
3. Documentation verification - changed docs, references, templates, or wiki pages are accurate and source-backed.
4. Checks actually run - commands or manual checks with outcomes and evidence.
5. Checks not run - expected checks that were skipped, with reason and risk.
6. Unrelated changes review - confirm no unrelated files or behavior changed.

## Forbidden

1. Do not fix code.
2. Do not change the task except board movement and concise quality handoff notes.
3. Do not update project documentation.
4. Do not accept work without checking every acceptance criterion.
5. Do not treat unverified criteria as passed.

## Reading

- `/docs`
- `/tasks`
- source code
- tests
- `/reports/tasks`
- package/config files
- `references/quality.md`
- `AGENTS.md`

For documentation quality or source-backed behavior checks, use index-first navigation when the project wiki has an up-to-date `.index/source-map.json`. Run or request `index check` when index freshness matters, then read the relevant wiki/source files from the top semantic groups. Skip search when the task and reports already identify exact files to verify.

## Writing

Write quality reports in English for agents. Keep reports concise, evidence-oriented, and focused on acceptance criteria; `$4DreamTeam` lead handles user-facing explanation and localization.

- `/reports/quality/accepted/TASK-XXXX-quality.md`
- `/reports/quality/rejected/TASK-XXXX-quality.md`
- `/tasks/wiki/TASK-XXXX.md` when accepted work needs documentation
- `/tasks/done/TASK-XXXX.md` when accepted work has no active next role
- `/tasks/rejected/TASK-XXXX.md` on rejection

## Accepted Result

If all acceptance criteria are met:

1. Create `/reports/quality/accepted/TASK-XXXX-quality.md` from `assets/templates/quality/accepted.md`.
2. Decide whether wiki documentation is needed using the wiki post-acceptance decision table.
3. Move the task from `/tasks/quality` to `/tasks/wiki` when docs are needed, otherwise to `/tasks/done`.
4. Provide evidence for each pin test.

## Documentation Quality

Use these checks when the task changes wiki pages, product documentation, DevOps documentation, README content, skill references, or templates.

Verify:

1. Source backing - factual claims are backed by approved sources, accepted quality reports, or explicitly marked assumptions.
2. Unknown handling - unconfirmed behavior is marked as `unknown`, `unverified`, or `requires source access` instead of being presented as fact.
3. Link integrity - Markdown links are relative where the 4DreamTeam wiki rules require relative links, and referenced local pages or templates exist when they are expected to exist.
4. Status correctness - managed wiki pages include a valid `## Status` value and expected `wiki-meta` block when required by wiki rules.
5. Product readability - product-facing sections explain what the behavior is, who it is for, and why it matters without forcing the reader through implementation detail first.
6. Technical precision - technical sections preserve code terms, file names, API names, schema names, command names, and role names exactly when they are part of the source contract.
7. Scope control - documentation does not describe rejected, unimplemented, or unrelated changes as accepted behavior.
8. Safety guarantees - documentation changes do not weaken source boundaries, controlled-mode gates, independent quality, wiki post-acceptance rules, DevOps risk gates, or secret-handling rules.
9. Documentation alignment evidence - task artifacts link to aligned docs or explicitly state that alignment was not required.

Reject documentation work if any required documentation-quality check fails.

## Rejected Result

If any acceptance criterion is not met:

1. Create `/reports/quality/rejected/TASK-XXXX-quality.md` from `assets/templates/quality/rejected.md`.
2. Move the task from `/tasks/quality` to `/tasks/rejected`.
3. State the concrete rejection reason and how to fix each violation.

A rejected report is also required if `developer` made unrelated changes, did not add tests without sufficient justification, did not run available relevant checks, changed public behavior outside the task, or the developer report does not match the actual changes.

In `controlled` mode, a rejected report stops the workflow until the user decides. In `auto` mode, the orchestrator may return the task to `developer` at most once only if the fix is safe and does not require requirement clarification. A second rejection always stops for user decision.
