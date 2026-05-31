---
id: contracts-agent-instructions
kind: contract
title: Agent Instructions Contract
status: actual
created_at: "2026-05-23T07:32:03Z"
updated_at: "2026-06-01T00:00:00Z"
owner: wiki
source_refs: ["sources/4DreamTeam/4dreamteam/SKILL.md", "sources/4DreamTeam/AGENTS.md", "sources/4DreamTeam/4dreamteam/agents/openai.yaml", "sources/4DreamTeam/4dreamteam/references/lead/contracts.md"]
task_refs: []
tags: ["agents", "contracts", "instructions"]
---

# Agent Instructions Contract

## Summary

Agent instructions are layered: repository development rules, skill entrypoint metadata, Codex UI metadata, lead routing rules, role references, mode-specific references, and templates.

## Content

`AGENTS.md` applies to this source repository. It states that this folder is for developing the `4DreamTeam` Codex skill, not for running external project tasks. It defines the default working mode, language policy, best-practice references, change policy, and safety constraints for source changes.

`4dreamteam/SKILL.md` is the installed skill entrypoint. It defines discoverability metadata, version, repository, first steps, role references, template inventory, reference-loading policy, and hard guarantees. It should stay compact enough to route the request, while detailed behavior lives in `references/`.

`4dreamteam/agents/openai.yaml` defines the UI wrapper: display name `4DreamTeam`, short description, small and large icons, brand color, and default prompt. This affects how the skill appears in Codex, not the detailed workflow contracts.

`references/lead/contracts.md` defines mandatory output contracts for every role. Product, analytic, developer, quality, wiki, release, devops, and marketing each have required artifact/report fields. It also defines the role instruction quality checklist and the boundary between behavior instructions and templates.

Role instructions must define responsibility, boundaries, mandatory inputs, mandatory outputs, stop conditions, approval gates, safety constraints, handoff rules, failure behavior, and useful template pointers. Templates may add structure, but they cannot be the only place a required behavior is defined.

When changing skill behavior, update the corresponding reference files. When changing workspace bootstrap behavior, update related templates. Before commit or release packaging, behavior, metadata, template, reference, or public documentation changes require version/changelog consideration under the source repository rules.

## Evidence

- `sources/4DreamTeam/4dreamteam/SKILL.md` defines skill loading, role references, templates, and hard guarantees.
- `sources/4DreamTeam/AGENTS.md` defines workspace-specific agent behavior.
- `sources/4DreamTeam/4dreamteam/agents/openai.yaml` declares the OpenAI agent entrypoint.
- `sources/4DreamTeam/4dreamteam/references/lead/contracts.md` defines instruction contract and precedence rules.

## Decisions

- Instruction changes belong in references or `SKILL.md`, not hidden only in templates.
- `AGENTS.md` should stay short and repository-focused.
- `SKILL.md` should remain the compact route entrypoint; detailed workflow belongs in reference modules.

## Open Questions

- Whether the source repository should add automated checks for frontmatter description length and version consistency.
- Whether each role reference should have an explicit example section or rely on template pointers.

## Related

- [Architecture Overview](../architecture/overview.md)
- [Runtime Entrypoint](../architecture/runtime-entrypoint.md)
- [Templates Domain](../domains/templates.md)
- [Task Lifecycle Flow](../flows/task-lifecycle.md)
