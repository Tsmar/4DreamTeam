# Development

This repository is for developing the `4DreamTeam` Codex skill.

## Repository Structure

```txt
4DreamTeam/
  AGENTS.md
  README.md
  README.ru.md
  CHANGELOG.md
  docs/
  4dreamteam/
    SKILL.md
    agents/
      openai.yaml
    references/
    assets/
      templates/
    scripts/
      wiki_index.py
```

Important files:

- `4dreamteam/SKILL.md` - skill metadata, trigger surface, entrypoint, template list, and hard guarantees.
- `4dreamteam/references/` - detailed role and workflow rules.
- `4dreamteam/assets/templates/` - templates copied or adapted into user workspaces.
- `4dreamteam/agents/openai.yaml` - Codex UI metadata.
- `4dreamteam/scripts/wiki_index.py` - dependency-free local wiki index CLI.
- `docs/` - detailed public documentation linked from the README.
- `AGENTS.md` - development rules for this repository.

## Before Changing The Skill

Check which layer is affected:

- `4dreamteam/SKILL.md` for trigger surface, template inventory, version metadata, and hard guarantees.
- `4dreamteam/agents/openai.yaml` for Codex UI metadata.
- `4dreamteam/references/` for detailed role behavior.
- `4dreamteam/assets/templates/` for generated workspace artifacts.
- `README.md` and `docs/` for user-facing documentation.
- `AGENTS.md` for repository development rules.

Keep `SKILL.md` concise and move detailed behavior into references. Keep templates aligned with the rules that mention them.

## Self-Improvement

When a 4DreamTeam workspace improves this skill, use the controlled lifecycle:

```txt
product -> developer -> quality -> wiki when needed -> product acceptance
```

Risky framework changes require independent quality review before wiki, product acceptance, or release packaging.

Do not edit safety rules, lifecycle rules, role routing, approval gates, release behavior, DevOps behavior, source-boundary behavior, role output contracts, or workflow templates as an ad hoc change.
