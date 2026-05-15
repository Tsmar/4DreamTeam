# Lead Routing

Use this file to choose the smallest route that can safely produce a checkable result.

## Routing

Route requests as follows:

- workspace status, "what is next", "continue", summarize current work -> status/continuation workflow in `references/lead/read-only.md`;
- validate workspace, check workspace structure, find inconsistent task/report/doc state -> workspace validation workflow in `references/lead/read-only.md`;
- update this workspace to the current 4DreamTeam skill version, refresh workspace rules, self-update workspace -> self-update workflow in `references/lead/self-maintenance.md`;
- improve the `4DreamTeam` skill itself from a workspace with an approved skill source -> self-improvement workflow in `references/lead/self-maintenance.md`;
- clear engineering work such as bugfix, refactor, tests, small docs, or concrete code/config changes -> analytic, then developer -> quality;
- small safe engineering task with explicit `auto` or direct "go ahead" permission -> analytic compact task, then developer -> quality;
- raw business request, product idea, roadmap, product development, backlog formation, epic planning, or feature decomposition -> product, then after approval analytic or developer;
- product backlog, epic shaping, discovery, product questions, or feature ideas -> product;
- continue an existing task or epic -> the role matching the artifact's board column;
- continue epic or product review -> product;
- verify a completed task -> quality;
- create a knowledge base for an existing project -> wiki bootstrap;
- check a knowledge base -> wiki audit/check;
- update a knowledge base after an accepted report -> wiki post-acceptance/sync;
- create a knowledge base for a future project -> wiki blueprint when this mode is enabled by wiki rules;
- deepen an existing knowledge base based on current implementation -> wiki deepening;
- press release, launch announcement, product marketing copy, README positioning, value proposition, audience-facing materials, competitive/product narrative, case study, market-facing analysis -> marketing;
- infrastructure, servers, SSH, deploys, logs, systemd, Docker, nginx/reverse proxy, databases, migrations, diagnostics, incident/deploy/runbook documentation -> devops;
- package accepted work for changelog, commit message, branch review, staging, git commit, release notes, or "prepare commit" -> release.

Do not create an epic for a clear standalone engineering task unless the user explicitly asks for product framing or backlog planning.

## Routing Decision Table

| Request shape | Route | Required gate |
|---|---|---|
| Raw idea, product direction, roadmap, feature decomposition, audience/value/scope question | `product` | Stop after epic changes in controlled mode. |
| Clear engineering change that still needs technical shaping | `analytic -> developer -> quality` | Stop after analytic in controlled mode unless the user approved auto. |
| Small safe localized engineering change with explicit go-ahead | `analytic compact task -> developer -> quality` | Never skip quality. |
| Already implementation-ready task in `tasks/developer/` | `developer -> quality` | Developer must follow task scope and report checks. |
| Completed implementation awaiting review | `quality` | Reject if any criterion is failed or not verified. |
| Accepted behavior needs docs | `wiki post-acceptance` | Requires accepted quality report, task, and developer report. |
| Existing docs need source-backed check without writes | `wiki audit/check` | Read-only unless a later update is approved. |
| New knowledge base from approved sources | `wiki bootstrap` | Intake summary before writing unless defaults/auto are explicitly accepted. |
| Docs need alignment with approved source changes | `wiki sync` | Use approved sources and write only allowed docs scope. |
| Release, changelog, commit, staging, tag, push, or publication | `release` | Requires accepted quality or product acceptance; staging/commit/push need explicit approval. |
| Infrastructure, SSH, deploy, logs, migrations, server state | `devops` | Explain first; risky changes require explicit approval. |
| Public messaging, README positioning, launch copy, market-facing analysis | `marketing` | Use confirmed sources; unsupported claims are excluded. |
| Secrets, destructive operations, production data, unapproved sources, unsafe ambiguity | stop | Ask for approval, source access, or clarification. |

If multiple routes seem plausible, choose the route that preserves safety and auditability:

1. product before analytic when product meaning or scope is unclear;
2. analytic before developer when technical impact, validation, or affected files are unclear;
3. quality before wiki/release for implementation or framework behavior changes;
4. devops before developer when server state or operational risk is involved;
5. release only after accepted evidence exists.

## Incomplete Context

Do not ask the user to decide minor implementation details that can be safely assumed and recorded.

Ask a blocking question or stop when missing context affects:

1. product goal, target audience, or acceptance criteria;
2. public API, contract, schema, data, migration, architecture, security, secrets, or compatibility;
3. source access boundaries;
4. production infrastructure, external services, or destructive operations;
5. release target, staging scope, push/tag/publication approval;
6. whether a claim is source-backed.

Safe assumptions must be written into the task, report, or docs artifact that depends on them.

Forbidden assumptions:

1. assuming approval for secrets, production data, destructive commands, deploys, migrations, git push, tags, or publication;
2. assuming access outside approved source boundaries;
3. assuming unverified behavior is implemented;
4. assuming a rejected or unreviewed change is accepted.
