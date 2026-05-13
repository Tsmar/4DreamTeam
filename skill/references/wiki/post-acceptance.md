# Wiki Mode: Post-Acceptance

Main mode for updating docs after an accepted quality report.

## Start Condition

Work only after an accepted quality report exists.

If an accepted quality report is missing, stop and do not change `docs/`, except for explicitly requested `audit`, `check`, `bootstrap`, `blueprint`, or `deepening` modes.

## Required Inputs

1. Accepted quality report.
2. Related task.
3. Developer report.
4. Existing documentation.

## Workflow

1. Read the accepted quality report.
2. Read the related task.
3. Read the developer report.
4. Read existing documentation.
5. Determine whether the implementation changed architecture, public APIs, domain model, workflow, project rules, important technical constraints, or system behavior.
6. If documentation is needed, update `docs/`.
7. For significant architecture decisions, create an ADR in `docs/<project-name>/decisions`.

Use this template for ADRs:

```txt
assets/templates/wiki/adr.md
```

## Write Scope

Allowed writes:

- `docs/`
- `docs/<project-name>/decisions/`

## When Docs Are Not Needed

If the accepted change does not change architecture, public APIs, domain model, workflow, project rules, technical constraints, or observable system behavior, state in the final response that a wiki update was not needed.

## Stop Conditions

Stop if:

1. There is no accepted quality report.
2. Accepted behavior is unclear.
3. Docs update would require describing unconfirmed changes.
4. An ADR is needed but the architecture decision is not recorded in the task or quality report.
