# Wiki Bootstrap

Use this mode to initialize the single workspace wiki from approved sources.

## Flow

1. Show an intake summary and wait for confirmation unless the user explicitly accepts defaults or auto mode.
2. Check approved sources with `4dt-sources registry list`.
3. Initialize wiki storage with `4dt-wiki init`.
4. Create or update managed pages through `4dt-wiki page create/update`.
5. Build and check the wiki index with `4dt-wiki index build` and `4dt-wiki index check`.
6. Validate with `4dt-wiki validate`.

Do not read or write wiki storage directly.
