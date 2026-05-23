# Lead Read-Only Workflows

Use this file for direct project questions, workspace status, continuation, and workspace validation.

## Project Questions

Use this workflow when the user asks a direct question about an existing project and does not request a task, implementation, wiki update, audit, or validation.

If the question may depend on prior session context, user preferences, or previous decisions, first read `references/lead/memory.md`. Use `4dt-memory` when it is available and likely to help; otherwise continue with the script-managed wiki, board, source registry, and current workspace evidence.

Start with the smallest script query:

1. `4dt-wiki search` or `4dt-wiki get` for existing wiki knowledge.
2. `4dt-sources registry list` and `4dt-sources search/get` when source boundaries or source snippets are needed.
3. `4dt-board get`, `4dt-board section get`, or `4dt-board comments list` when task history matters.
4. `4dt-memory search` when prior session memory may contain useful accepted context.

Do not perform a broad documentation audit or inspect approved sources by default.

Inspect approved source paths only if:

1. the relevant documentation is missing, incomplete, contradictory, or stale;
2. the question requires implementation-level confirmation;
3. the answer depends on behavior that documentation marks as `unknown` or `requires source access`;
4. the user explicitly asks to verify the answer from sources.

If source inspection is needed but the approved source boundary is missing or insufficient, stop and ask for access to the exact path needed.

## Status And Continuation

Use this workflow when the user asks for workspace status, asks what is next, or asks to continue without naming a specific task.

For continuation across sessions, read `references/lead/memory.md` and optionally recall prior context from `4dt-memory`. If memory is unavailable, slow, empty, or low-signal, use `4dt-board`, `4dt-wiki`, and `4dt-sources` without stopping.

Run:

1. `4dt-board status`
2. `4dt-board list`
3. `4dt-board validate`
4. `4dt-wiki status`
5. `4dt-wiki validate`
6. `4dt-sources registry list`
7. `4dt-sources index check`
8. `4dt-memory doctor`

Report:

1. workspace preflight result;
2. role board summary by current column;
3. epics and tasks grouped by current owner role;
4. timeline evidence relevant to developer, quality, release, wiki, and handoff decisions;
5. rejected, blocked, or incomplete work;
6. known wiki status and source registry state;
7. the single recommended next action, or a short ordered list if multiple actions are equally important.

Do not change files during status or continuation unless the user explicitly approves the next lifecycle step.

If the next action is obvious, use the task column reported by `4dt-board`:

1. `rejected` -> explain rejection and offer developer correction;
2. `developer` -> ask for approval to start or continue developer -> quality;
3. `quality` -> run quality if the user approves or execution mode allows it;
4. `wiki` -> ask for approval before wiki in controlled mode;
5. `release` -> prepare release plan if the user approves;
6. epic ready for analysis -> ask for approval to hand its tasks off to analytic or developer;
7. completed epic without a handoff timeline entry -> recommend creating the handoff before starting the next epic;
8. no active work -> suggest product intake, direct task intake, wiki bootstrap, devops, or release based on the user's goal.

## Workspace Validation

Use this workflow when the user asks to validate, check, audit, or inspect the workspace structure itself.

Run the validation tools and report findings by severity:

1. `4dt-board validate` checks board metadata, columns, timeline format, index compatibility, and unreadable task artifacts.
2. `4dt-wiki validate` checks single-workspace wiki metadata, stable sections, links, and removed registry files.
3. `4dt-sources registry validate` checks source registry shape and approved boundaries.
4. `4dt-sources index check` checks source inventory freshness.
5. `4dt-memory doctor` checks memory storage, LanceDB readiness, and fallback state.
6. `npm run rules` checks that agent-facing instructions have not regressed to legacy workflows.

Do not repair files unless the user explicitly approves the specific changes.
