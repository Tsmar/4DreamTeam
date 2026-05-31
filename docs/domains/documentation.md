---
id: domains-documentation
kind: domain
title: Documentation Domain
status: actual
created_at: 2026-05-23T07:31:56Z
updated_at: 2026-05-25T05:35:56Z
owner: wiki
source_refs: ["sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/README.md", "sources/4DreamTeam/README.ru.md", "sources/4DreamTeam/CHANGELOG.md", "sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/wiki.md", "sources/4DreamTeam/4dreamteam/references/release.md"]
task_refs: ["TASK-0022"]
---

# Documentation Domain

## Summary




Documentation is split between public user-facing README files, localized README translation, source-of-truth skill instructions, generated workspace templates, source release history, exported English docs, and this managed agent wiki.

## Content





Repository documentation has a strict language policy. Source-of-truth skill instructions, templates, and repository rules stay English. Localized README translations such as README.ru.md may use Russian.

README.md is the main public entrypoint. README.ru.md tracks the same structure and claims for Russian readers. The README files point to docs/ as English documentation, include the direct Codex install prompt for the GitHub 4dreamteam folder, include the first new-workspace startup prompt, and include a short author thanks section about colleagues and friends who believe in 4DreamTeam and entrust real projects to a team of agents.

docs/ is exported from the managed wiki with 4dt-wiki export --target sources/4DreamTeam/docs and holds detailed source-backed pages such as workspace overview, product overview, task lifecycle, wiki workflow, workspace tools, source boundaries, memory, templates, and storage schema.

CHANGELOG.md records release history for the source repository. Managed wiki pages are the editable source for exported docs and are maintained through 4dt-wiki.

## Evidence





- sources/4DreamTeam/README.md documents Wake Context, the direct install prompt, the first startup prompt, English docs location, thanks, and version 0.5.6.
- sources/4DreamTeam/README.ru.md is the Russian localized README with matching structure and claims, including the operator-provided thanks text.
- sources/4DreamTeam/CHANGELOG.md includes the 0.5.6 release entry.
- sources/4DreamTeam/4dreamteam/SKILL.md carries skill metadata version 0.5.6.
- sources/4DreamTeam/4dreamteam/references/wiki.md defines managed wiki modes and rules.
- sources/4DreamTeam/4dreamteam/references/release.md defines release documentation and changelog policy.
- TASK-0035 contains accepted quality evidence for the wiki write safety, legacy cleanup, README version, and changelog update.

## Decisions





- Keep README.md as public-facing orientation, not a full internal manual.
- Point README readers to docs/ as English documentation without describing the README as a landing page.
- Keep behavior contracts in SKILL.md and references/, not only in README or templates.
- Keep README.ru.md synchronized with README.md for public claims and release status.
- Use managed wiki as the editable source for exported docs and export it before release packaging when docs/ should reflect current behavior.

## Open Questions




- Whether README.ru.md should be synchronized immediately after every English README change or only before release.

## Related




- [README Maintenance Flow](../flows/readme-maintenance.md)
- [Agent Instructions Contract](../contracts/agent-instructions.md)
- [Templates Domain](templates.md)
- [Changelog](../changelog.md)
