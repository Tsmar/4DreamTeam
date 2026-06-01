# Wiki Deepening

Use this mode when existing wiki content needs more implementation detail from current approved sources.

## Flow

1. Find relevant pages through `4dt-search query "<query>" --domain wiki --json`.
2. Read the smallest required page sections through the result `getCommand` or `4dt-wiki get <page-or-id> --section <section>`.
3. Use `4dt-search query "<query>" --domain sources --json` for approved source evidence, then read full snippets through the result `getCommand` or `4dt-sources get`.
4. Update managed pages through the smallest safe `4dt-wiki` command:
   - `4dt-wiki page section-set` for one section;
   - `4dt-wiki page update` for metadata-only changes;
   - `4dt-wiki page apply` for metadata, tags, and multiple section changes.
5. Reconcile tags when the deeper content changes what the page is about: reuse existing tags from `4dt-wiki tags list`, add durable domain/workflow/component tags, and remove stale tags.
6. SQLite transactions serialize managed writes. Parallel reads/searches and independent page writes are allowed; combine same-page section, tag, status, and ref changes into one `page apply` payload when they are one logical update. Avoid competing same-page/same-field writes unless the workflow explicitly owns conflict handling.
7. Keep each section at or below 32,000 UTF-8 bytes. Split larger material into separate managed wiki pages and link them through `related`.
8. Validate with `4dt-wiki validate`.

Do not read or write wiki storage directly.
