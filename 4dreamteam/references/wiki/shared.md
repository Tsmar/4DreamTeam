# Wiki Shared Modules

Shared wiki behavior is implemented through tools:

- `4dt-wiki` owns wiki page shape, frontmatter, stable sections, changelog, ADRs, indexing, and validation.
- `4dt-sources` owns source registry and source inventory.
- `4dt-board` owns task-linked wiki timeline evidence.

Agents should load only the mode file they need and use the tools instead of copying template structures into prompt context.
