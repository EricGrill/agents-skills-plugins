#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { create, use } from "@memvid/sdk";
import { existsSync, mkdirSync, readdirSync, unlinkSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// Types for memvid SDK
interface MemvidInstance {
  put: (data: {
    text: string;
    title?: string;
    metadata?: Record<string, unknown>;
    labels?: string[];
    enableEmbedding?: boolean;
    embeddingModel?: string;
  }) => Promise<void>;
  find: (
    query: string | undefined,
    options?: { k?: number; mode?: "auto" | "lex" | "sem"; embedder?: unknown }
  ) => Promise<SearchResult[] | { hits: SearchResult[] }>;
  timeline?: (options?: { k?: number }) => Promise<SearchResult[]>;
}

interface SearchResult {
  id?: string;
  title?: string;
  text?: string;
  snippet?: string;
  preview?: string;
  score?: number;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// Embedding Configuration
// =============================================================================

// Supported embedding models
const EMBEDDING_MODELS = {
  // Local models (no API key required, Linux/macOS only)
  local: ["bge-small", "bge-base", "nomic", "gte-large"],
  // OpenAI models (requires OPENAI_API_KEY)
  openai: ["openai-small", "openai-large"],
  // Ollama models (requires OLLAMA_HOST or OPENAI_BASE_URL pointing to Ollama)
  ollama: ["ollama"],
} as const;

// Environment variables
const OLLAMA_HOST = process.env.OLLAMA_HOST || process.env.OLLAMA_BASE_URL;
const DEFAULT_EMBEDDING_MODEL = process.env.MEMVID_EMBEDDING_MODEL || "bge-small";

// Configure Ollama as OpenAI-compatible endpoint if OLLAMA_HOST is set
function configureOllama(): void {
  if (OLLAMA_HOST && !process.env.OPENAI_BASE_URL) {
    // Ollama exposes OpenAI-compatible API at /v1
    const ollamaUrl = OLLAMA_HOST.endsWith("/v1")
      ? OLLAMA_HOST
      : `${OLLAMA_HOST.replace(/\/$/, "")}/v1`;
    process.env.OPENAI_BASE_URL = ollamaUrl;
    console.error(`[mcp-memvid] Configured Ollama at ${ollamaUrl}`);
  }
}

// Get effective embedding model
function getEmbeddingModel(requested?: string): string {
  if (requested) return requested;

  // If Ollama is configured and no specific model requested, use openai-small
  // (which will route through Ollama's OpenAI-compatible API)
  if (OLLAMA_HOST && DEFAULT_EMBEDDING_MODEL === "bge-small") {
    return "openai-small";
  }

  return DEFAULT_EMBEDDING_MODEL;
}

// Get embedding configuration info
function getEmbeddingConfig(): Record<string, unknown> {
  return {
    defaultModel: DEFAULT_EMBEDDING_MODEL,
    effectiveModel: getEmbeddingModel(),
    ollamaHost: OLLAMA_HOST || null,
    openaiBaseUrl: process.env.OPENAI_BASE_URL || null,
    openaiKeySet: !!process.env.OPENAI_API_KEY,
    supportedModels: {
      local: EMBEDDING_MODELS.local,
      openai: EMBEDDING_MODELS.openai,
      note: "For Ollama, set OLLAMA_HOST and use 'openai-small' model",
    },
  };
}

// =============================================================================
// Storage Configuration - XDG compliant
// =============================================================================

const XDG_DATA_HOME =
  process.env.XDG_DATA_HOME || join(homedir(), ".local", "share");
const CAPSULES_DIR = join(XDG_DATA_HOME, "memvid", "capsules");

function ensureCapsuleDir(): void {
  if (!existsSync(CAPSULES_DIR)) {
    mkdirSync(CAPSULES_DIR, { recursive: true });
  }
}

function getCapsulePath(name: string): string {
  ensureCapsuleDir();
  const safeName = name.replace(/[^a-zA-Z0-9_-]/g, "_");
  return join(CAPSULES_DIR, `${safeName}.mv2`);
}

// Cache for open capsules
const capsuleCache = new Map<string, MemvidInstance>();

async function getCapsule(
  name: string,
  createIfNotExists = true
): Promise<MemvidInstance> {
  const cached = capsuleCache.get(name);
  if (cached) return cached;

  const path = getCapsulePath(name);
  let instance: MemvidInstance;

  try {
    if (!existsSync(path)) {
      if (!createIfNotExists) {
        throw new Error(`Capsule '${name}' does not exist`);
      }
      instance = (await create(path)) as unknown as MemvidInstance;
    } else {
      instance = (await use("basic", path)) as unknown as MemvidInstance;
    }
    capsuleCache.set(name, instance);
    return instance;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to access capsule '${name}': ${message}`);
  }
}

function listCapsules(): string[] {
  ensureCapsuleDir();
  return readdirSync(CAPSULES_DIR)
    .filter((f) => f.endsWith(".mv2"))
    .map((f) => f.replace(".mv2", ""));
}

function normalizeResults(
  results: SearchResult[] | { hits: SearchResult[] }
): SearchResult[] {
  return Array.isArray(results) ? results : results.hits || [];
}

// =============================================================================
// Tool Definitions
// =============================================================================

const tools: Tool[] = [
  // Storage tools
  {
    name: "store_memory",
    description:
      "Store information in a memvid capsule with optional vector embeddings for semantic search. Supports local models (bge-small, nomic), OpenAI, or Ollama for embeddings.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description:
            "Name of the capsule (e.g., 'agent-context', 'knowledge-base'). Created automatically if it doesn't exist.",
        },
        text: {
          type: "string",
          description: "The content to store",
        },
        title: {
          type: "string",
          description: "Optional title/identifier for this memory",
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Optional tags for categorization",
        },
        metadata: {
          type: "object",
          description: "Optional key-value metadata",
          additionalProperties: true,
        },
        enable_embedding: {
          type: "boolean",
          description:
            "Generate vector embedding for semantic search. Default: false",
          default: false,
        },
        embedding_model: {
          type: "string",
          description:
            "Embedding model to use. Options: 'bge-small' (local, default), 'bge-base', 'nomic', 'gte-large' (local), 'openai-small', 'openai-large' (requires OPENAI_API_KEY or Ollama)",
        },
      },
      required: ["capsule", "text"],
    },
  },
  {
    name: "delete_capsule",
    description:
      "Delete an entire capsule file. This permanently removes all memories. Requires confirmation.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description: "Name of the capsule to delete",
        },
        confirm: {
          type: "boolean",
          description: "Must be true to confirm deletion",
        },
      },
      required: ["capsule", "confirm"],
    },
  },

  // Search tools
  {
    name: "semantic_search",
    description:
      "Search memories by meaning using vector embeddings. Finds conceptually related content even when exact words don't match.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description: "Name of the capsule to search",
        },
        query: {
          type: "string",
          description: "Natural language query",
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 10)",
          default: 10,
        },
      },
      required: ["capsule", "query"],
    },
  },
  {
    name: "text_search",
    description:
      "Search memories using full-text/keyword search (BM25). Best for exact words, names, or specific terms.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description: "Name of the capsule to search",
        },
        query: {
          type: "string",
          description: "Keywords to search for",
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 10)",
          default: 10,
        },
      },
      required: ["capsule", "query"],
    },
  },
  {
    name: "smart_search",
    description:
      "Search with automatic mode selection - memvid chooses semantic or lexical based on query.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description: "Name of the capsule to search",
        },
        query: {
          type: "string",
          description: "Search query",
        },
        limit: {
          type: "number",
          description: "Maximum results (default: 10)",
          default: 10,
        },
      },
      required: ["capsule", "query"],
    },
  },
  {
    name: "recent_memories",
    description: "Get the most recent memories from a capsule in chronological order.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description: "Name of the capsule to query",
        },
        limit: {
          type: "number",
          description: "Number of recent memories (default: 10)",
          default: 10,
        },
      },
      required: ["capsule"],
    },
  },

  // Capsule management
  {
    name: "list_capsules",
    description: "List all available memory capsules.",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
  {
    name: "create_capsule",
    description: "Create a new empty capsule.",
    inputSchema: {
      type: "object" as const,
      properties: {
        name: {
          type: "string",
          description: "Name for the new capsule",
        },
      },
      required: ["name"],
    },
  },
  {
    name: "capsule_info",
    description: "Get information about a capsule including storage path.",
    inputSchema: {
      type: "object" as const,
      properties: {
        capsule: {
          type: "string",
          description: "Name of the capsule",
        },
      },
      required: ["capsule"],
    },
  },

  // Configuration
  {
    name: "embedding_config",
    description:
      "Get current embedding configuration including available models, Ollama status, and API key status.",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: [],
    },
  },
];

// =============================================================================
// Tool Handlers
// =============================================================================

function formatResult(result: SearchResult): string {
  const title = result.title || "Untitled";
  const content = result.snippet || result.text || result.preview || "";
  const score = result.score !== undefined ? `Score: ${result.score}` : "";
  return `[${title}]\n${content}\n${score}`.trim();
}

async function handleToolCall(
  name: string,
  args: Record<string, unknown>
): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  try {
    switch (name) {
      // Storage tools
      case "store_memory": {
        const capsule = await getCapsule(args.capsule as string);
        const enableEmbedding = (args.enable_embedding as boolean) || false;
        const embeddingModel = enableEmbedding
          ? getEmbeddingModel(args.embedding_model as string | undefined)
          : undefined;

        await capsule.put({
          text: args.text as string,
          title: args.title as string | undefined,
          labels: args.tags as string[] | undefined,
          metadata: args.metadata as Record<string, unknown> | undefined,
          enableEmbedding,
          embeddingModel,
        });

        let response = `Stored memory in capsule '${args.capsule}'`;
        if (args.title) response += ` with title '${args.title}'`;
        if (enableEmbedding) response += ` (embedded with ${embeddingModel})`;

        return {
          content: [{ type: "text", text: response }],
        };
      }

      case "delete_capsule": {
        if (args.confirm !== true) {
          return {
            content: [
              {
                type: "text",
                text: "Deletion not confirmed. Set 'confirm' to true to delete.",
              },
            ],
          };
        }
        const path = getCapsulePath(args.capsule as string);
        if (!existsSync(path)) {
          return {
            content: [{ type: "text", text: `Capsule '${args.capsule}' does not exist` }],
          };
        }
        capsuleCache.delete(args.capsule as string);
        unlinkSync(path);
        return {
          content: [{ type: "text", text: `Deleted capsule '${args.capsule}'` }],
        };
      }

      // Search tools
      case "semantic_search": {
        const capsule = await getCapsule(args.capsule as string, false);
        const results = await capsule.find(args.query as string, {
          k: (args.limit as number) || 10,
          mode: "sem",
        });
        const hits = normalizeResults(results);
        return {
          content: [
            {
              type: "text",
              text: hits.length > 0 ? hits.map(formatResult).join("\n\n---\n\n") : "No results found",
            },
          ],
        };
      }

      case "text_search": {
        const capsule = await getCapsule(args.capsule as string, false);
        const results = await capsule.find(args.query as string, {
          k: (args.limit as number) || 10,
          mode: "lex",
        });
        const hits = normalizeResults(results);
        return {
          content: [
            {
              type: "text",
              text: hits.length > 0 ? hits.map(formatResult).join("\n\n---\n\n") : "No results found",
            },
          ],
        };
      }

      case "smart_search": {
        const capsule = await getCapsule(args.capsule as string, false);
        const results = await capsule.find(args.query as string, {
          k: (args.limit as number) || 10,
          mode: "auto",
        });
        const hits = normalizeResults(results);
        return {
          content: [
            {
              type: "text",
              text: hits.length > 0 ? hits.map(formatResult).join("\n\n---\n\n") : "No results found",
            },
          ],
        };
      }

      case "recent_memories": {
        const capsule = await getCapsule(args.capsule as string, false);
        let hits: SearchResult[];
        if (typeof capsule.timeline === "function") {
          hits = await capsule.timeline({ k: (args.limit as number) || 10 });
        } else {
          const results = await capsule.find(undefined, {
            k: (args.limit as number) || 10,
          });
          hits = normalizeResults(results);
        }
        return {
          content: [
            {
              type: "text",
              text: hits.length > 0 ? hits.map(formatResult).join("\n\n---\n\n") : "No memories found",
            },
          ],
        };
      }

      // Capsule management
      case "list_capsules": {
        const capsules = listCapsules();
        return {
          content: [
            {
              type: "text",
              text:
                capsules.length > 0
                  ? `Available capsules:\n${capsules.map((c) => `  - ${c}`).join("\n")}\n\nStorage: ${CAPSULES_DIR}`
                  : `No capsules found.\nStorage: ${CAPSULES_DIR}`,
            },
          ],
        };
      }

      case "create_capsule": {
        const name = args.name as string;
        const path = getCapsulePath(name);
        if (existsSync(path)) {
          return {
            content: [{ type: "text", text: `Capsule '${name}' already exists at ${path}` }],
          };
        }
        await getCapsule(name, true);
        return {
          content: [{ type: "text", text: `Created capsule '${name}' at ${path}` }],
        };
      }

      case "capsule_info": {
        const name = args.capsule as string;
        const path = getCapsulePath(name);
        const exists = existsSync(path);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ name, path, exists, capsulesDirectory: CAPSULES_DIR }, null, 2),
            },
          ],
        };
      }

      // Configuration
      case "embedding_config": {
        const config = getEmbeddingConfig();
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(config, null, 2),
            },
          ],
        };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
        };
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${message}` }],
    };
  }
}

// =============================================================================
// Main Server
// =============================================================================

async function main() {
  // Configure Ollama if OLLAMA_HOST is set
  configureOllama();

  const server = new Server(
    {
      name: "mcp-memvid",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return { tools };
  });

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    return handleToolCall(
      request.params.name,
      (request.params.arguments as Record<string, unknown>) || {}
    );
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("mcp-memvid server started");
  console.error(`Capsules directory: ${CAPSULES_DIR}`);
  console.error(`Default embedding model: ${getEmbeddingModel()}`);
  if (OLLAMA_HOST) {
    console.error(`Ollama configured: ${OLLAMA_HOST}`);
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
