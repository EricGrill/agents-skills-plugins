import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { config } from "./config.js";
import { DockerBackend } from "./backends/docker.js";
import { ProxmoxBackend } from "./backends/proxmox.js";
import type { Backend } from "./backends/interface.js";
import { registerLifecycleTools } from "./tools/lifecycle.js";
import { registerReconTools } from "./tools/recon.js";
import { registerWebTools } from "./tools/web.js";
import { registerExploitTools } from "./tools/exploit.js";
import { registerPasswordTools } from "./tools/passwords.js";
import { registerPostExploitTools } from "./tools/post-exploit.js";
import { registerNetworkTools } from "./tools/network.js";

export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, unknown>;
    required?: string[];
  };
  handler: (args: Record<string, unknown>) => Promise<{
    content: Array<{ type: "text"; text: string }>;
    isError?: boolean;
  }>;
}

export class McpKaliServer {
  private server: Server;
  private backend: Backend;
  private tools: Map<string, ToolDefinition> = new Map();

  constructor() {
    this.server = new Server(
      {
        name: "mcp-kali",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Initialize backend based on config
    if (config.backend === "docker") {
      this.backend = new DockerBackend(config.docker);
    } else if (config.backend === "proxmox") {
      if (!config.proxmox) {
        throw new Error("Proxmox backend selected but not configured");
      }
      this.backend = new ProxmoxBackend(config.proxmox);
    } else {
      throw new Error(`Unknown backend: ${config.backend}`);
    }

    this.setupHandlers();
    this.registerTools();
  }

  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: Array.from(this.tools.values()).map((tool) => ({
          name: tool.name,
          description: tool.description,
          inputSchema: tool.inputSchema,
        })),
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const tool = this.tools.get(request.params.name);

      if (!tool) {
        return {
          content: [
            {
              type: "text" as const,
              text: `Unknown tool: ${request.params.name}`,
            },
          ],
          isError: true,
        };
      }

      try {
        const args = (request.params.arguments || {}) as Record<string, unknown>;
        return await tool.handler(args);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return {
          content: [
            {
              type: "text" as const,
              text: `Error executing ${request.params.name}: ${message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  private registerTools(): void {
    // Register lifecycle tools (kali_start, kali_stop, kali_list, etc.)
    registerLifecycleTools(this.backend, this.tools);

    // Register reconnaissance tools (nmap, whois, etc.)
    registerReconTools(this.backend, this.tools);

    // Register web application testing tools (nikto, sqlmap, etc.)
    registerWebTools(this.backend, this.tools);

    // Register exploitation tools (metasploit, searchsploit, etc.)
    registerExploitTools(this.backend, this.tools);

    // Register password attack tools (hydra, john, hashcat, etc.)
    registerPasswordTools(this.backend, this.tools);

    // Register post-exploitation tools (impacket, crackmapexec, etc.)
    registerPostExploitTools(this.backend, this.tools);

    // Register network tools (netcat, tcpdump, responder, etc.)
    registerNetworkTools(this.backend, this.tools);

    console.error(`Registered ${this.tools.size} tools`);
  }

  registerTool(tool: ToolDefinition): void {
    this.tools.set(tool.name, tool);
  }

  async run(): Promise<void> {
    // Check if backend is available
    const available = await this.backend.isAvailable();
    if (!available) {
      console.error(
        `Backend (${config.backend}) is not available. Please check your configuration.`
      );
      process.exit(1);
    }

    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("MCP Kali server running on stdio");
  }
}
