# MCP-Multi-Agent-Server-Delegation

**Delegate tasks to isolated Proxmox VMs for secure, sandboxed execution**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![5 Tools](https://img.shields.io/badge/Tools-5-blue.svg)](#-tool-catalog)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![Proxmox](https://img.shields.io/badge/Proxmox-VE-E57000.svg)](https://www.proxmox.com/)
[![MCP](https://img.shields.io/badge/MCP-Server-purple.svg)](https://modelcontextprotocol.io/)

[Quick Start](#-quick-start) | [Tool Catalog](#-tool-catalog) | [Agent Types](#-agent-types) | [Configuration](#-configuration) | [Architecture](#-architecture)

---

## What is this?

An MCP (Model Context Protocol) server that delegates tasks to isolated Proxmox VMs. Run untrusted code, long builds, or user-submitted jobs in complete isolation with automatic cleanup and HTTP callback status reporting.

Perfect for:
- **Untrusted code execution** - Sandboxed VM isolation
- **Build/test pipelines** - Clean environments every time
- **Agent orchestration** - Spawn Claude or custom agents in isolated VMs

> Requires [mcp-proxmox-admin](https://github.com/EricGrill/mcp-proxmox-admin) for VM management.

---

## Quick Start

**1. Add to Claude Code:**

```json
{
  "mcpServers": {
    "delegation": {
      "command": "node",
      "args": ["/path/to/dist/index.js"],
      "env": {
        "CALLBACK_PORT": "8765",
        "PROXMOX_ADMIN_PATH": "/path/to/mcp-proxmox-admin/dist/index.js"
      }
    }
  }
}
```

**2. Or install manually:**

```bash
git clone https://github.com/EricGrill/mcp-multi-agent-server-delegation.git
cd mcp-multi-agent-server-delegation
npm install && npm run build
node dist/index.js
```

---

## Why Use This?

| Feature | Description |
|---------|-------------|
| **Full VM isolation** | Each job runs in its own Proxmox VM - complete sandboxing |
| **Agent flexibility** | Run Claude, shell scripts, or custom binaries |
| **Automatic cleanup** | Ephemeral VMs destroyed after job completion |
| **Status callbacks** | Real-time updates via HTTP webhooks from VMs |
| **Timeout protection** | Jobs killed and VMs destroyed on timeout |

---

## Tool Catalog

| Tool | Description |
|------|-------------|
| `submit_job` | Submit a job manifest for execution in an isolated VM |
| `get_job_status` | Check current status, progress, and timing of a job |
| `get_job_result` | Retrieve output, artifacts, and errors from completed job |
| `cancel_job` | Cancel a running job and destroy its VM |
| `list_jobs` | List all jobs with optional status filter |

---

## All Tools

### Job Submission

| Tool | Parameters | Returns |
|------|------------|---------|
| `submit_job` | `manifest` (task, agentType, files, env, resources, timeout) | `job_id` |

### Job Monitoring

| Tool | Parameters | Returns |
|------|------------|---------|
| `get_job_status` | `job_id` | status, progress, timestamps |
| `get_job_result` | `job_id` | output, artifacts, duration, errors |
| `list_jobs` | `status?` (filter) | Array of job summaries |

### Job Control

| Tool | Parameters | Returns |
|------|------------|---------|
| `cancel_job` | `job_id` | confirmation |

---

## Agent Types

| Type | Command | Use Case |
|------|---------|----------|
| `claude` | Claude CLI | AI-powered task execution |
| `script` | Bash/Python | Build scripts, automation |
| `custom` | Any binary | Specialized tools, compilers |

### Example: Claude Agent

```json
{
  "task": "Review this codebase and create a summary",
  "agentType": "claude",
  "files": [
    { "path": "/workspace/code.py", "content": "base64..." }
  ],
  "timeout": 600
}
```

### Example: Script Agent

```json
{
  "task": "npm test",
  "agentType": "script",
  "agent": { "command": "bash -c 'cd /workspace && npm install && npm test'" },
  "timeout": 300
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CALLBACK_PORT` | Port for HTTP callback server | `8765` |
| `CALLBACK_HOST` | Host/IP for callback URL | `0.0.0.0` |
| `PROXMOX_ADMIN_PATH` | Path to mcp-proxmox-admin | — |
| `DEFAULT_VM_TEMPLATE` | Proxmox template name | `agent-template` |
| `DEFAULT_TIMEOUT` | Job timeout in seconds | `3600` |
| `DEFAULT_CPU` | VM CPU cores | `2` |
| `DEFAULT_MEMORY` | VM memory | `2G` |
| `DEFAULT_DISK` | VM disk size | `10G` |
| `HEARTBEAT_THRESHOLD_SECONDS` | Stale job detection | `120` |
| `CLEANUP_INTERVAL_SECONDS` | Cleanup check interval | `30` |

### Job Manifest Schema

```typescript
interface JobManifest {
  task: string;                    // What to do
  agentType: 'claude' | 'script' | 'custom';
  agent?: {
    command?: string;              // For script/custom
    claudeModel?: string;          // For claude
  };
  files?: Array<{ path: string; content: string }>;
  env?: Record<string, string>;
  resources?: { cpu?: number; memory?: string; disk?: string };
  timeout?: number;
  lifecycle?: 'ephemeral' | 'persistent';
  statusMode?: 'simple' | 'detailed' | 'streaming';
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude / Agent                           │
└─────────────────────────────┬───────────────────────────────────┘
                              │ MCP Protocol
┌─────────────────────────────▼───────────────────────────────────┐
│                 MCP Delegation Server                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Job Manager │  │ Status Store│  │ Callback HTTP Server    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ MCP Protocol
┌─────────────────────────────▼───────────────────────────────────┐
│                    mcp-proxmox-admin                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                     Proxmox VMs                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Job VM 1   │  │   Job VM 2   │  │   Job VM 3   │          │
│  │  → Agent     │  │  → Agent     │  │  → Agent     │          │
│  │  → Callback  │  │  → Callback  │  │  → Callback  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Job Lifecycle

```
submit_job → pending → provisioning → running → success/failed/timeout
                                         ↓
                              VM destroyed (if ephemeral)
```

---

## VM Template Requirements

Your Proxmox VM template should include:

- **Base OS**: Ubuntu/Debian minimal
- **Packages**: `curl`, `jq`, `bash`
- **Claude CLI**: For `claude` agent type
- **Python/Node**: For script execution
- **Network**: Access to callback server URL

---

## Development

```bash
npm run dev      # Run in development mode
npm test         # Run tests
npm run build    # Build for production
```

### Project Structure

```
src/
├── index.ts           # Entry point
├── server.ts          # MCP server with tools
├── store.ts           # In-memory job store
├── callback-server.ts # HTTP callback receiver
├── proxmox-client.ts  # Proxmox MCP client wrapper
├── types.ts           # TypeScript types
├── schemas.ts         # Zod validation schemas
└── config.ts          # Configuration loader
```

---

## Security Considerations

| Protection | Implementation |
|------------|----------------|
| **VM Isolation** | Each job in separate Proxmox VM |
| **Network Segmentation** | VMs in isolated VLAN (configure in Proxmox) |
| **Timeouts** | Automatic job termination on timeout |
| **Ephemeral VMs** | Destroyed after completion by default |
| **Resource Limits** | CPU/memory/disk quotas via Proxmox |

---

## Related Projects

- [mcp-proxmox-admin](https://github.com/EricGrill/mcp-proxmox-admin) - Required for VM management
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

---

## License

MIT
