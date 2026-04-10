# Contributing to Agents Skills Plugins

Thank you for your interest in contributing to the Claude Code Plugin Marketplace! This document provides comprehensive guidelines for submitting new plugins, skills, and agents.

## Table of Contents

- [Quick Start](#quick-start)
- [Contribution Types](#contribution-types)
- [Submission Guidelines](#submission-guidelines)
- [Plugin Structure](#plugin-structure)
- [Quality Standards](#quality-standards)
- [Review Process](#review-process)
- [Legal Requirements](#legal-requirements)

## Quick Start

```bash
# 1. Fork the repository
git clone https://github.com/YOUR_USERNAME/agents-skills-plugins.git
cd agents-skills-plugins

# 2. Create your plugin or skill
# See below for structure requirements

# 3. Test with Claude Code
# Ensure your plugin works as expected

# 4. Submit a Pull Request
# Include detailed description and testing notes
```

## Contribution Types

### 1. New Plugin
A complete plugin with multiple skills, agents, and/or commands.

**Best for:** Comprehensive functionality, curated workflows, multi-step capabilities

### 2. Individual Skill
A single SKILL.md file that teaches Claude a specific capability.

**Best for:** Specific techniques, reusable patterns, single-purpose workflows

### 3. Agent Definition
A specialized agent configuration for delegated tasks.

**Best for:** Background processing, independent workflows, specialized expertise

### 4. Command Extension
A new slash command for Claude Code.

**Best for:** Quick actions, frequently used operations, user convenience

## Submission Guidelines

### Before Submitting

- [ ] Ensure your contribution is original or properly attributed
- [ ] Test thoroughly with Claude Code
- [ ] Follow naming conventions (lowercase-with-hyphens)
- [ ] Include comprehensive documentation
- [ ] Add appropriate tags/categories

### Naming Conventions

| Type | Format | Example |
|------|--------|---------|
| Plugins | descriptive-name | `python-development` |
| Skills | verb-noun or noun-verb | `debug-python`, `python-debugger` |
| Agents | role-description | `code-reviewer`, `test-writer` |
| Commands | action | `/format-code`, `/run-tests` |

### Categories

Choose the most relevant category:

- **ai-ml** - AI/ML development, LLM tooling
- **backend** - Server-side development, APIs, databases
- **blockchain** - Web3, smart contracts, crypto
- **data** - Data science, analytics, visualization
- **devops** - CI/CD, infrastructure, deployment
- **frontend** - UI/UX, React, Vue, CSS
- **mobile** - iOS, Android, React Native
- **security** - Security auditing, penetration testing
- **testing** - Unit tests, e2e, QA automation
- **utilities** - General productivity tools

## Plugin Structure

### Standard Plugin Directory Layout

```
plugins/your-plugin-name/
├── README.md              # Required: Plugin documentation
├── LICENSE               # Required: MIT recommended
├── plugin.json           # Required: Plugin manifest
├── CHANGELOG.md          # Recommended: Version history
├── CONTRIBUTING.md       # Optional: Contribution guidelines
│
├── skills/               # Skill definitions
│   ├── skill-name/
│   │   ├── SKILL.md
│   │   └── (assets)
│   └── ...
│
├── agents/               # Agent definitions
│   └── agent-name.json
│
├── commands/             # Command definitions
│   └── command-name.json
│
└── assets/               # Static assets
    └── images/
```

### Required: plugin.json

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "Brief description of what this plugin does",
  "author": "Your Name <email@example.com>",
  "license": "MIT",
  "categories": ["backend", "testing"],
  "tags": ["python", "pytest", "tdd"],
  "requires": {
    "claude-code": ">=1.0.0"
  },
  "dependencies": {
    "plugins": ["superpowers@>=3.0.0"],
    "skills": [],
    "commands": []
  },
  "conflicts": [],
  "skills": ["skill-one", "skill-two"],
  "agents": ["agent-one"],
  "commands": ["/command-one"],
  "repository": "https://github.com/username/repo",
  "homepage": "https://example.com/docs",
  "bugs": "https://github.com/username/repo/issues"
}
```

### Required: README.md Template

```markdown
# Plugin Name

Brief one-line description.

## Description

Longer description of what this plugin does, who it's for, and why it's useful.

## Features

- Feature one with description
- Feature two with description
- Feature three with description

## Installation

\`\`\`bash
/plugin install your-plugin-name@agents-skills-plugins
\`\`\`

## Usage

### Skill: skill-name

Description of when to use this skill.

\`\`\`bash
# Example usage
/skill-name
\`\`\`

### Command: /command-name

Description of command.

\`\`\`bash
/command-name arg1 arg2
\`\`\`

## Requirements

- Claude Code >= 1.0.0
- Any other requirements

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)
```

## Quality Standards

### Documentation Requirements

All submissions must include:

1. **Clear description** - What does it do and why?
2. **Usage examples** - Concrete command/skill usage
3. **Installation instructions** - How to install
4. **Requirements** - Dependencies and prerequisites
5. **Troubleshooting** - Common issues and solutions

### Code Quality

- Skills should follow established patterns from `superpowers`
- Commands should have clear, consistent naming
- Agents should have specific, focused responsibilities
- Test your contribution thoroughly before submitting

### Security

- No hardcoded secrets or API keys
- No malicious code or commands
- Respect user privacy
- Clear data handling practices

## Review Process

### Submission Steps

1. **Fork & Branch**
   ```bash
   git checkout -b add-your-plugin-name
   ```

2. **Add Your Plugin**
   - Place in appropriate directory
   - Include all required files
   - Update main README.md catalog

3. **Test Locally**
   ```bash
   # Verify plugin structure
   ls -la plugins/your-plugin/
   
   # Check JSON validity
   cat plugins/your-plugin/plugin.json | python -m json.tool
   ```

4. **Submit PR**
   - Use clear title: "Add: plugin-name"
   - Fill out PR template
   - Reference any related issues

### Review Criteria

| Criteria | Weight | Description |
|----------|--------|-------------|
| Documentation | 30% | Clear, complete README |
| Functionality | 25% | Works as advertised |
| Code Quality | 20% | Follows best practices |
| Originality | 15% | Unique or better than alternatives |
| Maintenance | 10% | Likely to be maintained |

### Timeline

- **Initial Review:** 3-5 days
- **Feedback Integration:** 1-2 iterations typical
- **Final Merge:** Within 2 weeks of approval

## Legal Requirements

### Licensing

- All contributions must be MIT licensed
- Include LICENSE file in plugin directory
- Respect upstream licenses when forking

### Attribution

- Credit original authors when forking
- Include links to upstream repositories
- Respect attribution requirements

### CLA

By submitting a PR, you agree that:

1. You have the right to submit this contribution
2. Your contribution is original or properly licensed
3. You grant maintainers the right to distribute your contribution

## Getting Help

- **Discord:** [Join our community](https://discord.gg/example)
- **Issues:** [Open an issue](https://github.com/EricGrill/agents-skills-plugins/issues)
- **Discussions:** [GitHub Discussions](https://github.com/EricGrill/agents-skills-plugins/discussions)

## Recognition

Contributors will be:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Eligible for maintainer status after 5+ quality contributions

---

Thank you for making Claude Code better for everyone! 🚀
