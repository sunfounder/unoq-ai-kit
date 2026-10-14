# Documentation tools

## check_mermaid.mjs

Sphinx does not validate Mermaid. A broken diagram builds with **zero warnings**
and only shows an error box in the browser, so this script parses every
`.. mermaid::` block with the same Mermaid version the docs site loads.

```bash
cd tools
npm install          # or: pnpm install
node check_mermaid.mjs                 # defaults to ../docs/source
node check_mermaid.mjs path/to/source  # or point it somewhere else
```

Exit code is 1 when a diagram fails, so it can run in CI. Run it after editing
any diagram.
