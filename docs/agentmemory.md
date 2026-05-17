# Agentmemory

4DreamTeam can use the `agentmemory` plugin as an optional continuity layer when it is available in the current Codex session.

It is not required, and it is not the source of truth.

## Source Of Truth

The source of truth remains:

1. The current user request and explicit approvals.
2. Workspace files: `AGENTS.md`, `tasks/`, `reports/`, and `docs/`.
3. Approved source files inside explicit source boundaries.
4. `agentmemory` recalls, only as supporting context.

## Fallback Order

```txt
agentmemory recall when available and relevant
-> local wiki index/docs
-> tasks and reports
-> exact approved source files when needed and allowed
-> user clarification only when required
```

If `agentmemory` is unavailable, slow, empty, low-signal, or contradictory, 4DreamTeam continues with the local wiki and workspace artifacts.

## What To Save

Save concise durable memories when they help future sessions:

- accepted architecture or product decisions;
- source-boundary or process decisions;
- user workflow preferences;
- lessons from completed quality, release, or debugging work;
- recurring constraints that are easy to forget.

Prefer short summaries with file pointers.

## What Not To Save

Do not save:

- secrets;
- credentials;
- tokens;
- private keys;
- `.env` contents;
- dumps;
- production data;
- full wiki dumps;
- large copied artifacts;
- unaccepted speculation unless clearly marked as unaccepted.

## 0.1.5 Benchmark

We tested `agentmemory` on the `4dreamteam` workspace with five prompts:

1. Source boundaries.
2. Active work.
3. Safety guarantees.
4. Source-file navigation.
5. Why memory was added.

Before curated seeding, memory mostly recalled the fresh memory-policy task and sometimes unrelated project memories. The wiki and task board answered the project questions more reliably.

After saving five short wiki-derived memories with file pointers, memory returned a relevant top result for all five prompts.

## Conclusion

`agentmemory` is useful for quick orientation, recurring constraints, user preferences, and cross-session continuity.

It should not replace wiki verification, accepted reports, or approved source reads.
