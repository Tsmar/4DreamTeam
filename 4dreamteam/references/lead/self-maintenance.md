# Lead Self-Maintenance

Use this file for workspace self-update and 4DreamTeam skill self-improvement.

## Self-Update Workflow

Use this workflow when the user wants the current 4DreamTeam workspace to adopt the currently installed 4DreamTeam skill rules.

This is not the same as self-improvement:

- self-update updates only the current workspace rules file;
- self-improvement changes the skill source repository through the controlled self-improvement lifecycle.

Preflight:

1. Confirm the current folder is a 4DreamTeam workspace.
2. Confirm `assets/templates/workspace/AGENTS.md` is available from the installed skill.
3. Read the installed skill version from installed `SKILL.md` when available.
4. Explain that only `AGENTS.md` will be replaced.
5. Compare workspace-root `AGENTS.md` with the installed template and show a concise change summary before writing.
6. If a readable diff can be produced, show the diff or the most important changed sections.
7. Wait for explicit approval before writing.

Write scope:

```txt
AGENTS.md
```

Source:

```txt
assets/templates/workspace/AGENTS.md
```

Rules:

1. Replace only workspace-root `AGENTS.md`.
2. Do not change tool-managed storage, `keys/`, approved source repositories, or installed skill files.
3. Do not create task, report, wiki, or quality artifacts for self-update unless the user explicitly asks for an auditable lifecycle.
4. After replacing `AGENTS.md`, report the source template path, target path, and installed skill version when known.
5. Tell the user to restart Codex so the updated skill and workspace instructions are loaded in a clean session.
6. After restart, recommend `$4DreamTeam validate workspace` if the user wants to verify the workspace.

## Self-Improvement Workflow

Use this workflow when the user wants 4DreamTeam to improve the `4DreamTeam` skill itself from a 4DreamTeam workspace.

Required source boundary:

```txt
your local checkout of https://github.com/Tsmar/4DreamTeam, for example /Users/Tsmar/Projects/4DreamTeam
```

or another explicitly approved local path to the skill repository.

The skill repository is not a normal project workspace. It is the source for:

1. `4dreamteam/SKILL.md`
2. `4dreamteam/references/`
3. `4dreamteam/assets/templates/`
4. `4dreamteam/agents/openai.yaml`
5. `README.md`
6. repository `AGENTS.md`

When the approved source repository differs from the installed skill copy, use the approved source repository as the source of truth for self-improvement. The installed copy only describes what may currently be loaded by Codex.

Self-improvement follows this lifecycle by default:

```txt
product -> developer -> quality -> wiki when needed -> product acceptance -> release when the user wants a commit
```

Rules:

1. Use `product` to define the improvement goal, audience, scope, product acceptance criteria, and the exact developer task scope.
2. Stop after `product` and ask the framework user to approve product meaning and task scope, then ask the operator to approve the `product -> analytic` or `product -> developer` transition unless that exact transition is already approved.
3. Use `developer` to edit only approved skill source files within the approved task scope.
4. Use `quality` after `developer` for independent review before wiki, product acceptance, or release packaging.
5. Use `wiki` after accepted quality only if workspace knowledge base documentation needs to reflect the accepted skill behavior.
6. Use `product` after accepted quality and optional `wiki` to confirm that the resulting skill behavior matches what the product role wanted to see.
7. Use `release` after product acceptance only when the user asks to prepare or create a commit for the accepted change.
8. A lightweight self-improvement quality review is mandatory for any change to safety rules, lifecycle rules, role routing, approval gates, release behavior, DevOps behavior, source-boundary behavior, role output contracts, or templates used by implementation and quality workflows.
9. A narrowly scoped copyedit or typo fix may use product acceptance without a full quality report only when it does not affect behavior, templates, safety, routing, gates, source boundaries, or release/devops behavior.
10. Preserve source repository language policy. Markdown documentation and templates in the skill repository must remain in English unless repository rules change explicitly.
11. Do not weaken workspace preflight, source boundaries, controlled-mode gates, ordinary task quality gates, wiki gates, DevOps risk gates, or secret-handling rules.
12. Do not collapse self-improvement into ad-hoc direct edits. Changes to role behavior, routing, templates, lifecycle, safety, approval gates, source boundaries, release/devops behavior, or output contracts must have auditable workspace artifacts for product scope, developer implementation, and quality review.
13. If an agent accidentally edits the skill source before creating the required artifacts, stop further source edits, create the missing product/task/developer/quality artifacts with accurate timing notes, then run quality against the actual diff before reporting completion.

After receiving a high-level user task:

1. Read the root `AGENTS.md`.
2. Read `references/lead.md`.
3. Determine the route from `references/lead/routing.md`.
4. If this is a product workflow, run the `product` role.
5. If `product` created blocking questions, stop and ask the user.
6. In `controlled` mode, stop after the epic is created or updated and ask the user to approve whether its tasks go to `analytic`, `developer`, or remain in backlog.
7. If this is a task workflow or the epic tasks are approved for technical analysis, run `analytic`.
8. If `analytic` created blocking questions, stop and ask the user.
9. In `controlled` mode, stop after the task is created and ask the operator to approve `analytic -> developer` unless the user explicitly allowed the small safe task fast path or approved the task in advance.
10. If the task is approved, run `developer -> quality` without stopping between the roles.
11. If `quality` returns `rejected`, stop in `controlled` mode and show the user the rejection reason. In `auto` mode, return the task to `developer` at most once only if the fix is safe and does not require a user decision.
12. If `quality` returns `accepted`, use the wiki post-acceptance decision table to determine whether documentation is needed. Stop before `quality -> wiki` in `controlled` mode if documentation should be updated.
13. If `quality` returns `accepted`, run `wiki` if documentation needs to be updated and the execution mode allows it.
14. If the user requested product acceptance of the result or wiki, run `product` after `wiki`.
15. In the final response, report created and changed file paths.

Do not skip `quality`.

Do not run `wiki post-acceptance` before an accepted quality report exists. `audit`, `check`, `bootstrap`, `blueprint`, and `deepening` modes may run without an accepted quality report according to their mode-specific gates in `references/wiki/`.
