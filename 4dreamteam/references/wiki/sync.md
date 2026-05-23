# Wiki Sync

Use this mode when the workspace wiki must align with accepted changes, explicitly approved source changes, or confirmed pre-development requirements.

## Flow

1. Read related task and timeline evidence through `4dt-board`.
2. Search current wiki content through `4dt-wiki`.
3. Search approved source content through `4dt-sources` when source-backed verification is needed.
4. Update managed pages through `4dt-wiki page update`.
5. Rebuild and check the wiki index with `4dt-wiki`.
6. Append wiki evidence to the task through `4dt-board` when the sync belongs to a task.

Do not read or write wiki storage directly.
