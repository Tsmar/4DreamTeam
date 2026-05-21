# Lead Context Budget Policy

Use this file when a route may require broad reading, unfamiliar source inspection, large files, or long-running state. The goal is to preserve enough context to act correctly without loading the whole workspace, skill, wiki, or source tree.

This policy does not replace safety, source-boundary, quality, wiki, release, or DevOps gates. If another lead or role file requires stricter handling, use the stricter rule.

## Core Rule

Spend context only after the route justifies it:

1. Start from the compact entrypoint: `references/lead.md`.
2. Choose the route before loading role details.
3. Load only the smallest detailed module, role reference, task, report, wiki page, source-map entry, or source file needed for the next decision.
4. Expand context in stages only when the current evidence is insufficient.
5. Externalize important state into task, report, wiki, or release artifacts when it must survive beyond the current turn.

## Route-First Loading

Do:

- Read `references/lead.md` first.
- Read `references/lead/routing.md` before role references when the route is unclear.
- Load exactly one role reference first when the route is clear.
- Add detailed lead modules only when their gate applies.
- Prefer existing task, report, wiki, and source-map pointers over broad board or directory scans.

Do not:

- Load every role reference by default.
- Read all lead modules before deciding the route.
- Read broad docs or source trees when the user named an exact artifact.
- Treat installed skill files as source of truth during self-improvement when an approved source repository is available.

## Pointer Over Payload

Prefer durable pointers over copied content:

- Link or name exact files, headings, task IDs, report IDs, wiki pages, source-map entries, commands, and check results.
- Summarize only the decision-relevant parts of long artifacts.
- Preserve large evidence in the originating artifact instead of pasting it into new tasks or responses.
- In user-facing responses, report paths and outcomes rather than long internal artifacts.

Use direct content only when the exact text is needed to decide, patch, review, or verify the current step.

## Staged Expansion

For large files, generated indexes, docs trees, task boards, or approved source areas:

1. Search first with exact identifiers, headings, symbols, or route terms.
2. Read the nearest relevant range.
3. Expand to neighboring sections only when dependencies or contradictions are visible.
4. Read whole files only when the file is short, the entire contract matters, or partial reading would risk missing a gate.
5. Read whole directories only when a route explicitly requires an inventory or validation.

If a local wiki index is current, use index-first navigation before broad wiki or approved-source reading.

## Artifact Handoff

Externalize state when:

- work will continue across roles, turns, or sessions;
- acceptance criteria, assumptions, decisions, blockers, or validation evidence matter later;
- context is growing because multiple files or roles interact;
- quality, wiki, release, or product acceptance must review the result;
- the user says the current work is part of a larger release or roadmap.

Use the narrowest durable artifact:

- `tasks/backlog/EPIC-XXXX.md` for product scope and task candidates;
- `tasks/analytic/TASK-XXXX.md` for unresolved technical discovery;
- `tasks/developer/TASK-XXXX.md` for implementation-ready work;
- `reports/tasks/TASK-XXXX-report.md` for developer evidence;
- `reports/quality/accepted/` or `reports/quality/rejected/` for independent review;
- `reports/release/` for accepted release packaging;
- managed wiki pages only through the wiki route and its gates.

## Budget Escalation Triggers

Expand context deliberately when any of these are present:

- route selection is ambiguous;
- acceptance criteria, source boundaries, or approval gates are unclear;
- instructions appear to conflict;
- a safety, secret-handling, DevOps, git, release, or destructive-action gate may apply;
- a quality review must verify behavior against task requirements;
- a wiki route must confirm source maps, managed docs, or source-backed claims;
- a self-improvement task involves skill behavior, routing, lifecycle, safety, templates, or output contracts;
- user-visible or release-facing wording depends on source-backed evidence.

Record the reason for the expansion in the relevant task, report, or final response when it affects the result.

## Bulk-Load Guardrails

Do not bulk-load:

- every role reference;
- the whole `references/` tree;
- full task boards;
- full report trees;
- full wiki trees;
- generated `.index/*` files;
- approved source repositories;
- dependency directories, build outputs, logs, dumps, or unrelated files.

Bulk reading is allowed only for route-specific inventory, validation, release packaging, wiki indexing, or source-map work where the workflow requires it. Even then, prefer file lists, search results, indexes, and summaries before full content.

## User Communication

When the budget policy affects execution, explain it briefly:

- say what context is being loaded and why;
- name when a broader read is intentionally avoided;
- report durable artifacts created or changed;
- ask a blocking question only when route, source access, safety, acceptance, or release scope cannot be safely inferred.
