# Wiki Page Shape

`4dt-wiki` owns page frontmatter and stable sections.

Agents should not memorize or manually recreate page templates. Use `4dt-wiki page create`, `4dt-wiki page update`, `4dt-wiki page section-set`, `4dt-wiki page apply`, and `4dt-wiki validate`.

## Stable Sections

Managed wiki pages use these stable section keys and level-2 headings:

- `summary` -> `Summary`
- `content` -> `Content`
- `evidence` -> `Evidence`
- `decisions` -> `Decisions`
- `open_questions` -> `Open Questions`
- `related` -> `Related`

Validation requires every managed page to contain all six headings.

## Section Reads

Prefer section reads when one section is enough:

```bash
4dt-wiki get <page-or-id> --section <section>
```

The JSON response includes page metadata, `section`, and the selected section `content` only.

## Section Writes

Use section-scoped writes for single-section updates:

```bash
4dt-wiki page section-set <page-or-id> <section> --content "<markdown>"
```

If `--content` is omitted, `4dt-wiki` reads the replacement content from stdin. Section replacement preserves the page frontmatter and all other sections.

## Metadata And Multi-Section Writes

Use `page update` for metadata-only changes:

```bash
4dt-wiki page update <page-or-id> --status <status>
```

Use `page apply` when metadata and one or more sections should change together:

```bash
4dt-wiki page apply <page-or-id> --file payload.json
```

If `--file` is omitted, `4dt-wiki` reads the JSON payload from stdin.

Payload fields:

- `status`: one of the supported page statuses.
- `source_refs`: array of strings.
- `task_refs`: array of strings.
- `sections`: object keyed by stable section keys.

Each `sections` value may be a string or an array of strings. Arrays are joined with newline characters before replacing the section body.

Example payload:

```json
{
  "status": "accepted",
  "source_refs": ["sources/app.py"],
  "task_refs": ["TASK-0001"],
  "sections": {
    "summary": "Current accepted summary.",
    "evidence": ["- `sources/app.py`", "- `TASK-0001` quality acceptance"]
  }
}
```
