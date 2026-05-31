---
id: changelog
kind: changelog
title: Changelog
status: actual
created_at: "2026-05-23T07:31:46Z"
updated_at: "2026-06-01T00:00:00Z"
owner: wiki
source_refs: ["sources/4DreamTeam/CHANGELOG.md", "sources/4DreamTeam/4dreamteam/references/release.md", "sources/4DreamTeam/README.md", "sources/4DreamTeam/README.ru.md", "sources/4DreamTeam/4dreamteam/SKILL.md"]
task_refs: ["TASK-0023", "TASK-0024", "v0.5.8"]
tags: ["changelog", "release", "v0.5.8"]
---

# Changelog

## Summary

This workspace wiki changelog records notable managed-wiki changes for the 4DreamTeam skill workspace. Source release history remains in the repository `CHANGELOG.md`.

## Content

2026-06-01: Prepared 4DreamTeam v0.5.8 release packaging for shared-database schema control. The release records per-domain schema versions and hashes in `tool_schema_versions`, adds `4dt-db schema status`, adds `4dt-db migrate plan/apply` for SQL-side operator-approved data movement, changes memory setup to report `schema_mismatch` instead of silently migrating populated old schemas, and stops `4dt-board validate` from creating legacy board folders.

2026-05-31: Released 4DreamTeam v0.5.7 with shared `.4dt/db.sqlite3` authority for wiki, board, memory, search, and sources. The release moved wiki pages into relational metadata, sections, tags, and FTS rows; moved board items and comments into SQLite transactions; moved sources registry and search chunks/manifests into the shared database; added database backup plus full JSON export/import cycles for wiki, board, and memory; stopped bootstrap from creating `sources/.gitignore`; and kept release-facing Markdown docs generated from managed wiki export.

2026-05-31: Prepared 4DreamTeam v0.5.6 patch packaging for wiki write safety and legacy wiki cleanup. The release adds a 32,000 byte managed wiki section limit, documents serialized same-page wiki writes, updates bundled wiki templates to the current managed frontmatter and stable section contract, removes the legacy sources.md wiki template and source-map wiki index script, and bumps skill metadata/documented version to 0.5.6.

2026-05-25: Prepared 4DreamTeam v0.5.4 release packaging for agent-friendly CLI workflows. The release improves help across 4dt-wiki, 4dt-board, 4dt-sources, 4dt-search, and 4dt-memory; documents stdin-first wiki page apply for generated JSON; adds top-level command group descriptions; records the agent-friendly CLI contract; refreshes tests and exported docs; and bumps skill metadata/documented version to 0.5.4.

2026-05-25: Updated 4DreamTeam CLI ergonomics for agents after accepted TASK-0023 work. Help text now documents safe defaults, payload sources, mode choices, focused reads, source approval requirements, deterministic board timeline entry ids, memory import dry-run/apply behavior, search query/index modes, and stdin-first `4dt-wiki page apply` usage for generated JSON while preserving file-based payload compatibility.

2026-05-25: Prepared 4DreamTeam v0.5.3 release packaging for Wake Context and public README updates. The release adds Wakeup Recall startup guidance, makes installed skill wrappers the default startup launcher, adds a short human/agent wakeup analogy to English and Russian README files, updates quick-start prompts with direct GitHub skill installation, and bumps skill metadata/documented version to 0.5.3.

2026-05-24: Prepared 4DreamTeam v0.5.0 release packaging for EPIC-0001 and accepted EPIC-0002 packaging work. The release adds the universal 4dt-search CLI across sources, wiki, board, and memory; replaces memory retrieval with the SQLite-authoritative search backend; moves CLI source packages into repository packages/; adds self-contained installed-skill runtime wrappers under 4dreamteam/scripts; adds local and GitHub Actions quality gates; and updates managed wiki/source docs for the new search, memory, package, and runtime contracts.

2026-05-23: Bootstrapped the managed workspace wiki for the 4DreamTeam skill source repository. The initial wiki covers product promise, architecture, runtime entrypoint, documentation and README maintenance, agent instruction contracts, workspace tools, lifecycle, wiki workflow, templates, memory, source boundaries, and tool storage schema.

2026-05-23: Updated managed wiki after accepted TASK-0001, TASK-0002, TASK-0003, and TASK-0004 work. The wiki now records .gitignore-aware 4dt-sources exclusions and safe get rejection for excluded paths, section-scoped 4dt-wiki reads/writes with page section-set and page apply, 4dt-wiki export --target <path> for source-shipped release documentation, the developer implementation-plan approval gate, and the mandatory post-quality wiki review step.

2026-05-23: Prepared 4DreamTeam v0.4.0 release packaging for TASK-0001 through TASK-0006. The release includes source exclusion safety, wiki section/apply/export workflows, workflow gate updates, README positioning, simple existing-project setup guidance, and exported source documentation.

This wiki changelog is not a replacement for the source repository changelog. Release rules distinguish workspace changelog entries from source CHANGELOG.md entries. Source changelog updates are required for accepted skill-development changes that affect behavior, metadata, templates, references, or user-facing documentation when release packaging is requested.

## Evidence

- sources/4DreamTeam/CHANGELOG.md is the source repository release history and includes 0.5.8.
- sources/4DreamTeam/4dreamteam/references/release.md defines workspace and source changelog policy, including wiki export before packaging when source-shipped docs are needed.
- README.md, README.ru.md, and 4dreamteam/SKILL.md carry the 0.5.8 public documentation and metadata changes.
- v0.5.7 source changes moved managed wiki, board, memory, search, and sources state into the shared database and added backup/import/export support.
- v0.5.8 source changes add per-domain schema recording, controlled migration planning/apply commands, strict memory schema mismatch handling, and startup bootstrap regressions.

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
