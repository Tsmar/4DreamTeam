# Wiki Tooling

The current wiki model is a single workspace wiki managed by `4dt-wiki`.

Use:

```bash
npm run 4dt-wiki -- status
npm run 4dt-wiki -- validate
npm run 4dt-wiki -- index build
npm run 4dt-wiki -- index check
npm run 4dt-wiki -- search "release changelog"
npm run 4dt-wiki -- get overview
```

Source registry and source inventory are managed by `4dt-sources`:

```bash
npm run sources -- registry list
npm run sources -- index build
npm run sources -- index check
npm run sources -- search "api"
```

Agents should query wiki and source information through these tools. The old multi-project registry and source navigation model is legacy and should not be used for new work.
