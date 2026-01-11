# MCP Proxmox Admin - Design Document

**Date:** 2026-01-11
**Status:** Approved

## Overview

An MCP (Model Context Protocol) server for comprehensive Proxmox VE administration. Enables Claude to manage VMs, containers, and infrastructure through a hybrid SSH + REST API approach.

## Goals

- Full VM and container lifecycle management
- Infrastructure monitoring (nodes, storage, cluster)
- User-configurable transport layer (SSH, API, or auto)
- Open source ready with comprehensive documentation
- No credential leakage in repository

## Project Structure

```
mcp-proxmox-admin/
├── src/
│   ├── index.ts              # MCP server entry point
│   ├── config/
│   │   ├── loader.ts         # Layered config: MCP → env → file
│   │   └── schema.ts         # Config validation (Zod)
│   ├── transports/
│   │   ├── ssh.ts            # SSH command execution
│   │   ├── api.ts            # Proxmox REST API client
│   │   └── index.ts          # Transport selector/router
│   ├── tools/
│   │   ├── vm.ts             # VM operations (qm commands)
│   │   ├── container.ts      # Container operations (pct commands)
│   │   ├── node.ts           # Node/cluster info
│   │   └── storage.ts        # Storage operations
│   └── types/
│       └── proxmox.ts        # TypeScript types for Proxmox entities
├── docs/
│   ├── setup.md              # Detailed setup guide
│   ├── configuration.md      # All config options explained
│   ├── api-reference.md      # Every tool documented
│   ├── troubleshooting.md    # Common issues & solutions
│   ├── architecture.md       # How it works internally
│   └── contributing.md       # How to contribute
├── examples/
│   └── claude-desktop-config.json
├── .env.example              # Template (no real credentials)
├── .gitignore                # Ignores .env, node_modules, etc.
├── README.md                 # Main entry point
├── package.json
└── tsconfig.json
```

## MCP Tools

### VM Operations (`qm` commands)

| Tool | Description |
|------|-------------|
| `proxmox_vm_list` | List all VMs with status, resources |
| `proxmox_vm_start` | Start a VM |
| `proxmox_vm_stop` | Stop a VM |
| `proxmox_vm_restart` | Restart a VM |
| `proxmox_vm_shutdown` | Graceful shutdown |
| `proxmox_vm_create` | Create new VM from template or ISO |
| `proxmox_vm_delete` | Remove VM (requires confirm flag) |
| `proxmox_vm_clone` | Clone existing VM |
| `proxmox_vm_snapshot_create` | Create snapshot |
| `proxmox_vm_snapshot_list` | List snapshots |
| `proxmox_vm_snapshot_restore` | Restore snapshot |
| `proxmox_vm_snapshot_delete` | Delete snapshot |
| `proxmox_vm_config` | Get/set VM configuration |

### Container Operations (`pct` commands)

| Tool | Description |
|------|-------------|
| `proxmox_ct_list` | List all containers |
| `proxmox_ct_start` | Start a container |
| `proxmox_ct_stop` | Stop a container |
| `proxmox_ct_restart` | Restart a container |
| `proxmox_ct_create` | Create new container |
| `proxmox_ct_delete` | Remove container (requires confirm flag) |
| `proxmox_ct_clone` | Clone existing container |
| `proxmox_ct_snapshot_create` | Create snapshot |
| `proxmox_ct_snapshot_list` | List snapshots |
| `proxmox_ct_snapshot_restore` | Restore snapshot |
| `proxmox_ct_snapshot_delete` | Delete snapshot |

### Node & Cluster

| Tool | Description |
|------|-------------|
| `proxmox_node_status` | CPU, memory, uptime per node |
| `proxmox_node_list` | All nodes in cluster |
| `proxmox_cluster_status` | Overall cluster health |

### Storage

| Tool | Description |
|------|-------------|
| `proxmox_storage_list` | Available storage pools |
| `proxmox_storage_content` | ISOs, templates, backups on a storage |

### Common Parameters

All tools accept a `transport` parameter: `"ssh"`, `"api"`, or `"auto"` (uses config default).

## Configuration System

### Priority Order (highest to lowest)

1. MCP client settings (passed when launching server)
2. Environment variables
3. Config file (`proxmox-config.json`)

### Configuration Schema

```typescript
{
  // Connection
  host: string;           // Proxmox host/IP
  port?: number;          // API port (default: 8006)

  // Authentication - API
  apiTokenId?: string;    // e.g., "user@pam!tokenname"
  apiTokenSecret?: string;
  verifySsl?: boolean;    // default: true

  // Authentication - SSH
  sshUser?: string;
  sshPort?: number;       // default: 22
  sshKeyPath?: string;    // path to private key
  sshPassword?: string;   // alternative to key

  // Behavior
  defaultTransport: "ssh" | "api" | "auto";  // default: "auto"
  defaultNode?: string;   // for single-node setups
  timeout?: number;       // command timeout in ms
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PROXMOX_HOST` | Proxmox host/IP |
| `PROXMOX_PORT` | API port (default: 8006) |
| `PROXMOX_API_TOKEN_ID` | API token ID |
| `PROXMOX_API_TOKEN_SECRET` | API token secret |
| `PROXMOX_VERIFY_SSL` | Verify SSL certificates |
| `PROXMOX_SSH_USER` | SSH username |
| `PROXMOX_SSH_PORT` | SSH port (default: 22) |
| `PROXMOX_SSH_KEY_PATH` | Path to SSH private key |
| `PROXMOX_SSH_PASSWORD` | SSH password (alternative to key) |
| `PROXMOX_DEFAULT_TRANSPORT` | Default transport mode |
| `PROXMOX_DEFAULT_NODE` | Default node for operations |
| `PROXMOX_TIMEOUT` | Command timeout in ms |

## Transport Layer

### Architecture

```typescript
interface Transport {
  execute(command: string, options?: ExecOptions): Promise<Result>;
  query(endpoint: string, params?: object): Promise<Result>;
}

class SSHTransport implements Transport {
  // Uses ssh2 library
  // Executes: qm, pct, pvesh commands directly
}

class APITransport implements Transport {
  // HTTPS calls to Proxmox REST API
  // Uses apiTokenId + apiTokenSecret for auth
}
```

### Auto Mode Decision Logic

| Operation Type | Preferred Transport | Reason |
|---------------|---------------------|--------|
| List/query operations | API | Structured JSON response, faster |
| Status checks | API | Real-time data, no parsing needed |
| Start/stop/restart | API | Reliable, returns task ID |
| Create/delete | SSH | Direct control, clearer error messages |
| Snapshots | SSH | `qm snapshot` more reliable than API |
| Config changes | SSH | `qm set` syntax well-documented |

### Fallback Behavior

- If preferred transport fails, try the other (configurable)
- Log which transport was used for debugging
- Return consistent response format regardless of transport

## Security

### Credential Protection

`.gitignore` includes:
```
.env
proxmox-config.json
*.pem
*.key
node_modules/
dist/
```

### Provided Templates

`.env.example`:
```bash
PROXMOX_HOST=192.168.1.100
PROXMOX_API_TOKEN_ID=user@pam!mytoken
PROXMOX_API_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PROXMOX_SSH_USER=root
PROXMOX_SSH_KEY_PATH=~/.ssh/id_rsa
PROXMOX_DEFAULT_TRANSPORT=auto
```

### Destructive Operation Safeguards

- `proxmox_vm_delete` and `proxmox_ct_delete` require explicit `confirm: true` parameter
- Tool descriptions warn Claude about destructive operations
- Optional `safeMode` config flag that disables delete/create operations entirely

### SSL/TLS

- Default `verifySsl: true` for API connections
- Documentation explains how to handle self-signed certs

## Tech Stack

### Dependencies

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.x",
    "ssh2": "^1.x",
    "axios": "^1.x",
    "zod": "^3.x",
    "dotenv": "^16.x"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "@types/ssh2": "^1.x",
    "@types/node": "^20.x",
    "tsup": "^8.x"
  }
}
```

### Build & Run

- `npm run build` → compiles to `dist/`
- `npm run dev` → watch mode for development
- Entry point: `node dist/index.js`
- Node.js version: 18+ (LTS)

## Documentation Plan

### README.md

- Features overview
- Quick start (5 steps)
- Configuration summary
- Available tools table
- Usage examples
- Links to detailed docs
- Contributing section
- MIT License

### docs/ Contents

| File | Purpose |
|------|---------|
| `setup.md` | Detailed setup guide |
| `configuration.md` | All config options explained |
| `api-reference.md` | Every tool documented |
| `troubleshooting.md` | Common issues & solutions |
| `architecture.md` | How it works internally |
| `contributing.md` | How to contribute |

### examples/

- `claude-desktop-config.json` - ready to copy/paste configuration

## License

MIT
