# Wiki Source Boundaries

Use this file when a wiki mode reads approved sources or validates source-backed claims.

## Source Boundaries

An approved source is a hard boundary.

Read only descendants of the specified source path.

Approved sources can be:

1. confirmed descendants of the workspace `sources/` directory;
2. explicit external source paths approved by the operator.

Forbidden:

1. parent directories;
2. sibling directories;
3. inferred project roots;
4. neighboring projects;
5. files outside approved sources, even if they seem obviously related.

If a file outside an approved source is needed for a correct wiki, stop and request access to that exact path.

## Workspace Sources

`sources/` is the workspace-local staging area for source materials or symlinks to source materials.

First-touch gate:

1. Do not list, stat, resolve, inventory, index, or read `sources/` before operator first-touch confirmation.
2. Ask the operator to personally inspect whether `sources/` exists and whether all current contents may be used.
3. Confirmation is all-or-nothing for the current `sources/` contents. Do not request or accept named-entry confirmation in this task generation.
4. If the operator denies access or confirms absence, do not inspect `sources/`.
5. New files added after confirmation require a separate rescan/actualization confirmation.

After confirmation:

1. Every current descendant of `sources/` is an approved source boundary, subject to the ignore list and forbidden paths.
2. If a descendant is a symlink, resolve it, record both the workspace alias and resolved target, and treat the resolved target as the boundary. Do not read parent or sibling paths.
3. Do not create or repair `sources/.gitignore` automatically. Project-provided `.gitignore` files are honored when present, but workspace bootstrap must not add one because it can block source study through `4dt-sources`.
4. Archive extraction and deep archive inspection are out of scope unless a separate task explicitly defines them.

## Ignore List

Approved sources are read recursively, excluding:

```txt
.git
.hg
.svn
node_modules
dist
build
out
coverage
.cache
.next
.nuxt
.vite
.turbo
.vercel
.DS_Store
*.log
*.tmp
*.bak
.env
.env.*
*.pem
*.key
*.p12
*.sqlite
*.db
*.dump
*.zip
*.tar
*.tar.gz
*.tgz
*.7z
*.rar
vendor
target
.gradle
.idea
.vscode
__pycache__
.pytest_cache
.mypy_cache
```

The user may add forbidden paths beyond the standard list.

## Source Truth

Code and artifacts in confirmed workspace `sources/` and explicit approved external sources are the primary source of truth.

Do not invent behavior that does not exist in approved code sources.

If behavior is not visible from approved sources, mark it as `unknown` or `requires source access`.

Documentation, tests, and comments are used only if they are inside approved sources.

## Project Name Rules

Use `4dt-wiki` to create wiki pages; agents do not derive wiki storage paths from project names.

Allowed format:

```txt
^[a-z0-9]+(-[a-z0-9]+)*$
```

Rules:

1. Lowercase Latin letters, digits, and hyphens only.
2. No spaces.
3. No `_`.
4. No dots.
5. Must not start or end with a hyphen.
6. Must not contain `..`, `/`, or `\`.
7. Length from 2 to 64 characters.

If the user provides an invalid name, propose a normalized version and ask for confirmation.
