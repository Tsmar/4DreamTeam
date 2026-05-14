# RELEASE-XXXX: Release Plan

## Status

planned / approved / committed / blocked

## Accepted Basis

- `<path>` - <accepted evidence>

## Repository

- Path: `<path>`
- Current branch: `<branch>`
- Target branch: `<branch or requires user decision>`

## Included Files

- `<path>` - <reason>

## Excluded Dirty Files

- `<path>` - <reason, or `None`>

## Changelog

- Workspace target: `docs/<project-name>/CHANGELOG.md` / not applicable
- Source target: `<approved-source>/CHANGELOG.md` / not applicable

```md
<entry>
```

## Commit

```txt
<type>(<scope>): <summary>
```

## Commands After Approval

```bash
git add <specific-file> <specific-file>
git commit -m "<message>"
```

## Approval State

- Stage/commit approval: pending / approved
- Push approval: not requested / pending / approved

## Result

- Commit: `<hash>` / not created
- Notes: <blocked reason or `None`>
