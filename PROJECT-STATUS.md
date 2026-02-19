# agents-skills-plugins — Project Status

## Overview
Community marketplace/registry repo for Claude Code plugins, skills, and agents; acts as a discovery/install catalog rather than a runtime application.

## Current State
- Mature content repository centered on a large README catalog and `plugins/` metadata/content.
- README advertises broad inventory (49 plugins, 70+ agents, 110+ skills).
- Active maintenance includes syncing upstream plugin sources and adding MCP-focused plugin entries.
- Not a deployable web app in this repo; primary deliverable is marketplace/catalog content.

## Architecture
- Repo structure is simple:
  - `README.md` as primary marketplace UI/documentation
  - `plugins/` directory with plugin definitions/assets
  - `.claude-plugin` and GitHub workflow config for ecosystem integration/automation
- No root `package.json` runtime or service architecture present.

## Deploy Info
- Distribution model: consumed via Claude Code plugin commands (documented in README):
  - `/plugin marketplace add EricGrill/agents-skills-plugins`
  - `/plugin install <plugin>@agents-skills-plugins`
- Hosting/runtime deployment: N/A for this repository (catalog repo).
- Environment variables: None required at repository level.

## Recent Changes
- 2026-02-18: Added new skill `skills/picoclaw-fleet/` with `SKILL.md`, deploy/dispatch/status scripts, and README for orchestrating PicoClaw SSH worker fleets. Commit: `81975c8`.
- 2026-01-13: Added blog guide links to MCP server entries.
- 2026-01-12: Added 8 EricGrill MCP servers to README.
- 2026-01-12: Added 5 more EricGrill MCP plugins.
- 2026-01-11: Added `mcp-multi-agent-ssh` and `mcp-kali-orchestration` plugins.
- 2026-01-11: Synced plugins from upstream sources and updated superpowers to v4.0.3.

## Open Tasks / TODO
1. Keep plugin counts/catalog metadata accurate as entries evolve.
2. Add stronger validation/QA tooling for plugin metadata consistency.
3. Improve contributor documentation for adding/updating plugin entries safely.
4. Track stale/abandoned plugins and define deprecation policy.

## Known Issues
- Catalog scale introduces drift risk between README summaries and actual plugin data.
- Quality/reliability of listed third-party plugins varies by upstream maintainer.
- No obvious in-repo automated integrity checks were confirmed (Needs investigation).

## Decisions Log
- Product decision: centralize discovery into one installable marketplace source.
- Ecosystem decision: aggregate plugins from multiple authors rather than only first-party packages.
- UX decision: command-driven install flow inside Claude Code (`/plugin ...`) for low-friction adoption.
- Content strategy: include educational guides/blog links alongside plugin listings to improve adoption and usage quality.