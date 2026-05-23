# Wiki Deepening

Use this mode when existing wiki content needs more implementation detail from current approved sources.

## Flow

1. Find relevant pages through `4dt-wiki search`.
2. Read the smallest required page sections through `4dt-wiki get <page-or-id> --section <section>`.
3. Use `4dt-sources search/get` for approved source evidence.
4. Update managed pages through the smallest safe `4dt-wiki` command:
   - `4dt-wiki page section-set` for one section;
   - `4dt-wiki page update` for metadata-only changes;
   - `4dt-wiki page apply` for metadata plus multiple section changes.
5. Validate with `4dt-wiki validate`.

Do not read or write wiki storage directly.
