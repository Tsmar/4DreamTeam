---
id: domains-source-boundaries
kind: domain
title: Source Boundaries Domain
status: actual
created_at: 2026-05-23T07:32:25Z
updated_at: 2026-05-24T10:42:40Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/4dreamteam/references/wiki.md", "sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py", "sources/4DreamTeam/packages/search/src/fourdt_search/domains/sources.py"]
task_refs: ["TASK-0001", "EPIC-0001-TASK-0010"]
---

# Source Boundaries Domain

## Summary



Source boundaries control what agents may read for project facts. Workspace `sources/` is built in; external paths must be registered explicitly through `4dt-sources` with operator approval.

## Content




The skill treats approved source paths as hard read boundaries. It must not infer access to parent directories, sibling projects, secrets, dumps, or unrelated user files. The workspace `sources/` folder is readable by default, and external file or directory boundaries are added only through `4dt-sources registry add --operator-approved`.

`4dt-sources` owns the registry, source inventory, search, get, and stats. The registry is the single source of truth for approved external source access. Agents should use `4dt-sources registry list`, `index build/check`, `search`, and `get` before broad source reading.

The sources tool now applies one exclusion policy to both index traversal and safe file reads. It filters common ignored names such as dependency folders, build outputs, caches, and `.DS_Store`; treats secret-like names and suffixes as forbidden, including `.env`, `.env.*`, `.pem`, `.key`, `.p12`, and `.dump`; and honors project `.gitignore` rules for workspace and registered directory sources. Ignored or forbidden paths are omitted from the inventory, ignored directories are pruned before traversal, and `get` rejects excluded paths before reading file content.

Wiki and documentation claims must be backed by approved sources, accepted timeline evidence, or explicit blueprint assumptions. The wiki role must not document rejected or unconfirmed changes as actual behavior and must not read outside approved source boundaries.

In this workspace, `4dt-sources registry list` reports the built-in `workspace-sources` boundary at `sources`. The active source repository for this wiki is `sources/4DreamTeam/`. Legacy docs under `sources/old_docs/` are inside the boundary but should be treated as legacy reference material, not the current model for new wiki storage.

## Evidence





- `sources/4DreamTeam/4dreamteam/SKILL.md` defines hard source-boundary guarantees.
- `sources/4DreamTeam/4dreamteam/references/lead/preflight.md` defines workspace `sources/` and external source registration policy.
- `sources/4DreamTeam/4dreamteam/references/wiki.md` defines wiki source-of-truth and approved-source rules.
- `sources/4DreamTeam/packages/sources/src/fourdt_sources/cli.py` defines registry behavior, ignored names, forbidden source patterns, `.gitignore` matching, and the shared index/get exclusion policy.
- `sources/4DreamTeam/packages/search/src/fourdt_search/domains/sources.py` connects approved-source records to unified 4dt-search discovery without expanding permissions.
- TASK-0001 accepted quality evidence records tests for node_modules, `.env`, `.gitignore` file and directory exclusions, registered directory sources, and `get` rejection for excluded paths.

## Decisions




- Use `4dt-search query --domain sources` for source discovery.
- Use `4dt-sources` as the source registry, inventory, and exact-read API.
- Treat source registry boundaries as hard limits, not suggestions.
- Keep old multi-project wiki registry/source-map material as legacy, not new-work guidance.

## Open Questions




- Whether old docs should remain inside the broad workspace `sources/` boundary or be archived outside active source inventory.
- Whether additional source-domain ranking fixtures are needed after CI is added.

## Related



- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Wiki Workflow](../flows/wiki-workflow.md)
- [Memory Domain](memory.md)
- [Tool Storage Schema](../schemas/tool-storage.md)
