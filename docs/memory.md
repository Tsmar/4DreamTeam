# 4DT Memory

4DT Memory is the local memory runtime for 4DreamTeam. It helps with cross-session continuity, accepted decisions, user preferences, lessons learned, and memory effectiveness checks.

Memory is not a source of truth. It is a recall layer below:

1. the current user request and explicit approvals;
2. workspace artifacts such as `AGENTS.md`, `tasks/`, `reports/`, and managed wiki pages;
3. approved source files inside explicit source boundaries.

When memory conflicts with those sources, trust the current request, workspace artifacts, managed wiki, or approved source files.

## Storage

By default, 4DT Memory stores data outside the workspace and outside the skill directory:

```txt
~/.codex/storage/4dreamteam/memory
```

SQLite is the authoritative store for memory items, evidence, workspace identity, session state, and audit logs. LanceDB is only a rebuildable vector index. The index can be deleted and rebuilt from SQLite with `reindex`.

The CLI supports `--storage-root <path>` for tests, debugging, and controlled maintenance.

## Commands

Initialize storage:

```txt
4dt-memory init --workspace . --json
```

Check storage and index health:

```txt
4dt-memory doctor --workspace . --json
```

Save accepted memory:

```txt
4dt-memory remember "Use local memory storage outside the workspace." \
  --workspace . \
  --scope workspace \
  --type decision \
  --source-type task \
  --source-ref tasks/done/EPIC-0007-TASK-0029-technical-architecture-task-contract.md \
  --json
```

Search memory:

```txt
4dt-memory search "storage root decision" --workspace . --json
```

Search returns concise preview fields by default. Use `get <id>` for full memory content:

```txt
4dt-memory get mem_... --workspace . --json
```

Soft-delete memory:

```txt
4dt-memory forget mem_... --reason "superseded by accepted task" --workspace . --json
```

Rebuild index state:

```txt
4dt-memory reindex --workspace . --embedding-provider hash --json
```

Export and import JSONL:

```txt
4dt-memory export --workspace . --format jsonl --output memory.jsonl --json
4dt-memory import memory.jsonl --workspace . --format jsonl --json
4dt-memory import memory.jsonl --workspace . --format jsonl --apply --json
```

Import is dry-run by default. Exported JSONL can contain sensitive accepted memory content and should be handled as local private data.

Session state:

```txt
4dt-memory session set session-1 '{"step":"quality"}' --workspace . --ttl-seconds 3600 --json
4dt-memory session get session-1 --workspace . --json
```

Benchmark harness:

```txt
4dt-memory benchmark --workspace . --json
```

The benchmark covers wiki-only, memory-only, and memory-plus-wiki modes, with metrics for correctness, completeness, irrelevant or stale recalls, files read, latency, and safety.

## Safety

4DT Memory should store concise, accepted facts with source references.

Allowed durable memory includes:

- stable user preferences;
- accepted architecture, product, source-boundary, or process decisions;
- lessons learned from completed quality, release, or debugging work;
- reusable gotchas that prevent repeated mistakes.

Do not store:

- secrets, credentials, tokens, private keys, `.env` contents, local secret files, dumps, production data, or personal data;
- large copied task, report, wiki, or source contents;
- temporary implementation details that are obvious from current files;
- unaccepted proposals, rejected assumptions, or speculative claims as durable memory.

Redaction is a blocking guard before storage. It is conservative and testable, but it is not a promise that every possible secret can be detected.

## Degraded Mode

Memory absence must not fail a 4DreamTeam workflow.

If SQLite is uninitialized, LanceDB is unavailable, index metadata is mismatched, or embeddings are unavailable, the CLI returns structured degraded status and warnings. Agents should continue with epic handoffs, the local wiki index, tasks, reports, and approved source files.

The deterministic `hash` provider exists for smoke tests and reproducible local checks. It should not be presented as high-quality semantic search. The `none` provider uses lexical fallback.

## Source Boundaries

4DT Memory must not read workspace `sources/` by itself. Import/export/session/benchmark commands do not grant source access and do not replace source-boundary first-touch confirmation.

Memory recalls can help navigation, but any important claim should be verified against current tasks, reports, managed wiki pages, or approved source files before changing behavior.
