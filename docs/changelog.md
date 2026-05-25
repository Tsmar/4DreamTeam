---
id: changelog
kind: changelog
title: Changelog
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-25T05:34:15Z
owner: wiki
source_refs: ["sources/4DreamTeam/CHANGELOG.md", "sources/4DreamTeam/4dreamteam/references/release.md", "sources/4DreamTeam/README.md", "sources/4DreamTeam/README.ru.md", "sources/4DreamTeam/4dreamteam/SKILL.md"]
task_refs: ["EPIC-0001", "EPIC-0002-TASK-0014", "EPIC-0002-TASK-0015", "TASK-0021", "TASK-0022"]
---

# Changelog

## Summary



This workspace wiki changelog records notable managed-wiki changes for the 4DreamTeam skill workspace. Source release history remains in the repository `CHANGELOG.md`.

## Content






2026-05-25: Prepared 4DreamTeam v0.5.3 release packaging for Wake Context and public README updates. The release adds Wakeup Recall startup guidance, makes installed skill wrappers the default startup launcher, adds a short human/agent wakeup analogy to English and Russian README files, updates quick-start prompts with direct GitHub skill installation, and bumps skill metadata/documented version to 0.5.3.

2026-05-24: Prepared 4DreamTeam v0.5.0 release packaging for EPIC-0001 and accepted EPIC-0002 packaging work. The release adds the universal 4dt-search CLI across sources, wiki, board, and memory; replaces memory retrieval with the SQLite-authoritative search backend; moves CLI source packages into repository packages/; adds self-contained installed-skill runtime wrappers under 4dreamteam/scripts; adds local and GitHub Actions quality gates; and updates managed wiki/source docs for the new search, memory, package, and runtime contracts.

2026-05-23: Bootstrapped the managed workspace wiki for the 4DreamTeam skill source repository. The initial wiki covers product promise, architecture, runtime entrypoint, documentation and README maintenance, agent instruction contracts, workspace tools, lifecycle, wiki workflow, templates, memory, source boundaries, and tool storage schema.

2026-05-23: Updated managed wiki after accepted TASK-0001, TASK-0002, TASK-0003, and TASK-0004 work. The wiki now records .gitignore-aware 4dt-sources exclusions and safe get rejection for excluded paths, section-scoped 4dt-wiki reads/writes with page section-set and page apply, 4dt-wiki export --target <path> for source-shipped release documentation, the developer implementation-plan approval gate, and the mandatory post-quality wiki review step.

2026-05-23: Prepared 4DreamTeam v0.4.0 release packaging for TASK-0001 through TASK-0006. The release includes source exclusion safety, wiki section/apply/export workflows, workflow gate updates, README positioning, simple existing-project setup guidance, and exported source documentation.

This wiki changelog is not a replacement for the source repository changelog. Release rules distinguish workspace changelog entries from source CHANGELOG.md entries. Source changelog updates are required for accepted skill-development changes that affect behavior, metadata, templates, references, or user-facing documentation when release packaging is requested.

## Evidence






- sources/4DreamTeam/CHANGELOG.md is the source repository release history and includes 0.5.3.
- sources/4DreamTeam/4dreamteam/references/release.md defines workspace and source changelog policy, including wiki export before packaging when source-shipped docs are needed.
- README.md, README.ru.md, and 4dreamteam/SKILL.md carry the 0.5.3 public documentation and metadata changes.
- TASK-0021 and TASK-0022 contain accepted timeline evidence for Wake Context startup, README, version, validation, and release packaging.

## Decisions




- Use this page for workspace wiki history only.
- Keep source release history in the approved source repository changelog.
- Export managed wiki pages into docs/ before release packaging when README points users to docs/.

## Open Questions



- Whether future accepted wiki-only changes should create formal board timeline evidence before changelog entries.

## Related




- [Workspace Overview](overview.md)
- [Search Domain](domains/search.md)
- [Memory Domain](domains/memory.md)
- [Workspace Tools Contract](contracts/workspace-tools.md)
- [Task Lifecycle Flow](flows/task-lifecycle.md)
