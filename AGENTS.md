# 4DreamTeam Skill Development Rules

## Repository Purpose

This folder is the repository for the Codex skill `4DreamTeam`.

It contains:

- the self-contained skill in `4dreamteam/`;
- agent metadata and UI interface files;
- role references;
- templates for files that the skill creates in user workspaces;
- README documentation for installation, testing, and usage.

This folder is not a working workspace for external project tasks.

## Default Working Mode

Requests in this repository are interpreted by default as development, improvement, review, testing, or documentation tasks for the Codex skill.

Do not route these requests through the `4DreamTeam` framework itself. Work as the skill developer: inspect the structure, update instructions, metadata, templates, and documentation.

## What To Check

Before changing the skill, identify which layer the request affects:

- `4dreamteam/SKILL.md` - name, description, trigger surface, main entrypoint, and hard guarantees.
- `4dreamteam/agents/openai.yaml` - display name, short description, icons, brand color, and default prompt.
- `4dreamteam/references/` - detailed workflow and role-specific behavior.
- `4dreamteam/references/wiki/` - knowledge-base route rules.
- `4dreamteam/assets/templates/` - files the skill creates or uses as templates.
- `README.md` - user-facing installation, verification, and usage guide.
- `AGENTS.md` - development rules for this repository only.

Keep `AGENTS.md` short. Do not duplicate lifecycle, task format, wiki structure, or role-specific rules here. Those details belong in `4dreamteam/references/`.

## Language Policy

All Markdown documentation and templates in this repository must be written in English.

Do not add Russian text to `README.md`, `AGENTS.md`, `4dreamteam/references/`, or `4dreamteam/assets/templates/`. User-facing examples must also be in English.

Localized user-facing README translations are allowed in files named `README.<locale>.md`, such as `README.ru.md`. Keep source-of-truth skill instructions, templates, and repository rules in English.

## Best Practices

Codex always has access to the `skill-creator` and `skill-installer` skills.

Use `skill-creator` as the source of best practices when a task concerns skill structure, `SKILL.md`, metadata, discoverability, packaging, or instruction quality.

Consider `skill-installer` when a task concerns installation, removal, installed-skill verification, or reproducing the install flow. The user may test installation themselves; do not add local sync scripts without an explicit request.

When changing the skill, verify that:

- the `name` in frontmatter matches the expected skill name;
- the `name` is discoverable lowercase hyphen-case;
- the `description` clearly explains when the skill should trigger;
- the `description` stays within Codex skill metadata limits, including the 1024-character frontmatter limit;
- short instructions in `SKILL.md` do not conflict with detailed references;
- old names, paths, or outdated installation notes are not left behind;
- templates match the rules that reference them.

## Change Policy

Before changing files, clearly explain what will be changed and wait for user approval unless the user gave explicit `auto` mode or direct confirmation.

When changing skill behavior, update the corresponding reference files.

When changing workspace bootstrap behavior, update the related templates.

When renaming the skill, check metadata, documentation, references, templates, asset paths, and prompts.

Before creating a commit, update the skill version when the change affects skill behavior, metadata, templates, references, or user-facing documentation.

## Changelog Policy

For this repository, `CHANGELOG.md` is a historical index. Source-history entries live in dated files under `changelog/YYYY-MM-DD.md`, and all entries for the same calendar date belong in the same daily file.

When release packaging applies, update the daily changelog file and the root index together. Detailed release rules belong in `4dreamteam/references/release.md`.

## Safety

Do not run destructive commands without explicit user approval.

Do not expose secrets in tasks, reports, documentation, or responses.

Do not perform unrelated refactoring.
