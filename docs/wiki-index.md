# Wiki Index

Project wikis can include a structured source map:

```txt
docs/<project-name>/source-map.md
```

`source-map.md` is the editable source of truth for semantic navigation across approved sources. Generated `.index` files are derived from it and should not be edited by hand.

## Commands

The skill includes a dependency-free Python 3 CLI. Resolve the installed skill path first, then run:

```bash
python3 <resolved-skill-path>/scripts/wiki_index.py index build docs/<project-name>
python3 <resolved-skill-path>/scripts/wiki_index.py index check docs/<project-name>
python3 <resolved-skill-path>/scripts/wiki_index.py search docs/<project-name> "release changelog"
```

From this repository checkout, the path is:

```bash
python3 4dreamteam/scripts/wiki_index.py index build docs/<project-name>
python3 4dreamteam/scripts/wiki_index.py index check docs/<project-name>
python3 4dreamteam/scripts/wiki_index.py search docs/<project-name> "release changelog"
```

If the script is unavailable, use `source-map.md` directly with narrow `rg` searches and report that generated `.index` files were not rebuilt.

## Index-First Navigation

The index is intentionally lightweight. It searches source roots, semantic groups, file descriptions, keywords, and related wiki pages before an agent reads larger source files.

When a project wiki has a current `.index/source-map.json`, 4DreamTeam roles use index-first navigation before broad project wiki or approved-source reading. They search first, then read the relevant wiki pages and source files from the top semantic groups.

Exact file/page tasks and missing or stale indexes can skip this step.

## Source Boundaries

Search results do not grant access to additional files. Approved source paths are hard boundaries.

Do not infer access to:

- parent directories;
- sibling projects;
- `.env` files;
- credentials;
- private keys;
- dumps;
- unrelated user files.
