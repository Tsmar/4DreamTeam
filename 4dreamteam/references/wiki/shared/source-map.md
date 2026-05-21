# Wiki Source Map

Use this file when creating or updating `docs/<project-name>/source-map.md`.

## Source Map

Managed wikis may include a semantic source map:

```txt
docs/<project-name>/source-map.md
```

`source-map.md` is a navigation layer over approved sources, not a raw file manifest. It answers:

```txt
Where is the source of truth for this behavior, contract, workflow, role, schema, integration, or release artifact?
```

Keep `sources.md` and `source-map.md` separate:

1. `sources.md` records approved source boundaries, denied paths, requested sources, and ignore policy.
2. `source-map.md` groups files by semantic purpose and points agents to the right source files and related wiki pages.
3. `.index/sources/*` records low-token raw source inventory and must not be treated as a semantic source map.

Use this hierarchy:

```txt
approved source root
-> source area
-> semantic group
-> primary/supporting files
-> related wiki pages
-> update triggers
```

Each source map must support multiple approved source roots and project shapes such as `frontend`, `backend`, `fullstack`, `skill-development`, `docs`, `infra`, `library`, `mixed`, or `unknown`.

Do not mirror the full file tree. Include only files that help an agent answer a meaningful question or locate a source of truth.

When a source root is a workspace `sources/` alias or symlink, record both the workspace alias and the resolved path in source metadata. The resolved target is the hard read boundary; its parent and siblings remain out of scope.
