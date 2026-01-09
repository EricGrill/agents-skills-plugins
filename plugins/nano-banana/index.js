#!/usr/bin/env node

/**
 * Nano Banana MCP Server
 * Image generation using Google's Gemini API (Nano Banana / Nano Banana Pro)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs/promises";
import path from "path";

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const OUTPUT_DIR = process.env.NANO_BANANA_OUTPUT_DIR || "./public/blog";

// Model configurations
const MODELS = {
  flash: "gemini-2.0-flash-exp",
  pro: "gemini-2.0-flash-exp"
};

const server = new Server(
  {
    name: "nano-banana",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "generate_image",
        description: "Generate an image using Nano Banana (Gemini). Returns the path to the saved image file.",
        inputSchema: {
          type: "object",
          properties: {
            prompt: {
              type: "string",
              description: "Detailed description of the image to generate",
            },
            filename: {
              type: "string",
              description: "Output filename (without extension, .png will be added)",
            },
            outputDir: {
              type: "string",
              description: "Output directory relative to project root (default: public/blog)",
            },
            aspectRatio: {
              type: "string",
              enum: ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"],
              description: "Aspect ratio for the generated image (default: 16:9)",
            },
            model: {
              type: "string",
              enum: ["flash", "pro"],
              description: "Model to use: flash (fast) or pro (higher quality). Default: flash",
            },
          },
          required: ["prompt", "filename"],
        },
      },
      {
        name: "generate_blog_images",
        description: "Generate a complete set of images for a blog post (hero + section images)",
        inputSchema: {
          type: "object",
          properties: {
            slug: {
              type: "string",
              description: "Blog post slug (used for output directory)",
            },
            heroPrompt: {
              type: "string",
              description: "Prompt for the hero/featured image",
            },
            sectionPrompts: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  name: { type: "string", description: "Section image name" },
                  prompt: { type: "string", description: "Image prompt" },
                },
                required: ["name", "prompt"],
              },
              description: "Array of section image prompts",
            },
            style: {
              type: "string",
              description: "Style guidelines to append to all prompts (e.g., brand colors)",
            },
          },
          required: ["slug", "heroPrompt"],
        },
      },
    ],
  };
});

// Generate image using Gemini API
async function generateImage(prompt, options = {}) {
  const {
    aspectRatio = "16:9",
    model = "flash",
  } = options;

  if (!GEMINI_API_KEY) {
    throw new Error("GEMINI_API_KEY environment variable is not set");
  }

  const modelId = MODELS[model] || MODELS.flash;
  const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelId}:generateContent?key=${GEMINI_API_KEY}`;

  const requestBody = {
    contents: [
      {
        parts: [
          {
            text: prompt,
          },
        ],
      },
    ],
    generationConfig: {
      responseModalities: ["TEXT", "IMAGE"],
    },
  };

  const response = await fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Gemini API error: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  // Extract image from response
  const candidates = data.candidates || [];
  for (const candidate of candidates) {
    const parts = candidate.content?.parts || [];
    for (const part of parts) {
      if (part.inlineData?.mimeType?.startsWith("image/")) {
        return {
          data: part.inlineData.data,
          mimeType: part.inlineData.mimeType,
        };
      }
    }
  }

  throw new Error("No image found in API response");
}

// Save image to file
async function saveImage(imageData, outputPath) {
  const dir = path.dirname(outputPath);
  await fs.mkdir(dir, { recursive: true });

  const buffer = Buffer.from(imageData, "base64");
  await fs.writeFile(outputPath, buffer);

  return outputPath;
}

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === "generate_image") {
      const { prompt, filename, outputDir, aspectRatio, model } = args;

      const result = await generateImage(prompt, { aspectRatio, model });

      const ext = result.mimeType === "image/jpeg" ? "jpg" : "png";
      const outDir = outputDir || OUTPUT_DIR;
      const outputPath = path.join(process.cwd(), outDir, `${filename}.${ext}`);

      await saveImage(result.data, outputPath);

      return {
        content: [
          {
            type: "text",
            text: `Image generated successfully!\nSaved to: ${outputPath}\nRelative path: /${outDir}/${filename}.${ext}`,
          },
        ],
      };
    }

    if (name === "generate_blog_images") {
      const { slug, heroPrompt, sectionPrompts = [], style = "" } = args;

      const outDir = path.join(OUTPUT_DIR, slug);
      const results = [];

      // Generate hero image
      const styledHeroPrompt = style ? `${heroPrompt}. ${style}` : heroPrompt;
      const heroResult = await generateImage(styledHeroPrompt, { aspectRatio: "16:9" });
      const heroPath = path.join(process.cwd(), outDir, "hero.png");
      await saveImage(heroResult.data, heroPath);
      results.push({ name: "hero", path: `/${outDir}/hero.png` });

      // Generate section images
      for (const section of sectionPrompts) {
        const styledPrompt = style ? `${section.prompt}. ${style}` : section.prompt;
        const sectionResult = await generateImage(styledPrompt, { aspectRatio: "16:9" });
        const sectionPath = path.join(process.cwd(), outDir, `${section.name}.png`);
        await saveImage(sectionResult.data, sectionPath);
        results.push({ name: section.name, path: `/${outDir}/${section.name}.png` });
      }

      return {
        content: [
          {
            type: "text",
            text: `Blog images generated successfully!\n\nGenerated ${results.length} images:\n${results.map(r => `- ${r.name}: ${r.path}`).join("\n")}`,
          },
        ],
      };
    }

    return {
      content: [
        {
          type: "text",
          text: `Unknown tool: ${name}`,
        },
      ],
      isError: true,
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Nano Banana MCP server running");
}

main().catch(console.error);
