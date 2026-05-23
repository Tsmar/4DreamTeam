---
id: changelog
kind: changelog
title: Changelog
status: actual
created_at: 2026-05-23T07:31:46Z
updated_at: 2026-05-23T08:50:39Z
owner: wiki
source_refs: ["sources/4DreamTeam/CHANGELOG.md", "sources/4DreamTeam/4dreamteam/references/release.md"]
task_refs: []
---

# Changelog

## Summary


This workspace wiki changelog records notable managed-wiki changes for the 4DreamTeam skill workspace. Source release history remains in the repository `CHANGELOG.md`.

## Content




2026-05-23: Bootstrapped the managed workspace wiki for the 4DreamTeam skill source repository. The initial wiki covers product promise, architecture, runtime entrypoint, documentation and README maintenance, agent instruction contracts, workspace tools, lifecycle, wiki workflow, templates, memory, source boundaries, and tool storage schema.

2026-05-23: Updated managed wiki after accepted TASK-0001, TASK-0002, TASK-0003, and TASK-0004 work. The wiki now records `.gitignore`-aware `4dt-sources` exclusions and safe `get` rejection for excluded paths, section-scoped `4dt-wiki` reads/writes with `page section-set` and `page apply`, `4dt-wiki export --target <path>` for source-shipped release documentation, the developer implementation-plan approval gate, and the mandatory post-quality wiki review step.

2026-05-23: Prepared 4DreamTeam v0.4.0 release packaging for TASK-0001 through TASK-0006. The release includes source exclusion safety, wiki section/apply/export workflows, workflow gate updates, README landing-page positioning, simple existing-project setup guidance, and exported source documentation.

This wiki changelog is not a replacement for the source repository changelog. Release rules distinguish workspace changelog entries from source `CHANGELOG.md` entries. Source changelog updates are required for accepted skill-development changes that affect behavior, metadata, templates, references, or user-facing documentation when release packaging is requested.

## Evidence




- `sources/4DreamTeam/CHANGELOG.md` is the source repository release history.
- `sources/4DreamTeam/4dreamteam/references/release.md` defines workspace and source changelog policy, including wiki export before packaging when source-shipped docs are needed.
- This managed wiki was created and updated through `4dt-wiki init`, `page create`, `page section-set`, and `page apply`.
- TASK-0001, TASK-0002, TASK-0003, TASK-0004, and TASK-0005 contain timeline evidence for recent wiki and README updates.

## Decisions


- Use this page for workspace wiki history only.
- Keep source release history in the approved source repository changelog.

## Open Questions


- Whether future accepted wiki-only changes should create formal board timeline evidence before changelog entries.

## Related


- [Workspace Overview](overview.md)
- [README Maintenance Flow](flows/readme-maintenance.md)
- [Task Lifecycle Flow](flows/task-lifecycle.md)
