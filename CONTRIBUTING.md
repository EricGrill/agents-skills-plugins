# Contributing to Agents, Skills & Plugins

Thank you for your interest in contributing! This repository is a curated collection of Claude Code skills, agents, and MCP plugins.

## Quick Start

1. **Fork** the repository
2. **Create a branch** for your contribution: `git checkout -b add-my-skill`
3. **Add your skill/agent/plugin** following the structure below
4. **Test** it locally with Claude Code
5. **Submit a PR** with a clear description

## Repository Structure

```
agents/          # Autonomous agents (multi-step workflows)
skills/          # Individual capabilities (single-purpose tools)
plugins/         # MCP server integrations
prompts/         # Reusable system prompts
tools/           # Utility scripts and helpers
```

## Adding a Skill

Skills go in `skills/<category>/<skill-name>/`:

```
skills/web/scrape-website/
├── SKILL.md          # Required: Purpose, usage, examples
├── main.py           # Entry point (if applicable)
└── README.md         # Optional: Extended documentation
```

**SKILL.md template:**
```markdown
# Skill Name

## Purpose
One-line description of what this skill does.

## Usage
How to invoke the skill from Claude Code.

## Examples
Example prompts that trigger this skill.

## Requirements
Any dependencies or setup needed.
```

## Adding an Agent

Agents go in `agents/<agent-name>/`:

```
agents/my-custom-agent/
├── AGENT.md          # Required: Purpose, behavior, triggers
├── prompts/          # System prompts
├── tools/            # Custom tools
└── README.md
```

## Adding a Plugin (MCP)

MCP plugins go in `plugins/<plugin-name>/`:

```
plugins/my-mcp-server/
├── README.md         # Installation and usage
├── package.json      # If Node.js-based
└── src/              # Source code
```

## Quality Guidelines

Before submitting:

- [ ] **Tested**: You've actually used this with Claude Code
- [ ] **Documented**: Clear SKILL.md or AGENT.md explaining purpose and usage
- [ ] **Focused**: Does one thing well (skills) or has clear scope (agents)
- [ ] **Safe**: No hardcoded secrets, respects user privacy
- [ ] **Portable**: Works across different setups when possible

## PR Template

```markdown
**Type:** Skill / Agent / Plugin / Prompt / Tool

**Name:** Brief name

**Description:** What it does and why it's useful

**Testing:** How you tested it

**Checklist:**
- [ ] Added SKILL.md/AGENT.md
- [ ] Tested with Claude Code
- [ ] No secrets or sensitive data
- [ ] Follows repository structure
```

## Review Process

1. PR submitted → Automatic checks run
2. Maintainers review within 48 hours
3. Feedback addressed
4. Merged to main

## Questions?

Open an issue with the `question` label or reach out in discussions.

## License

By contributing, you agree that your contributions will be licensed under the same license as the repository (MIT).
