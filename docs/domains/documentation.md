---
id: domains-documentation
kind: domain
title: Documentation Domain
status: actual
created_at: 2026-05-23T07:31:56Z
updated_at: 2026-05-23T08:42:31Z
owner: wiki
source_refs: ["sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/README.md", "sources/4DreamTeam/README.ru.md", "sources/4DreamTeam/CHANGELOG.md", "sources/4DreamTeam/4dreamteam/references/wiki.md", "sources/4DreamTeam/4dreamteam/references/release.md"]
task_refs: []
---

# Documentation Domain

## Summary


Documentation is split between public user-facing docs, localized README translations, source-of-truth skill instructions, generated/workspace templates, changelog history, and this managed agent wiki.

## Content



Repository documentation has a strict language policy. `AGENTS.md` states that Markdown documentation and templates in the source repository must be English, except localized README translations such as `README.ru.md`. Source-of-truth skill instructions, templates, and repository rules stay English.

`README.md` is the main public entrypoint and landing page. It explains the product promise in simple language, shows real situations, gives quick-start prompts, points to exported documentation, and keeps safety guarantees understandable for people who are not trying to learn the internal architecture first.

`README.ru.md` is a localized user-facing translation. It can use Russian because it is explicitly named as a localized README, but it should track the structure and claims of the English README and avoid becoming the source of truth for behavior.

`docs/` is exported from the managed wiki with `4dt-wiki export --target sources/4DreamTeam/docs`. It holds detailed source-backed pages such as workspace overview, product overview, task lifecycle, wiki workflow, workspace tools, source boundaries, memory, templates, and storage schema. The exported docs are release documentation, not the place to maintain separate hand-written copies of the same knowledge.

`CHANGELOG.md` records release history for the source repository. Release rules require source changelog updates for skill-development projects when accepted changes affect skill behavior, metadata, templates, references, or user-facing documentation.

Managed wiki pages are the editable source for exported docs. They are maintained through `4dt-wiki`, backed by accepted evidence and approved source references, and can be exported into the source tree before release packaging.

## Evidence



- `sources/4DreamTeam/AGENTS.md` defines workspace instructions.
- `sources/4DreamTeam/README.md` is the product landing page.
- `sources/4DreamTeam/README.ru.md` is the Russian README.
- `sources/4DreamTeam/CHANGELOG.md` is source release history.
- `sources/4DreamTeam/4dreamteam/references/wiki.md` defines managed wiki modes and rules.
- `sources/4DreamTeam/4dreamteam/references/release.md` defines release documentation and changelog policy.

## Decisions


- Keep `README.md` as product-facing orientation, not a full internal manual.
- Keep behavior contracts in `SKILL.md` and `references/`, not only in README or templates.
- Use this wiki for agent continuation and source-backed navigation, not for public marketing copy.

## Open Questions


- Whether `README.ru.md` should be synchronized immediately after every English README change or only before release.
- Whether public docs should link to this managed wiki; current model treats managed wiki as workspace-internal.

## Related


- [README Maintenance Flow](../flows/readme-maintenance.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Templates Domain](templates.md)
- [Changelog](../changelog.md)
