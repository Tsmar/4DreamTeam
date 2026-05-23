---
id: flows-readme-maintenance
kind: flow
title: README Maintenance Flow
status: actual
created_at: 2026-05-23T07:31:59Z
updated_at: 2026-05-23T07:36:36Z
owner: wiki
source_refs: ["sources/4DreamTeam/README.md", "sources/4DreamTeam/README.ru.md", "sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/4dreamteam/references/marketing.md", "sources/4DreamTeam/4dreamteam/assets/templates/marketing/readme-positioning-review.md", "sources/4DreamTeam/4dreamteam/references/release.md"]
task_refs: []
---

# README Maintenance Flow

## Summary


README maintenance keeps the public promise, examples, commands, documentation map, safety claims, localized README, and release history aligned with confirmed source behavior.

## Content


Start README work by identifying whether the change is product positioning, feature documentation, installation guidance, usage examples, safety claims, or release/version status. The README is public-facing, so it should explain what 4DreamTeam is, who it helps, why files matter, and how to try it before exposing deep internals.

Claims must be source-backed. Marketing/reference rules require confirmed sources and claim audits before public claims appear in README, landing pages, release notes, pitch decks, case studies, or launch copy. Unsupported metrics, customers, benchmarks, security claims, certifications, and roadmap commitments must be excluded.

The English README is the source-facing public document. `README.ru.md` is allowed as a localized translation, but source-of-truth skill instructions and templates remain English. When changing README structure or claims, check whether the Russian README now needs synchronization; do not introduce Russian text into English source docs or templates.

When README changes affect skill behavior, metadata, templates, references, or user-facing documentation, release rules classify the change as belonging in the skill-development source history. Before commit/release packaging, update `CHANGELOG.md` when the source changelog policy applies and show an exact staging plan.

A practical README review sequence: read `README.md`; compare claims against `SKILL.md`, role references, docs, and templates; use the README positioning review template when the task is market-facing; update localized README if required; run documentation quality checks; include source-backed evidence in the handoff.

## Evidence


- `sources/4DreamTeam/README.md` is the English public entrypoint.
- `sources/4DreamTeam/README.ru.md` is the localized Russian README.
- `sources/4DreamTeam/AGENTS.md` defines the English source documentation policy and localized README exception.
- `sources/4DreamTeam/4dreamteam/assets/templates/marketing/readme-positioning-review.md` is the dedicated README positioning review template.
- `sources/4DreamTeam/4dreamteam/references/release.md` defines source changelog expectations for skill-development projects.

## Decisions


- Treat README work as public documentation plus positioning, not as the sole behavior contract.
- Keep behavioral rules in references and update README only with confirmed claims.
- Review localized README drift whenever English README claims or structure change.

## Open Questions


- The repository does not yet define an automatic synchronization policy for localized README files.
- It may be useful to add a dedicated README maintenance checklist to public docs or templates.

## Related


- [Documentation Domain](../domains/documentation.md)
- [Product Overview](../product/overview.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Task Lifecycle Flow](task-lifecycle.md)
