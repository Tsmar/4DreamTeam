# Wiki Local Indexing

Use this file when generating, checking, or searching local wiki indexes.

## Local Wiki Index

Generated index files may live under:

```txt
docs/<project-name>/.index/
  source-map.json
  manifest.json
```

Rules:

1. `source-map.md` is the editable source of truth.
2. `.index/source-map.json` and `.index/manifest.json` are generated artifacts.
3. Agents must not edit `.index/*` manually.
4. Rebuild the index after source map changes with the bundled Python wiki index script:

```bash
python3 <resolved-skill-path>/scripts/wiki_index.py index build <docs-project-path>
```

5. Check the index with:

```bash
python3 <resolved-skill-path>/scripts/wiki_index.py index check <docs-project-path>
```

6. Search the index with:

```bash
python3 <resolved-skill-path>/scripts/wiki_index.py search <docs-project-path> "<query>"
```

Resolve `<resolved-skill-path>` from the installed 4DreamTeam skill first. In the source repository checkout, the script path is `4dreamteam/scripts/wiki_index.py`.

If the bundled tooling is unavailable in the current workspace, keep `source-map.md` updated, navigate it directly with narrow `rg` searches and small reads, and report that generated `.index` files were not rebuilt.

## Index-First Navigation

When a managed wiki has an up-to-date index at:

```txt
docs/<project-name>/.index/source-map.json
```

roles must use local wiki search before broad project wiki or approved-source reading for:

1. project orientation;
2. finding source-of-truth files for behavior, API, workflow, schema, integration, role rules, infrastructure, or release artifacts;
3. preparing analytic tasks;
4. starting developer work in an unfamiliar area;
5. quality checks for documentation or source-backed behavior;
6. wiki sync, check, or deepening;
7. broad project questions.

Search-first flow:

1. Run `python3 <resolved-skill-path>/scripts/wiki_index.py index check <docs-project-path>` if index freshness is uncertain.
2. Run `python3 <resolved-skill-path>/scripts/wiki_index.py search <docs-project-path> "<query>"`.
3. Read only the relevant wiki pages and approved source files from the top results, usually 1-3 semantic groups.
4. If the bundled tool is unavailable, search `source-map.md` directly with `rg` and read the smallest relevant groups.
5. If search results are missing, stale, or insufficient, fall back to the smallest relevant docs/source scope and report that fallback.

Skip search when:

1. the user gave an exact file or exact wiki page;
2. the task already has exact approved source scope;
3. the workflow is workspace status without project-specific deep dive;
4. `source-map.md` or `.index/source-map.json` is absent;
5. `index check` reports stale or missing index and the current mode is read-only;
6. wiki bootstrap has not created a source map yet.

After any change to `source-map.md`:

1. run `python3 <resolved-skill-path>/scripts/wiki_index.py index build <docs-project-path>`;
2. run `python3 <resolved-skill-path>/scripts/wiki_index.py index check <docs-project-path>`;
3. do not edit `.index/*` manually.

Search results do not expand source permissions. Read only files inside approved source boundaries from `sources.md`.
