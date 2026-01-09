# Agent Skills Plugins

A curated collection of Claude Code skills and agents by Eric Grill.

## Installation

Add this marketplace:
```
/plugin marketplace add ericgrill/agent-skills-plugins
```

## Available Plugins

### nano-banana

Image generation MCP server using Google's Gemini API.

```
/plugin install nano-banana@agent-skills-plugins
```

**Tools:**
- `generate_image` - Generate a single image from a text prompt
- `generate_blog_images` - Generate a complete set of images for a blog post

**Requires:** `GEMINI_API_KEY` environment variable

## License

MIT
