# <project-name> Wiki Sources

## Output

`docs/<project-name>`

## Approved sources

- `<path>` — <purpose>

Each approved source is a recursive read boundary. The agent may read only descendants of the approved path, excluding ignored files.

## Denied sources

- `<path>` — <reason>

## Requested sources

- `<path>` — <why needed>

## Notes

- <note>

## Ignore list

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
