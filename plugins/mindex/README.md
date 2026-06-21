# MIndex - Auditable, Version-Controlled Memory for Claude Code

MIndex is a structured, long-term memory system for Claude Code that stores verified facts, preferences, and project decisions in plain Markdown files with auto-generated indexing.

## Skills

| Command | Description |
|---------|-------------|
| /mindex:setup | Install or reconnect MIndex as cross-project Claude Code memory |
| /mindex:remember | Save filtered, long-term memory to the MIndex store |
| /mindex:recall | Search historical memory by topic |
| /mindex:doctor | Check installation, index integrity, locks, and privacy |

## Features

- Auditable - all memories are plain Markdown, version-controlled with Git
- Cross-project - single memory store shared across all Claude Code workspaces
- Zero dependencies - standard library only, no pip install required
- Privacy-safe - user confirms what gets saved; full conversations never leak
- Complements Auto Memory - works alongside Claude Code's built-in per-repo memory

## Quick Install

From this marketplace: /plugin install mindex@agents-skills-plugins
From GitHub directly: claude --plugin-dir /path/to/mindex/plugin

## License

MIT
