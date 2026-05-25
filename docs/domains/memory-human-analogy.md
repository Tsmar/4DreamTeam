---
id: domains-memory-human-analogy
kind: domain
title: Memory Human Analogy
status: actual
created_at: 2026-05-25T03:36:03Z
updated_at: 2026-05-25T03:44:47Z
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/references/lead/memory.md", "sources/4DreamTeam/4dreamteam/references/lead/preflight.md", "sources/4DreamTeam/packages/memory/src/fourdt_memory/cli.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/sqlite_store.py", "sources/4DreamTeam/packages/memory/src/fourdt_memory/search_backend.py", "sources/4DreamTeam/packages/search/src/fourdt_search/scoring.py", "https://pubmed.ncbi.nlm.nih.gov/11058819/", "https://pmc.ncbi.nlm.nih.gov/articles/PMC6993580/", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3416886/", "https://arxiv.org/abs/2310.08560", "https://arxiv.org/abs/2304.03442", "https://openai.github.io/openai-agents-js/guides/sandbox-agents/memory/", "https://docs.langchain.com/oss/python/langgraph/persistence"]
task_refs: ["TASK-0017", "TASK-0018", "TASK-0019"]
---

# Memory Human Analogy

## Summary


4DT Memory is designed as an engineering analogue of human memory, not as a biological simulation. The useful parallel is functional: humans do not keep every experience in active attention, and 4DreamTeam should not load every memory into context. Instead, both systems benefit from a small working set, durable long-term stores, selective retrieval, consolidation of lessons, and safeguards against stale or misleading memories.

## Content


### Why The Analogy Matters

The product goal is not to make an agent "remember everything". The goal is to let future work start with the right prior experience, without repeating avoidable discovery or flooding the context window. Human memory is useful here because it is selective and layered: a person keeps only a small amount in active attention, stores different kinds of knowledge differently, retrieves memories based on the current situation, and consolidates repeated experience into more general lessons.

4DreamTeam follows the same engineering pattern:

- `4dt-memory defaults load` is the stable startup layer.
- Bounded `4dt-search` recall is the task/role-specific retrieval layer.
- Board timeline, wiki pages, and approved sources are the evidence layer.
- Durable memory entries are compact lessons, preferences, gotchas, process instructions, and decisions.
- Current evidence always outranks remembered guidance.

### Human Working Memory And The Agent Context Window

Human working memory is limited. Baddeley's working-memory model separates active control from short-term stores and later adds an episodic buffer that binds information into a coherent working episode. 4DreamTeam maps this to the agent's current context:

- The current user request, active role, task id, and loaded references form the active working set.
- The context window is scarce, so memory recall must be bounded.
- The "episodic buffer" analogue is the task working context: the agent combines the current request, selected wiki/source/board evidence, and a few relevant memories into one coherent plan.
- Loading all memory would be like trying to hold a whole life history in working memory before answering one question; it reduces signal and makes mistakes more likely.

This is why startup recall is split into contract defaults plus a small supplemental search only when route, role, continuation state, or the operator request makes prior lessons relevant.

### Episodic, Semantic, And Procedural-Like Memory

Human memory research often distinguishes episodic memory (events and experiences) from semantic memory (general knowledge). 4DreamTeam should use a similar split:

- Board timeline entries are closest to episodic memory. They preserve what happened: product decisions, analytic handoffs, developer reports, quality acceptance, wiki updates, and release records.
- Wiki pages are closest to semantic memory. They consolidate accepted facts about product, architecture, workflows, tools, source boundaries, and schemas.
- Durable `4dt-memory` items are compact retrieval cues and learned rules. They are not raw transcripts; they point future agents toward the relevant board/wiki/source evidence.
- Role-scoped memories behave like procedural guidance: "how the developer role should run tests here", "what quality usually checks", or "what wiki sync must not forget".

This division avoids turning memory into a second source of truth. Episodes stay in the board, consolidated knowledge stays in the wiki, and compact recall cues stay in memory.

### Consolidation: Turning Experience Into Lessons

Human memory is not just recording; it transforms experience into durable knowledge. Systems-consolidation research describes how memories can be stabilized, reorganized, and integrated over time. 4DreamTeam has a workflow version of consolidation:

1. The agent performs work through product, analytic, developer, quality, wiki, and release roles.
2. The board timeline records the episode.
3. Quality acceptance determines whether the outcome is trusted.
4. Wiki post-acceptance turns accepted behavior into durable project knowledge.
5. `4dt-memory remember` stores only compact, reusable lessons when they help future sessions.

The important rule is timing: do not save unaccepted guesses as durable memory. A memory entry should usually be created after evidence exists, especially for implementation lessons, test workflows, or process instructions.

### Retrieval: Remembering By Situation

Humans recall different memories depending on cues: task, goal, role, recent context, and relevant associations. 4DreamTeam should do the same with explicit search cues:

- current role: `developer`, `quality`, `wiki`, `release`, `analytic`, `product`, or `devops`;
- current task id and title;
- artifact ids, file paths, commands, package names, and CLI names;
- translated English technical terms from the operator's request;
- known problem shape: tests, logs, source boundaries, releases, wiki sync, CI, migrations, or operator preference.

The agent should generate a small set of enriched `4dt-search query` variants and search explicit domains. Examples:

```txt
developer project test workflow noisy logs validation commands
quality acceptance criteria rejected gotcha task TASK-0017
wiki post-acceptance documentation source-backed update
release packaging changelog staging commit policy
```

This is intentionally closer to cue-based recall than to a database dump.

### Forgetting, Filtering, And Safety

Human forgetting is not only failure; it is also filtering. An agent needs the same discipline. 4DreamTeam should not save:

- secrets, credentials, `.env` contents, dumps, production data, or private keys;
- temporary implementation details already obvious from source;
- unaccepted proposals, rejected assumptions, or speculative claims;
- large copied logs or reports;
- memories that duplicate canonical role instructions.

When memory conflicts with current evidence, the current request, board/wiki/source artifacts, and live validation win. A stale memory should be superseded, retired, or documented as a conflict through visible workflow.

### Language Model

The operator may express memory intent in any language. Internal durable memory is stored in English because the managed agent knowledge base is English-first, English improves cross-agent portability, and consistent English technical wording improves `4dt-search` recall. Exact commands, paths, ids, API names, code identifiers, and localized user-facing text are preserved when they are the thing being remembered.

This means a Russian operator request such as "нужно запомнить как у нас работают тесты, чтобы в следующий раз не изучать" should become an English memory entry after evidence is gathered, for example: "For this project, developer agents should discover the test workflow from ... before broad source reading."

### Where The Analogy Stops

4DT Memory is not a mind, hippocampus, neocortex, or biological model. The analogy is operational:

- working memory maps to the bounded active context;
- episodic memory maps to board timeline evidence;
- semantic memory maps to managed wiki knowledge;
- procedural guidance maps to role-scoped memory;
- consolidation maps to quality acceptance plus wiki/memory updates;
- cue-based recall maps to enriched `4dt-search` queries.

The framework should keep this boundary explicit so memory design stays testable, auditable, and safe.

## Evidence


- `4dreamteam/references/lead/memory.md` defines authority order, operator memory intent, English-first durable memory, placement policy, role-scoped recall, bounded startup/task recall, save flow, and stale-memory handling.
- `4dreamteam/references/lead/preflight.md` defines contract defaults and bounded supplemental recall after defaults.
- `packages/memory/src/fourdt_memory/cli.py` defines durable memory commands, scopes, roles, types, contract defaults, session state, and safety checks.
- `packages/memory/src/fourdt_memory/sqlite_store.py` and `schema.sql` define the authoritative SQLite store.
- `packages/memory/src/fourdt_memory/search_backend.py` adapts memory rows to the shared 4dt-search runtime backend.
- `packages/search/src/fourdt_search/scoring.py` provides the shared retrieval/ranking behavior used by memory search.
- TASK-0017 accepted quality evidence backs operator-intent, placement, role-scoped recall, and bounded startup/task recall policy.
- TASK-0018 accepted quality evidence backs English durable memory regardless of operator language.
- Baddeley, "The episodic buffer: a new component of working memory?", PubMed: https://pubmed.ncbi.nlm.nih.gov/11058819/
- Eichenbaum, "Semantic Memory and the Hippocampus", PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC6993580/
- Norman, "How hippocampus and cortex contribute to recognition memory: Revisiting the Complementary Learning Systems model", PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3416886/
- MemGPT: "Towards LLMs as Operating Systems", arXiv: https://arxiv.org/abs/2310.08560
- Generative Agents: "Interactive Simulacra of Human Behavior", arXiv: https://arxiv.org/abs/2304.03442
- OpenAI Agents SDK sandbox memory guide: https://openai.github.io/openai-agents-js/guides/sandbox-agents/memory/
- LangGraph persistence and memory docs: https://docs.langchain.com/oss/python/langgraph/persistence

## Decisions


- Use the human-memory analogy as an engineering model, not a biological claim.
- Keep active recall bounded; never load all memory into context by default.
- Treat board timeline as episodic evidence and wiki as consolidated semantic knowledge.
- Treat role-scoped durable memory as procedural guidance for future agents.
- Store durable memory in English regardless of operator language.
- Use 4dt-search query enrichment as the explicit cue-based recall mechanism.
- Consolidate only accepted or source-backed lessons into durable memory.
- Keep memory below current request, board/wiki/source artifacts, and live validation output.

## Open Questions


- Should a future `4dt-memory classify-intent` helper expose the analogy as machine-readable categories?
- Should memory benchmarks measure "context saved" and "irrelevant recall avoided" alongside correctness?
- Should future memory entries include explicit `startupRelevant` or `roleRelevant` metadata, or is scope/type/role enough?

## Related


- [Memory Domain](memory.md)
- [Search Domain](search.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Workspace Tools Contract](../contracts/workspace-tools.md)
- [Task Lifecycle](../flows/task-lifecycle.md)
