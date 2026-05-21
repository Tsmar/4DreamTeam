# Lead Read-Only Workflows

Use this file for direct project questions, workspace status, continuation, and workspace validation.

## Project Questions

Use this read-only workflow when the user asks a direct question about an existing project and does not request a task, implementation, wiki update, audit, or validation.

If the question may depend on prior session context, user preferences, or previous decisions, first read `references/lead/memory.md`. Use `agentmemory` only when it is available and likely to help; otherwise continue with the local wiki and workspace artifacts. Memory recalls do not override current wiki, task, report, or approved source evidence.

Start with the smallest relevant part of the project documentation:

1. `docs/index.md` only if the project wiki must be identified.
2. If the question is broad and `docs/<project-name>/.index/source-map.json` exists and is current, use index-first navigation to find the relevant semantic groups.
3. The specific `docs/<project-name>/` pages that are likely to answer the question.
4. `docs/<project-name>/sources.md` only if source boundaries may be needed.

Do not perform a broad documentation audit or inspect approved sources by default.

Inspect approved source paths only if:

1. the relevant documentation is missing, incomplete, contradictory, or stale;
2. the question requires implementation-level confirmation;
3. the answer depends on behavior that documentation marks as `unknown` or `requires source access`;
4. the user explicitly asks to verify the answer from sources.

If source inspection is needed but the approved source boundary is missing or insufficient, stop and ask for access to the exact path needed.

Do not read the whole project wiki or broad source tree for project questions when index-first navigation can narrow the scope.

## Status And Continuation

Use this read-only workflow when the user asks for workspace status, asks what is next, or asks to continue without naming a specific task.

For continuation across sessions, read `references/lead/memory.md` and optionally recall prior context from `agentmemory` when available. If memory is unavailable, slow, empty, or low-signal, use the workspace board, reports, and wiki fallback without stopping.

Read only the current 4DreamTeam workspace:

1. `AGENTS.md`
2. `docs/index.md`
3. `docs/<project-name>/sources.md` files if present
4. `tasks/backlog/`
5. `tasks/analytic/`
6. `tasks/developer/`
7. `tasks/quality/`
8. `tasks/wiki/`
9. `tasks/release/`
10. `tasks/released/`
11. `tasks/done/`
12. `tasks/rejected/`
13. `reports/product/`
14. `reports/tasks/`
15. `reports/quality/accepted/`
16. `reports/quality/rejected/`
17. `reports/release/`
18. `reports/handoffs/`

Do not use project source-map search for plain workspace status unless a project-specific deep dive is needed.

Report:

1. workspace preflight result;
2. role board summary: backlog, analytic, developer, quality, wiki, release, released, done, and rejected;
3. epics and tasks grouped by current owner role;
4. developer reports, quality reports, and release plans;
5. epic handoffs and completed epics missing a handoff;
6. rejected, blocked, or incomplete work;
7. known project wikis and missing `sources.md`;
8. the single recommended next action, or a short ordered list if multiple actions are equally important.

Do not change files during status or continuation unless the user explicitly approves the next lifecycle step.

If the next action is obvious:

1. `tasks/rejected/` -> explain rejection and offer developer correction;
2. `tasks/developer/` -> ask for approval to start or continue developer -> quality;
3. `tasks/quality/` -> run quality if the user approves or execution mode allows it;
4. `tasks/wiki/` -> ask for approval before wiki in controlled mode;
5. `tasks/release/` -> prepare release plan if the user approves;
6. epic ready for analysis -> ask for approval to hand its tasks off to analytic or developer;
7. completed epic without a handoff -> recommend creating the epic handoff before starting the next epic;
8. no active work -> suggest product intake, direct task intake, wiki bootstrap, devops, or release based on the user's goal.

## Workspace Validation

Use this read-only workflow when the user asks to validate, check, audit, or inspect the workspace structure itself.

Check:

1. required workspace files and directories exist:
   - `AGENTS.md`
   - `docs/index.md`
   - `tasks/backlog/`
   - `tasks/analytic/`
   - `tasks/developer/`
   - `tasks/quality/`
   - `tasks/wiki/`
   - `tasks/release/`
   - `tasks/released/`
   - `tasks/done/`
   - `tasks/rejected/`
   - `reports/product/`
   - `reports/tasks/`
   - `reports/quality/accepted/`
   - `reports/quality/rejected/`
   - `reports/release/`
   - `reports/handoffs/`
2. task/report consistency:
   - tasks in `tasks/quality/`, `tasks/wiki/`, `tasks/release/`, `tasks/released/`, and `tasks/done/` have developer reports unless the task is documentation-only and explicitly explains why;
   - tasks in `tasks/wiki/`, `tasks/release/`, `tasks/released/`, and `tasks/done/` have accepted quality reports when quality has run;
   - tasks in `tasks/released/` have a release report with pushed release evidence;
   - rejected tasks have rejected quality reports with actionable reasons;
   - reports are not orphaned from tasks or epics;
   - completed epics have `reports/handoffs/EPIC-XXXX-handoff.md`;
3. wiki consistency:
   - each `docs/<project-name>/` has `sources.md`;
   - managed wiki pages include status and expected `wiki-meta` where required by wiki rules;
   - obvious statuses are valid: `proposed`, `actual`, `accepted`, `superseded`, `deprecated`, or `unknown`;
4. lifecycle risks:
   - tasks stuck in a role column without a next action;
   - rejected work without a next action;
   - epics with blocking questions;
   - accepted work queued for release without explicit user request;
   - docs that appear to require post-acceptance updates before accepted quality exists.

Return findings by severity and include a recommended repair plan. Do not repair files unless the user explicitly approves the specific changes.
