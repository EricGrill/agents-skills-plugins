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

Do not overwrite an existing destination; move or remove it deliberately before creating the link. Copying the whole `taste-skill` directory to the same destination also works. Start a fresh Seven session after installing so native discovery includes the package.

Seven's Linear sessions run headlessly with `kimi -p`. `/reload` is interactive-only, and `/skill:design-taste-frontend` is not reliably expanded in headless mode. Instead, put an explicit tool instruction in the Linear ticket:

```text
Before starting, call the Skill tool with skill design-taste-frontend. Then follow the loaded skill for this design ticket.
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

The inspector requires Node 22+ and an installed Chrome, Edge, or Chromium. It launches the existing browser with a temporary profile, serves local files on loopback, and writes screenshots plus `report.json` under `.taste-skill/inspect/` by default. It installs nothing. Set `CHROME_PATH` only when the browser is in a nonstandard location. The draw, lint, and asset scripts otherwise have no npm dependencies; open-collection image searches require network access but no API keys. The scripts can write generated artifacts under `.taste-skill/` in the target project; do not include those artifacts in ticket PRs.

Read `references/critique.md` and inspect every screenshot before completing a public-facing design ticket. Reference-image metadata is in `library/photos.json` and `library/sites.json`; imagery licensing and credits are covered by `references/imagery.md` and the upstream [README](README.md).

## Validate and smoke test

From this repository's root:

```bash
node scripts/validate-taste-skill.mjs
node scripts/validate-taste-skill.mjs --browser
node scripts/validate-taste-skill.mjs --native
```

The first command checks native directory layout, required companion resources, JSON and JavaScript integrity, upstream unit tests, and a seeded art-direction draw using isolated temporary state. The second also runs the real-browser inspector at 1440, 768, and 390 against a local fixture and verifies all screenshots. Browser design findings on the fixture are not treated as packaging failures; failure to produce a complete three-width report is.

The third command requires an authenticated `kimi` on `PATH`. It prompts Kimi to call the `Skill` tool explicitly against a symlinked installation in an isolated skills directory. The test fails unless the transcript contains a `Skill "design-taste-frontend" loaded inline.` tool result and the model recovers `# tasteskill v2` from the loaded body. It then repeats the prompt against an empty skills directory and requires a `not found` tool result, so a cooperative text response cannot make the smoke test pass.
