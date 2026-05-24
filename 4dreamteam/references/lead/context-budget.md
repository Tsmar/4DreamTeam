# Context Budget

Use this file when context may expand beyond the compact route path, when large files or broad source areas are involved, or when state should be externalized into artifacts.

## Principles

1. Start with the smallest relevant tool query.
2. Prefer task ids, section names, timeline entry ids, wiki slugs, source ids, and commands over broad directory reads.
3. Load only the smallest detailed module, role reference, task section, timeline entry, wiki page, source registry entry, or source snippet needed for the next decision.
4. Summarize long findings into timeline entries instead of keeping everything in chat context.
5. Use `4dt-memory` only for durable prior context that may change current decisions.

## Tool Order

For discovery, use `4dt-search query` first with explicit domains:

1. `4dt-search query "<query>" --domain board --json`
2. `4dt-search query "<query>" --domain wiki --json`
3. `4dt-search query "<query>" --domain sources --json`
4. `4dt-search query "<query>" --domain memory --json`

Use the result locator or `getCommand` for the smallest full read.

For exact board context:

1. `4dt-board status`
2. `4dt-board list/find`
3. `4dt-board get`
4. `4dt-board section get`
5. `4dt-board comments list/latest`

For exact wiki context:

1. `4dt-wiki get`
2. `4dt-wiki validate` when freshness or compatibility matters.

For exact source context:

1. `4dt-sources registry list`
2. `4dt-sources get`
3. Direct source reads only when the approved boundary and exact need are clear.

## Escalation

Escalate from pointers to content only when the answer, implementation, or acceptance decision cannot be made from summaries and exact references.

Bulk reading is allowed only for route-specific inventory, validation, release packaging, wiki indexing, or source work where the workflow requires it. Even then, prefer tool indexes, search results, and summaries before full content.
