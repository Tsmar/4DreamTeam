# Wiki Sync

Use this mode when the workspace wiki must align with accepted changes, explicitly approved source changes, or confirmed pre-development requirements.

## Flow

1. Read related task and timeline evidence through `4dt-board`.
2. Search current wiki content through `4dt-wiki`.
3. Search approved source content through `4dt-sources` when source-backed verification is needed.
4. Read only the needed wiki sections with `4dt-wiki get <page-or-id> --section <section>` when full-page context is not required.
5. Update managed pages through the smallest safe command:
   - `4dt-wiki page section-set` for one section;
   - `4dt-wiki page update` for metadata-only changes;
   - `4dt-wiki page apply` for metadata plus multiple section changes.
6. Do not run multiple wiki writes in parallel for the same page; combine same-page section changes into one `page apply` payload or run them sequentially.
7. Keep each section at or below 32,000 UTF-8 bytes. Split larger material into separate managed wiki pages and link them through `related`.
8. Rebuild and check the wiki index with `4dt-wiki`.
9. Append wiki evidence to the task through `4dt-board` when the sync belongs to a task.

Do not read or write wiki storage directly.
