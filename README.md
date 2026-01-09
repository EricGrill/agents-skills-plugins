# Agent Skills Plugins

A curated collection of Claude Code skills and agents by Eric Grill.

## Installation

Add this marketplace:
```
/plugin marketplace add EricGrill/agents-skills-plugins
```

## Available Plugins

### nano-banana

Image generation MCP server using Google's Gemini API.

```
/plugin install nano-banana@agents-skills-plugins
```

**Tools:**
- `generate_image` - Generate a single image from a text prompt
- `generate_blog_images` - Generate a complete set of images for a blog post

**Requires:** `GEMINI_API_KEY` environment variable

### superpowers

Core skills library for Claude Code: TDD, debugging, collaboration patterns, and proven techniques.

```
/plugin install superpowers@agents-skills-plugins
```

**Skills (14):** brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills

**Commands:** `/brainstorm`, `/write-plan`, `/execute-plan`

**Attribution:** Forked from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent (MIT License)

## License

MIT
