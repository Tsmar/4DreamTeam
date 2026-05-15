# Wiki Source Boundaries

Use this file when a wiki mode reads approved sources or validates source-backed claims.

## Source Boundaries

An approved source is a hard boundary.

Read only descendants of the specified source path.

Forbidden:

1. parent directories;
2. sibling directories;
3. inferred project roots;
4. neighboring projects;
5. files outside approved sources, even if they seem obviously related.

If a file outside an approved source is needed for a correct wiki, stop and request access to that exact path.

## Ignore List

Approved sources are read recursively, excluding:

```txt
.git
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

Code in approved sources is the primary source of truth.

Do not invent behavior that does not exist in approved code sources.

If behavior is not visible from approved sources, mark it as `unknown` or `requires source access`.

Documentation, tests, and comments are used only if they are inside approved sources.

## Project Name Rules

`project name` is used as the directory name in `docs/<project-name>`.

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
