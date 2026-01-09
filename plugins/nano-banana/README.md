# Nano Banana

Image generation MCP server using Google's Gemini API.

## Requirements

- Node.js 18+
- Google Gemini API key

## Setup

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Set your API key:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

## Tools

### generate_image

Generate a single image from a text prompt.

**Parameters:**
- `prompt` (required) - Description of the image to generate
- `filename` (required) - Output filename (without extension)
- `outputDir` - Output directory (default: `public/blog`)
- `aspectRatio` - One of: `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`
- `model` - `flash` (fast) or `pro` (higher quality)

### generate_blog_images

Generate a complete set of images for a blog post.

**Parameters:**
- `slug` (required) - Blog post slug for output directory
- `heroPrompt` (required) - Prompt for the hero image
- `sectionPrompts` - Array of `{name, prompt}` for section images
- `style` - Style guidelines appended to all prompts

## Environment Variables

- `GEMINI_API_KEY` - Your Gemini API key (required)
- `NANO_BANANA_OUTPUT_DIR` - Default output directory (default: `./public/blog`)

## License

MIT
