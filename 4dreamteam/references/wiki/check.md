# Wiki Check

Use this mode for a read-only check that wiki content matches approved sources.

## Flow

1. Use `4dt-wiki status` and `4dt-wiki validate`.
2. Use `4dt-search query "<query>" --domain wiki --json` for relevant pages, then result `getCommand` or `4dt-wiki get` for full reads.
3. Use `4dt-sources registry list`, `4dt-sources index check`, and `4dt-search query "<query>" --domain sources --json` for approved source evidence.
4. Report stale, conflicting, missing, or unverified claims.

Do not repair files unless the user approves the specific changes.
