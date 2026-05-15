# Lead Contracts

Use this file when creating role artifacts, reviewing role output, changing templates, or changing role instructions.

## Mandatory Output Contracts

Each role must produce at least the fields below in its main artifact or report. Role templates may add structure, but they do not replace this contract.

`product`:

- problem statement;
- target user;
- goals;
- non-goals;
- scope;
- acceptance criteria;
- open questions;
- next recommended role.

`analytic`:

- task summary;
- affected areas;
- technical impact checklist;
- implementation requirements;
- technical constraints;
- assumptions and open questions;
- acceptance criteria;
- validation plan;
- handoff to developer, product, or blocked state.

`developer`:

- implementation summary;
- files changed;
- decisions made;
- tests/checks run;
- tests/checks not run with reasons;
- known limitations;
- handoff to quality.

`quality`:

- acceptance checklist or matrix;
- test results;
- code review findings;
- functional verification findings;
- unrelated changes check;
- decision: accepted or rejected;
- rejection reason and required fix when rejected.

`wiki`:

- docs updated;
- source of truth used;
- links added or updated;
- stale or conflicting docs found;
- unresolved documentation gaps.

`release`:

- tasks included;
- changelog entries;
- files to stage;
- commit message;
- risk notes;
- approval requirement.

`devops`:

- requested operation;
- environment impact;
- risks;
- required approvals;
- rollback notes;
- commands proposed or executed.

`marketing`:

- target audience;
- message;
- claims used;
- unsupported claims excluded;
- final copy or artifact.

## Role Instruction Quality Checklist

When changing role instructions, verify that the changed role has:

1. clear responsibility;
2. clear boundaries and forbidden actions;
3. mandatory inputs;
4. mandatory outputs;
5. stop conditions;
6. approval gates;
7. safety constraints;
8. handoff rules;
9. failure behavior;
10. at least one example or template pointer when useful;
11. no avoidable role overlap;
12. no self-approval.

## Instruction And Template Boundary

Role instructions define behavior. Templates define artifact shape.

Rules:

1. Mandatory behavior must live in role instructions or shared lead rules.
2. Templates may add structure but cannot be the only place a required behavior is defined.
3. Role instructions must point to the templates they expect agents to use.
4. Minimum output contracts must be duplicated or referenced in instructions, not hidden only in templates.
5. Changing a template that affects behavior counts as a framework behavior change and requires quality review.
