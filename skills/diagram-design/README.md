# Diagram Design

Create branded diagrams as self-contained HTML files with inline SVG. The skill covers 45 visual types, including architecture, architecture delta, flowchart, sequence, state machine, data models, timelines, service blueprints, dependency graphs, and statistical charts. It also imports Mermaid, draw.io, and Excalidraw content and exports diagrams to SVG or PNG.

## Package contents

- `SKILL.md`: selection workflow, design rules, accessibility contract, and pre-output checks.
- `references/`: 45 visual-type guides plus semantic patterns, layout budgets, styling, import/export, and animation guidance.
- `assets/`: light, dark, and full-editorial examples, five templates, and the icon gallery.
- `scripts/`: dependency-free import, SVG export, accessibility, and geometry helpers, plus optional Playwright-based PNG export.
- `LICENSE` and `THIRD_PARTY_LICENSES.md`: upstream license and bundled-content notices.

The complete directory is the installable skill. Do not copy only `SKILL.md`; its relative companion paths must remain intact.

## Requirements

Viewing HTML output requires a modern browser. The self-check, import helpers, and SVG exporter require Python 3 with no third-party packages. PNG export optionally requires an approved, preinstalled Python Playwright runtime and compatible browser. Templates use Google Fonts with system-font fallbacks; offline output is supported.

## Install and validate

See [Seven's native Linear installation and loading guide](SEVEN.md) for the standard `~/.agents/skills/diagram-design` installation, explicit `/skill:diagram-design` loading, and native Kimi smoke command.

From the repository root, run the offline package validation:

```bash
node scripts/validate-diagram-design.mjs
```

## Attribution

Vendored from [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) at immutable commit `0cf73c3fcc56667ad91a9a04c439ac6ccfabc9d1`. See [UPSTREAM.md](UPSTREAM.md) for the exact packaged scope.
