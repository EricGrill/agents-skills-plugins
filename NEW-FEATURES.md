# New Features Documentation

This document describes the new features added to address open issues in the agents-skills-plugins repository.

---

## Issue #20: Enhanced CONTRIBUTING.md ✅

**Location:** `CONTRIBUTING.md`

Comprehensive contribution guidelines including:
- Quick start guide
- Contribution types (plugins, skills, agents, commands)
- Submission guidelines with checklists
- Naming conventions by type
- Categories taxonomy
- Standard plugin directory layout
- Required `plugin.json` manifest with full schema
- README.md template
- Quality standards and security requirements
- Review process with scoring rubric
- Legal requirements and CLA

---

## Issue #24: Plugin Bundles/Presets ✅

**Location:** `bundles/bundles.json`

8 curated plugin bundles for common workflows:

| Bundle | Description | Plugins Included |
|--------|-------------|------------------|
| `web-developer` | Web development essentials | superpowers, javascript-typescript, git-pr-workflows, unit-testing |
| `data-scientist` | Data science toolkit | superpowers, python-development, business-analytics, ai-investigator |
| `devops-engineer` | DevOps & infrastructure | superpowers, multi-agent-patterns, mcp-multi-agent-ssh, mcp-proxmox-admin |
| `security-analyst` | Security & pentesting | superpowers, mcp-kali-orchestration, frontend-mobile-security |
| `mobile-developer` | Mobile app development | superpowers, frontend-mobile-development, ios-simulator-skill |
| `blockchain-developer` | Web3 & blockchain | superpowers, blockchain-web3, mcp-bitcoin-cli |
| `content-creator` | SEO & content tools | superpowers, seo-content-creation, readwren, ralph-wiggum-marketer |
| `team-lead` | Team collaboration | superpowers, team-collaboration, git-pr-workflows |

**Install command:** `/plugin bundle <bundle-name>`

---

## Issue #26: Plugin Dependency Management ✅

**Location:** `schemas/plugin-manifest.json`

JSON Schema for `plugin.json` manifests including:
- Standard metadata (name, version, author, license)
- Categories and tags
- System requirements (claude-code version, node version, platforms)
- Dependencies:
  - `plugins`: Array of required plugins with version constraints
  - `skills`: Required skills
  - `commands`: Required commands
- Conflicts: Incompatible plugins with reasons and alternatives
- Assets: icons, screenshots

**Example dependency declaration:**
```json
{
  "dependencies": {
    "plugins": ["superpowers@>=3.0.0", "git-pr-workflows"],
    "skills": ["test-driven-development"],
    "commands": ["/write-plan"]
  },
  "conflicts": [
    {
      "plugin": "old-git-plugin",
      "reason": "Conflicting git command handlers",
      "alternative": "git-pr-workflows"
    }
  ]
}
```

---

## Issue #23: Quality Scoring System ✅

**Location:** `docs/QUALITY-SCORING.md`

Automated quality scoring with 5 categories:
- Documentation (30%) - README completeness, examples
- Functionality (25%) - Works as advertised
- Code Quality (20%) - Security, best practices
- Maintenance (15%) - Recent activity, issue response
- Community (10%) - Stars, forks, contributors

**Badges:**
- Platinum (90-100) - Exceptional quality
- Gold (75-89) - High quality, recommended
- Silver (60-74) - Good quality
- Bronze (40-59) - Acceptable
- Needs Work (0-39) - Needs improvement

**API endpoint:** `GET /api/scores/{plugin-name}`

---

## Issue #22: Interactive Plugin Discovery ✅

**Location:** `plugins-index.json`

Comprehensive plugin index with:
- Searchable plugin catalog (70 plugins)
- Category filtering with icons
- Quality score integration
- Sort options (name, rating, downloads, updated)
- Command index
- Bundle references
- Plugin statistics (skills, agents, commands counts)

**Search fields:** name, description, tags, author, skills, commands

**Usage:**
```bash
# Search for plugins
/plugin search python
/plugin search --category backend
/plugin search --quality gold
/plugin search --sort rating
```

---

## Issue #25: Update Notification System ✅

**Location:** `scripts/update-checker.js`

Node.js update checker with:
- Automatic version comparison
- Registry sync from GitHub
- Breaking change detection
- Caching (24-hour interval)
- CLI interface with multiple output formats
- Install command suggestions

**Usage:**
```bash
# Check for updates
node scripts/update-checker.js

# Force check
node scripts/update-checker.js --force

# JSON output
node scripts/update-checker.js --json

# Quiet mode (updates only)
node scripts/update-checker.js --quiet
```

**Integration with Claude Code:**
```
/plugin update          # Update all plugins
/plugin update <name>   # Update specific plugin
/plugin list --updates  # List plugins with updates
```

---

## Summary

| Issue | Feature | Status | Location |
|-------|---------|--------|----------|
| #20 | CONTRIBUTING.md | ✅ Complete | `CONTRIBUTING.md` |
| #24 | Plugin Bundles | ✅ Complete | `bundles/bundles.json` |
| #26 | Dependency Management | ✅ Complete | `schemas/plugin-manifest.json` |
| #23 | Quality Scoring | ✅ Complete | `docs/QUALITY-SCORING.md` |
| #22 | Discovery Index | ✅ Complete | `plugins-index.json` |
| #25 | Update Notifications | ✅ Complete | `scripts/update-checker.js` |

All 6 open issues have been addressed with working implementations.
