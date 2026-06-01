# Wiki Sync

Use this mode when the workspace wiki must align with accepted changes, explicitly approved source changes, or confirmed pre-development requirements.

## Flow

1. Read related task and timeline evidence through `4dt-board`.
2. Search current wiki content through `4dt-wiki`.
3. Search approved source content through `4dt-sources` when source-backed verification is needed.
4. Read only the needed wiki sections with `4dt-wiki get <page-or-id> --section <section>` when full-page context is not required.
5. Inspect current tags with `4dt-wiki tags list` when the change introduces, removes, or renames durable concepts.
6. Update managed pages through the smallest safe command:
   - `4dt-wiki page section-set` for one section;
   - `4dt-wiki page update` for metadata-only changes;
   - `4dt-wiki page apply` for metadata, tags, and multiple section changes.
7. Keep page tags aligned with the updated content: reuse existing durable tags, add newly important domain/workflow/component tags, and remove tags that no longer describe the page.
8. SQLite transactions serialize managed writes. Parallel reads/searches and independent page writes are allowed; combine same-page section, tag, status, and ref changes into one `page apply` payload when they are one logical update. Avoid competing same-page/same-field writes unless the workflow explicitly owns conflict handling.
9. Keep each section at or below 32,000 UTF-8 bytes. Split larger material into separate managed wiki pages and link them through `related`.
10. Rebuild and check the wiki index with `4dt-wiki`.
11. Append wiki evidence to the task through `4dt-board` when the sync belongs to a task.

Do not read or write wiki storage directly.
