# RELEASE-XXXX: Release Plan

## Status

planned / approved / committed / pushed / tagged / published / blocked

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

## Tag And GitHub Release

- Tag: `<tag>` / not requested
- GitHub Release: none / draft / published
- Release notes: manual / generated / from file

## Commands After Approval

```bash
git add <specific-file> <specific-file>
git commit -m "<message>"
```

## Approval State

- Stage/commit approval: pending / approved
- Branch push approval: not requested / pending / approved
- Tag approval: not requested / pending / approved
- GitHub Release approval: not requested / pending / approved

## Result

- Commit: `<hash>` / not created
- Branch pushed: yes / no
- Tag pushed: `<tag>` / no
- GitHub Release: `<url>` / draft / not created
- Released tasks moved to `tasks/released`: yes / no
- Notes: <blocked reason or `None`>
