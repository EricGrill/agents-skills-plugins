# Seven native Linear sessions

The native skill name is `design-taste-frontend`. The complete directory must be installed together: `SKILL.md` uses the sibling `references/`, `library/`, `assets/`, and `scripts/` resources at runtime. Installing only the Markdown file loses the art-direction library, reference-image metadata, and browser inspector.

This package is opt-in. These instructions do not change Seven's default skill or AgentBridge's text-injection configuration.

## Install for native discovery

After this package merges, symlink the whole directory from the normal checkout into Kimi Code's shared user skill directory:

```bash
REPO="$HOME/code/agents-skills-plugins"
mkdir -p "$HOME/.agents/skills"
ln -s "$REPO/skills/taste-skill" "$HOME/.agents/skills/design-taste-frontend"
```

Do not overwrite an existing destination; move or remove it deliberately before creating the link. Copying the whole `taste-skill` directory to the same destination also works. Start a fresh Seven session, or run `/reload`, then load the skill explicitly with:

```text
/skill:design-taste-frontend
```

For a one-off session without installing, use `--skills-dir`. This replaces automatic user and project skill discovery for that launch, so it is primarily useful for an isolated smoke test:

```bash
kimi --skills-dir "$REPO/skills"
```

Kimi Code's directory-form discovery and companion-file behavior are documented at <https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html>.

## Use from a design ticket

Run the commands from the target project's root, not from the skill directory. Replace `$SKILL_DIR` with the installed path above:

```bash
node "$SKILL_DIR/scripts/draw.mjs" --sector saas --brief "One line about the subject" --options 3
node "$SKILL_DIR/scripts/lint.mjs" path/to/source
node "$SKILL_DIR/scripts/inspect.mjs" path/to/index.html --widths 1440,768,390
```

The inspector requires Node 22+ and an installed Chrome, Edge, or Chromium. It launches the existing browser with a temporary profile, serves local files on loopback, and writes screenshots plus `report.json` under `.taste-skill/inspect/` by default. It installs nothing. Set `CHROME_PATH` only when the browser is in a nonstandard location. The draw, lint, and asset scripts otherwise have no npm dependencies; open-collection image searches require network access but no API keys.

Read `references/critique.md` and inspect every screenshot before completing a public-facing design ticket. Reference-image metadata is in `library/photos.json` and `library/sites.json`; imagery licensing and credits are covered by `references/imagery.md` and the upstream [README](README.md).

## Validate and smoke test

From this repository's root:

```bash
node scripts/validate-taste-skill.mjs
node scripts/validate-taste-skill.mjs --browser
```

The first command checks native directory layout, required companion resources, JSON and JavaScript integrity, upstream unit tests, and a seeded art-direction draw using isolated temporary state. The second also runs the real-browser inspector at 1440, 768, and 390 against a local fixture and verifies all screenshots. Browser design findings on the fixture are not treated as packaging failures; failure to produce a complete three-width report is.

To prove native Kimi discovery and loading with the installed CLI:

```bash
kimi --skills-dir "$REPO/skills" --output-format stream-json -p '/skill:design-taste-frontend Loading smoke only. Reply exactly TASTE_SKILL_LOADED and take no other action.'
```

The response proves that Kimi parsed the frontmatter and loaded the skill body from the complete native package; the validation command proves that its companion resources are usable.
