# Seven native Linear sessions

The native skill name is `diagram-design`. Install the complete directory: `SKILL.md` loads the sibling `references/` and `assets/` resources while designing a diagram, and the `scripts/` helpers provide import, export, accessibility, and geometry checks. Installing only the Markdown file loses all 45 type references, the design system, templates, examples, and validation helpers.

This package is opt-in. These instructions do not change Seven's default skill or AgentBridge's text-injection configuration.

## Install for native discovery

After this package merges, symlink the whole directory from the normal checkout into Kimi Code's shared user skill directory:

```bash
REPO="$HOME/code/agents-skills-plugins"
mkdir -p "$HOME/.agents/skills"
ln -s "$REPO/skills/diagram-design" "$HOME/.agents/skills/diagram-design"
```

Do not overwrite an existing destination; move or remove it deliberately before creating the link. Copying the whole `diagram-design` directory to the same destination also works. Treat a symlinked install as shared, read-only resources: it points into Eric's checkout, so Seven must never write to its installed `references/style-guide.md` or customize it through markerless onboarding or `load`/`switch`. Start a fresh Seven session, or run `/reload`, then load the skill explicitly with:

```text
/skill:diagram-design
```

For a one-off session without installing, use `--skills-dir`. This replaces automatic user and project skill discovery for that launch, so it is primarily useful for an isolated smoke test:

```bash
kimi --skills-dir "$REPO/skills"
```

Kimi Code's directory-form discovery and companion-file behavior are documented at <https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html>.

## Use from a Linear ticket

Ask Seven for a diagram in natural language, such as an architecture delta, sequence, flowchart, dependency graph, or service blueprint. The skill selects one of its 45 visual types, loads that type's reference and the style guide, and produces a self-contained HTML file with inline SVG.

Select the skin with a `.diagram-design` marker at the target project's root, containing exactly one line:

```text
profile: <slug>
```

Use the saved profile slug named by the ticket, or `profile: default` for the shipped skin. Marker-first resolution reads the selected profile directly and leaves the installed `references/style-guide.md` byte-for-byte unchanged. Never write to that installed file during a Linear session, including through custom onboarding or a markerless `load`/`switch`.

If an unattended run has no valid marker and the first-diagram branding gate fires, do not pause for the interactive branding question or modify the shared install. Use the marker when the ticket names a skin; otherwise stop and reply `STATUS: NEEDS_YOU Choose a saved diagram-design profile or explicitly approve the default skin.`

Run packaged helpers from the target project's root. Replace `$SKILL_DIR` with the installed path above:

```bash
python3 "$SKILL_DIR/scripts/self_check.py" path/to/diagram.html
python3 "$SKILL_DIR/scripts/export_svg.py" path/to/diagram.html path/to/diagram.svg --system-fonts
```

`self_check.py` checks accessible SVG structure, document completeness, single-file safety, painted geometry within the viewBox, and motion basics. It needs only Python's standard library. SVG export is also dependency-free. Mermaid, draw.io, and Excalidraw import helpers use the standard library too.

PNG export is optional and requires an already provisioned Python Playwright installation and compatible browser. The skill does not install it automatically. Generated templates can request Google Fonts when opened; use system-font or offline output when network access is not wanted.

## Validate and smoke test

From this repository's root:

```bash
node scripts/validate-diagram-design.mjs
```

The validator checks native directory layout, the pinned attribution and licenses, all 45 type references and their light/dark/full examples, local companion links, and Python syntax. It then creates an isolated `.agents/skills/diagram-design` symlink and, through that native install path, loads references and templates, runs the packaged self-check on every primary type example and template, and exports an architecture example to standalone SVG. It uses no network, credentials, package installation, browser, or upstream executable installer.

To prove native Kimi discovery and loading with the installed CLI:

```bash
kimi --skills-dir "$REPO/skills" --output-format stream-json -p '/skill:diagram-design Loading smoke only. Reply exactly DIAGRAM_DESIGN_LOADED and take no other action.'
```

The response proves that Kimi parsed the frontmatter and loaded the skill body from the complete native package; the validation command proves that its companion resources are usable.
