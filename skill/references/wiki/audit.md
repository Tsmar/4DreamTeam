# Wiki Mode: Audit

Read-only analysis of docs and explicitly specified sources.

## Purpose

Find gaps, stale pages, missing sources, structural mismatches, and propose an update plan.

## Rules

1. May run without an accepted quality report.
2. Read only docs and source roots explicitly specified by the user.
3. Do not change files.
4. Do not create tasks, reports, or docs.
5. If source access is insufficient, explicitly list the missing paths.

## Output

Report:

1. What was checked.
2. What gaps were found.
3. Which pages look stale.
4. Which sources are missing.
5. Recommended update plan.

## Status Handling

Do not change page status. If a status looks incorrect, report it as a finding.
