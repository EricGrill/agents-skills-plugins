# MCP Proxmox Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MCP server that enables Claude to manage Proxmox VMs, containers, and infrastructure via hybrid SSH/API transport.

**Architecture:** TypeScript MCP server with layered configuration (MCP settings → env → config file), pluggable transport layer (SSH via ssh2, REST API via axios), and comprehensive tool set for Proxmox administration.

**Tech Stack:** TypeScript 5.x, @modelcontextprotocol/sdk, ssh2, axios, zod, dotenv, tsup

---

## Task 1: Project Initialization

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `.env.example`
- Create: `proxmox-config.example.json`

**Step 1: Create package.json**

```json
{
  "name": "mcp-proxmox-admin",
  "version": "0.1.0",
  "description": "MCP server for Proxmox VE administration",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "mcp-proxmox-admin": "dist/index.js"
  },
  "scripts": {
    "build": "tsup",
    "dev": "tsup --watch",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "tsc --noEmit"
  },
  "keywords": ["mcp", "proxmox", "virtualization", "claude"],
  "author": "",
  "license": "MIT",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "axios": "^1.7.0",
    "dotenv": "^16.4.0",
    "ssh2": "^1.16.0",
    "zod": "^3.24.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/ssh2": "^1.15.0",
    "tsup": "^8.0.0",
    "typescript": "^5.7.0",
    "vitest": "^2.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022"],
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

**Step 3: Create tsup.config.ts**

```typescript
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm"],
  target: "node18",
  clean: true,
  dts: true,
  sourcemap: true,
  shims: true,
  banner: {
    js: "#!/usr/bin/env node",
  },
});
```

**Step 4: Create .env.example**

```bash
# Proxmox Connection
PROXMOX_HOST=192.168.1.100
PROXMOX_PORT=8006

# API Authentication
PROXMOX_API_TOKEN_ID=user@pam!mytoken
PROXMOX_API_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PROXMOX_VERIFY_SSL=true

# SSH Authentication
PROXMOX_SSH_USER=root
PROXMOX_SSH_PORT=22
PROXMOX_SSH_KEY_PATH=~/.ssh/id_rsa
# PROXMOX_SSH_PASSWORD=  # Alternative to key

# Behavior
PROXMOX_DEFAULT_TRANSPORT=auto
PROXMOX_DEFAULT_NODE=pve
PROXMOX_TIMEOUT=30000
```

**Step 5: Create proxmox-config.example.json**

```json
{
  "host": "192.168.1.100",
  "port": 8006,
  "apiTokenId": "user@pam!mytoken",
  "apiTokenSecret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "verifySsl": true,
  "sshUser": "root",
  "sshPort": 22,
  "sshKeyPath": "~/.ssh/id_rsa",
  "defaultTransport": "auto",
  "defaultNode": "pve",
  "timeout": 30000
}
```

**Step 6: Install dependencies**

Run: `npm install`
Expected: Dependencies installed, node_modules created

**Step 7: Verify TypeScript compiles**

Run: `npx tsc --noEmit`
Expected: No errors (no source files yet)

**Step 8: Commit**

```bash
git add package.json tsconfig.json tsup.config.ts .env.example proxmox-config.example.json
git commit -m "chore: initialize TypeScript project with dependencies"
```

---

## Task 2: Configuration Schema

**Files:**
- Create: `src/config/schema.ts`
- Create: `src/config/schema.test.ts`

**Step 1: Write failing test for config schema**

```typescript
// src/config/schema.test.ts
import { describe, it, expect } from "vitest";
import { configSchema, type Config } from "./schema.js";

describe("configSchema", () => {
  it("validates minimal config with host", () => {
    const config = { host: "192.168.1.100" };
    const result = configSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("applies default values", () => {
    const config = { host: "192.168.1.100" };
    const result = configSchema.parse(config);
    expect(result.port).toBe(8006);
    expect(result.sshPort).toBe(22);
    expect(result.defaultTransport).toBe("auto");
    expect(result.verifySsl).toBe(true);
    expect(result.timeout).toBe(30000);
  });

  it("rejects config without host", () => {
    const config = { port: 8006 };
    const result = configSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("validates transport enum", () => {
    const validTransports = ["ssh", "api", "auto"];
    for (const transport of validTransports) {
      const config = { host: "192.168.1.100", defaultTransport: transport };
      const result = configSchema.safeParse(config);
      expect(result.success).toBe(true);
    }
  });

  it("rejects invalid transport", () => {
    const config = { host: "192.168.1.100", defaultTransport: "invalid" };
    const result = configSchema.safeParse(config);
    expect(result.success).toBe(false);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL - cannot find module "./schema.js"

**Step 3: Write config schema implementation**

```typescript
// src/config/schema.ts
import { z } from "zod";

export const transportSchema = z.enum(["ssh", "api", "auto"]);
export type Transport = z.infer<typeof transportSchema>;

export const configSchema = z.object({
  // Connection
  host: z.string().min(1),
  port: z.number().int().positive().default(8006),

  // API Authentication
  apiTokenId: z.string().optional(),
  apiTokenSecret: z.string().optional(),
  verifySsl: z.boolean().default(true),

  // SSH Authentication
  sshUser: z.string().optional(),
  sshPort: z.number().int().positive().default(22),
  sshKeyPath: z.string().optional(),
  sshPassword: z.string().optional(),

  // Behavior
  defaultTransport: transportSchema.default("auto"),
  defaultNode: z.string().optional(),
  timeout: z.number().int().positive().default(30000),
  safeMode: z.boolean().default(false),
});

export type Config = z.infer<typeof configSchema>;
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS - all tests pass

**Step 5: Commit**

```bash
git add src/config/schema.ts src/config/schema.test.ts
git commit -m "feat: add configuration schema with Zod validation"
```

---

## Task 3: Configuration Loader

**Files:**
- Create: `src/config/loader.ts`
- Create: `src/config/loader.test.ts`
- Create: `src/config/index.ts`

**Step 1: Write failing test for config loader**

```typescript
// src/config/loader.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { loadConfig } from "./loader.js";

describe("loadConfig", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("loads config from environment variables", () => {
    process.env.PROXMOX_HOST = "10.0.0.1";
    process.env.PROXMOX_PORT = "8007";
    process.env.PROXMOX_SSH_USER = "admin";

    const config = loadConfig({});
    expect(config.host).toBe("10.0.0.1");
    expect(config.port).toBe(8007);
    expect(config.sshUser).toBe("admin");
  });

  it("MCP settings override environment variables", () => {
    process.env.PROXMOX_HOST = "10.0.0.1";

    const config = loadConfig({ host: "192.168.1.1" });
    expect(config.host).toBe("192.168.1.1");
  });

  it("throws error when host is missing", () => {
    expect(() => loadConfig({})).toThrow();
  });

  it("parses boolean env vars correctly", () => {
    process.env.PROXMOX_HOST = "10.0.0.1";
    process.env.PROXMOX_VERIFY_SSL = "false";
    process.env.PROXMOX_SAFE_MODE = "true";

    const config = loadConfig({});
    expect(config.verifySsl).toBe(false);
    expect(config.safeMode).toBe(true);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL - cannot find module "./loader.js"

**Step 3: Write config loader implementation**

```typescript
// src/config/loader.ts
import { existsSync, readFileSync } from "fs";
import { resolve } from "path";
import { configSchema, type Config } from "./schema.js";

interface MCPSettings {
  host?: string;
  port?: number;
  apiTokenId?: string;
  apiTokenSecret?: string;
  verifySsl?: boolean;
  sshUser?: string;
  sshPort?: number;
  sshKeyPath?: string;
  sshPassword?: string;
  defaultTransport?: string;
  defaultNode?: string;
  timeout?: number;
  safeMode?: boolean;
}

function loadFromEnv(): Partial<MCPSettings> {
  const parseBoolean = (val: string | undefined): boolean | undefined => {
    if (val === undefined) return undefined;
    return val.toLowerCase() === "true";
  };

  const parseNumber = (val: string | undefined): number | undefined => {
    if (val === undefined) return undefined;
    const num = parseInt(val, 10);
    return isNaN(num) ? undefined : num;
  };

  return {
    host: process.env.PROXMOX_HOST,
    port: parseNumber(process.env.PROXMOX_PORT),
    apiTokenId: process.env.PROXMOX_API_TOKEN_ID,
    apiTokenSecret: process.env.PROXMOX_API_TOKEN_SECRET,
    verifySsl: parseBoolean(process.env.PROXMOX_VERIFY_SSL),
    sshUser: process.env.PROXMOX_SSH_USER,
    sshPort: parseNumber(process.env.PROXMOX_SSH_PORT),
    sshKeyPath: process.env.PROXMOX_SSH_KEY_PATH,
    sshPassword: process.env.PROXMOX_SSH_PASSWORD,
    defaultTransport: process.env.PROXMOX_DEFAULT_TRANSPORT,
    defaultNode: process.env.PROXMOX_DEFAULT_NODE,
    timeout: parseNumber(process.env.PROXMOX_TIMEOUT),
    safeMode: parseBoolean(process.env.PROXMOX_SAFE_MODE),
  };
}

function loadFromFile(): Partial<MCPSettings> {
  const configPath = resolve(process.cwd(), "proxmox-config.json");
  if (!existsSync(configPath)) {
    return {};
  }
  try {
    const content = readFileSync(configPath, "utf-8");
    return JSON.parse(content);
  } catch {
    return {};
  }
}

function removeUndefined<T extends object>(obj: T): Partial<T> {
  return Object.fromEntries(
    Object.entries(obj).filter(([_, v]) => v !== undefined)
  ) as Partial<T>;
}

export function loadConfig(mcpSettings: MCPSettings): Config {
  const fileConfig = loadFromFile();
  const envConfig = loadFromEnv();

  // Priority: MCP settings > env > file
  const merged = {
    ...removeUndefined(fileConfig),
    ...removeUndefined(envConfig),
    ...removeUndefined(mcpSettings),
  };

  return configSchema.parse(merged);
}
```

**Step 4: Create config index**

```typescript
// src/config/index.ts
export { configSchema, type Config, type Transport } from "./schema.js";
export { loadConfig } from "./loader.js";
```

**Step 5: Run test to verify it passes**

Run: `npm test`
Expected: PASS - all tests pass

**Step 6: Commit**

```bash
git add src/config/loader.ts src/config/loader.test.ts src/config/index.ts
git commit -m "feat: add layered configuration loader (MCP → env → file)"
```

---

## Task 4: Transport Interface and Types

**Files:**
- Create: `src/types/proxmox.ts`
- Create: `src/transports/types.ts`

**Step 1: Create Proxmox types**

```typescript
// src/types/proxmox.ts
export interface VMStatus {
  vmid: number;
  name: string;
  status: "running" | "stopped" | "paused";
  node: string;
  cpu: number;
  mem: number;
  maxmem: number;
  disk: number;
  maxdisk: number;
  uptime: number;
  template: boolean;
}

export interface ContainerStatus {
  vmid: number;
  name: string;
  status: "running" | "stopped";
  node: string;
  cpu: number;
  mem: number;
  maxmem: number;
  disk: number;
  maxdisk: number;
  uptime: number;
  template: boolean;
}

export interface NodeStatus {
  node: string;
  status: "online" | "offline";
  cpu: number;
  maxcpu: number;
  mem: number;
  maxmem: number;
  disk: number;
  maxdisk: number;
  uptime: number;
}

export interface StorageInfo {
  storage: string;
  type: string;
  content: string;
  active: boolean;
  enabled: boolean;
  shared: boolean;
  total: number;
  used: number;
  avail: number;
}

export interface Snapshot {
  name: string;
  description: string;
  snaptime?: number;
  parent?: string;
}

export interface TaskResult {
  success: boolean;
  taskId?: string;
  message?: string;
  data?: unknown;
}
```

**Step 2: Create transport interface**

```typescript
// src/transports/types.ts
import type { TaskResult, VMStatus, ContainerStatus, NodeStatus, StorageInfo, Snapshot } from "../types/proxmox.js";

export interface CommandResult {
  success: boolean;
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface Transport {
  // Connection
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;

  // Raw execution
  executeCommand(command: string): Promise<CommandResult>;
  apiRequest<T>(method: string, endpoint: string, data?: unknown): Promise<T>;

  // VM operations
  listVMs(node?: string): Promise<VMStatus[]>;
  getVM(node: string, vmid: number): Promise<VMStatus>;
  startVM(node: string, vmid: number): Promise<TaskResult>;
  stopVM(node: string, vmid: number): Promise<TaskResult>;
  shutdownVM(node: string, vmid: number): Promise<TaskResult>;
  restartVM(node: string, vmid: number): Promise<TaskResult>;

  // Container operations
  listContainers(node?: string): Promise<ContainerStatus[]>;
  getContainer(node: string, vmid: number): Promise<ContainerStatus>;
  startContainer(node: string, vmid: number): Promise<TaskResult>;
  stopContainer(node: string, vmid: number): Promise<TaskResult>;
  restartContainer(node: string, vmid: number): Promise<TaskResult>;

  // Node operations
  listNodes(): Promise<NodeStatus[]>;
  getNodeStatus(node: string): Promise<NodeStatus>;

  // Storage operations
  listStorage(node?: string): Promise<StorageInfo[]>;

  // Snapshot operations
  listSnapshots(node: string, vmid: number, type: "vm" | "ct"): Promise<Snapshot[]>;
  createSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string, description?: string): Promise<TaskResult>;
  deleteSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string): Promise<TaskResult>;
  restoreSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string): Promise<TaskResult>;
}

export type TransportType = "ssh" | "api" | "auto";
```

**Step 3: Commit**

```bash
git add src/types/proxmox.ts src/transports/types.ts
git commit -m "feat: add Proxmox types and transport interface"
```

---

## Task 5: SSH Transport Implementation

**Files:**
- Create: `src/transports/ssh.ts`
- Create: `src/transports/ssh.test.ts`

**Step 1: Write failing test for SSH transport**

```typescript
// src/transports/ssh.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { SSHTransport } from "./ssh.js";
import type { Config } from "../config/index.js";

// Mock ssh2
vi.mock("ssh2", () => {
  const mockExec = vi.fn();
  const mockConnect = vi.fn();
  const mockEnd = vi.fn();
  const mockOn = vi.fn();

  class MockClient {
    exec = mockExec;
    connect = mockConnect;
    end = mockEnd;
    on = mockOn;
  }

  return { Client: MockClient };
});

describe("SSHTransport", () => {
  const baseConfig: Config = {
    host: "192.168.1.100",
    port: 8006,
    sshUser: "root",
    sshPort: 22,
    sshKeyPath: "/home/user/.ssh/id_rsa",
    defaultTransport: "ssh",
    verifySsl: true,
    timeout: 30000,
    safeMode: false,
  };

  it("creates instance with config", () => {
    const transport = new SSHTransport(baseConfig);
    expect(transport).toBeInstanceOf(SSHTransport);
  });

  it("isConnected returns false initially", () => {
    const transport = new SSHTransport(baseConfig);
    expect(transport.isConnected()).toBe(false);
  });

  it("parseVMList parses qm list output", () => {
    const transport = new SSHTransport(baseConfig);
    const output = `      VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID
       100 ubuntu-server        running    4096              32.00 12345
       101 windows-desktop      stopped    8192              64.00 0`;

    const result = transport.parseVMListOutput(output, "pve");
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      vmid: 100,
      name: "ubuntu-server",
      status: "running",
      node: "pve",
    });
    expect(result[1]).toMatchObject({
      vmid: 101,
      name: "windows-desktop",
      status: "stopped",
      node: "pve",
    });
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL - cannot find module "./ssh.js"

**Step 3: Write SSH transport implementation**

```typescript
// src/transports/ssh.ts
import { Client, type ConnectConfig } from "ssh2";
import { readFileSync } from "fs";
import { resolve } from "path";
import type { Config } from "../config/index.js";
import type {
  Transport,
  CommandResult,
} from "./types.js";
import type {
  VMStatus,
  ContainerStatus,
  NodeStatus,
  StorageInfo,
  Snapshot,
  TaskResult,
} from "../types/proxmox.js";

export class SSHTransport implements Transport {
  private client: Client;
  private config: Config;
  private connected = false;

  constructor(config: Config) {
    this.config = config;
    this.client = new Client();
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const connectConfig: ConnectConfig = {
        host: this.config.host,
        port: this.config.sshPort ?? 22,
        username: this.config.sshUser ?? "root",
        readyTimeout: this.config.timeout,
      };

      if (this.config.sshKeyPath) {
        const keyPath = this.config.sshKeyPath.replace("~", process.env.HOME || "");
        connectConfig.privateKey = readFileSync(resolve(keyPath));
      } else if (this.config.sshPassword) {
        connectConfig.password = this.config.sshPassword;
      }

      this.client.on("ready", () => {
        this.connected = true;
        resolve();
      });

      this.client.on("error", (err) => {
        this.connected = false;
        reject(err);
      });

      this.client.connect(connectConfig);
    });
  }

  async disconnect(): Promise<void> {
    this.client.end();
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  async executeCommand(command: string): Promise<CommandResult> {
    return new Promise((resolve, reject) => {
      this.client.exec(command, (err, stream) => {
        if (err) {
          reject(err);
          return;
        }

        let stdout = "";
        let stderr = "";

        stream.on("data", (data: Buffer) => {
          stdout += data.toString();
        });

        stream.stderr.on("data", (data: Buffer) => {
          stderr += data.toString();
        });

        stream.on("close", (code: number) => {
          resolve({
            success: code === 0,
            stdout: stdout.trim(),
            stderr: stderr.trim(),
            exitCode: code,
          });
        });
      });
    });
  }

  async apiRequest<T>(_method: string, _endpoint: string, _data?: unknown): Promise<T> {
    throw new Error("API requests not supported via SSH transport. Use pvesh command instead.");
  }

  // Parser methods (public for testing)
  parseVMListOutput(output: string, node: string): VMStatus[] {
    const lines = output.split("\n").slice(1); // Skip header
    return lines
      .filter((line) => line.trim())
      .map((line) => {
        const parts = line.trim().split(/\s+/);
        return {
          vmid: parseInt(parts[0], 10),
          name: parts[1],
          status: parts[2] as "running" | "stopped" | "paused",
          node,
          mem: parseInt(parts[3], 10) * 1024 * 1024,
          maxmem: parseInt(parts[3], 10) * 1024 * 1024,
          disk: parseFloat(parts[4]) * 1024 * 1024 * 1024,
          maxdisk: parseFloat(parts[4]) * 1024 * 1024 * 1024,
          cpu: 0,
          uptime: 0,
          template: false,
        };
      });
  }

  parseContainerListOutput(output: string, node: string): ContainerStatus[] {
    const lines = output.split("\n").slice(1);
    return lines
      .filter((line) => line.trim())
      .map((line) => {
        const parts = line.trim().split(/\s+/);
        return {
          vmid: parseInt(parts[0], 10),
          name: parts[2],
          status: parts[1] as "running" | "stopped",
          node,
          mem: parseInt(parts[4], 10),
          maxmem: parseInt(parts[3], 10),
          disk: parseInt(parts[6], 10),
          maxdisk: parseInt(parts[5], 10),
          cpu: 0,
          uptime: 0,
          template: false,
        };
      });
  }

  // VM Operations
  async listVMs(node?: string): Promise<VMStatus[]> {
    const targetNode = node ?? this.config.defaultNode ?? "pve";
    const result = await this.executeCommand("qm list");
    if (!result.success) {
      throw new Error(`Failed to list VMs: ${result.stderr}`);
    }
    return this.parseVMListOutput(result.stdout, targetNode);
  }

  async getVM(node: string, vmid: number): Promise<VMStatus> {
    const vms = await this.listVMs(node);
    const vm = vms.find((v) => v.vmid === vmid);
    if (!vm) {
      throw new Error(`VM ${vmid} not found on node ${node}`);
    }
    return vm;
  }

  async startVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm start ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} started` : result.stderr,
    };
  }

  async stopVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm stop ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} stopped` : result.stderr,
    };
  }

  async shutdownVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm shutdown ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} shutdown initiated` : result.stderr,
    };
  }

  async restartVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm reboot ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} restarting` : result.stderr,
    };
  }

  // Container Operations
  async listContainers(node?: string): Promise<ContainerStatus[]> {
    const targetNode = node ?? this.config.defaultNode ?? "pve";
    const result = await this.executeCommand("pct list");
    if (!result.success) {
      throw new Error(`Failed to list containers: ${result.stderr}`);
    }
    return this.parseContainerListOutput(result.stdout, targetNode);
  }

  async getContainer(node: string, vmid: number): Promise<ContainerStatus> {
    const containers = await this.listContainers(node);
    const ct = containers.find((c) => c.vmid === vmid);
    if (!ct) {
      throw new Error(`Container ${vmid} not found on node ${node}`);
    }
    return ct;
  }

  async startContainer(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`pct start ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `Container ${vmid} started` : result.stderr,
    };
  }

  async stopContainer(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`pct stop ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `Container ${vmid} stopped` : result.stderr,
    };
  }

  async restartContainer(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`pct reboot ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `Container ${vmid} restarting` : result.stderr,
    };
  }

  // Node Operations
  async listNodes(): Promise<NodeStatus[]> {
    const result = await this.executeCommand("pvesh get /nodes --output-format json");
    if (!result.success) {
      throw new Error(`Failed to list nodes: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return data.map((n: Record<string, unknown>) => ({
      node: n.node as string,
      status: n.status as "online" | "offline",
      cpu: n.cpu as number,
      maxcpu: n.maxcpu as number,
      mem: n.mem as number,
      maxmem: n.maxmem as number,
      disk: n.disk as number,
      maxdisk: n.maxdisk as number,
      uptime: n.uptime as number,
    }));
  }

  async getNodeStatus(node: string): Promise<NodeStatus> {
    const result = await this.executeCommand(`pvesh get /nodes/${node}/status --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to get node status: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return {
      node,
      status: "online",
      cpu: data.cpu,
      maxcpu: data.cpuinfo?.cpus ?? 1,
      mem: data.memory?.used ?? 0,
      maxmem: data.memory?.total ?? 0,
      disk: data.rootfs?.used ?? 0,
      maxdisk: data.rootfs?.total ?? 0,
      uptime: data.uptime ?? 0,
    };
  }

  // Storage Operations
  async listStorage(node?: string): Promise<StorageInfo[]> {
    const targetNode = node ?? this.config.defaultNode ?? "pve";
    const result = await this.executeCommand(`pvesh get /nodes/${targetNode}/storage --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to list storage: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return data.map((s: Record<string, unknown>) => ({
      storage: s.storage as string,
      type: s.type as string,
      content: s.content as string,
      active: s.active === 1,
      enabled: s.enabled === 1,
      shared: s.shared === 1,
      total: s.total as number,
      used: s.used as number,
      avail: s.avail as number,
    }));
  }

  // Snapshot Operations
  async listSnapshots(node: string, vmid: number, type: "vm" | "ct"): Promise<Snapshot[]> {
    const cmd = type === "vm" ? "qm" : "pct";
    const result = await this.executeCommand(`${cmd} listsnapshot ${vmid}`);
    if (!result.success) {
      throw new Error(`Failed to list snapshots: ${result.stderr}`);
    }
    // Parse snapshot list output
    const lines = result.stdout.split("\n");
    return lines
      .filter((line) => line.includes("->") || line.trim().startsWith("`-"))
      .map((line) => {
        const match = line.match(/(?:`-|->)\s*(\S+)/);
        return {
          name: match ? match[1] : "unknown",
          description: "",
        };
      });
  }

  async createSnapshot(
    node: string,
    vmid: number,
    type: "vm" | "ct",
    name: string,
    description?: string
  ): Promise<TaskResult> {
    const cmd = type === "vm" ? "qm" : "pct";
    const descArg = description ? ` --description "${description}"` : "";
    const result = await this.executeCommand(`${cmd} snapshot ${vmid} ${name}${descArg}`);
    return {
      success: result.success,
      message: result.success ? `Snapshot ${name} created` : result.stderr,
    };
  }

  async deleteSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string): Promise<TaskResult> {
    const cmd = type === "vm" ? "qm" : "pct";
    const result = await this.executeCommand(`${cmd} delsnapshot ${vmid} ${name}`);
    return {
      success: result.success,
      message: result.success ? `Snapshot ${name} deleted` : result.stderr,
    };
  }

  async restoreSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string): Promise<TaskResult> {
    const cmd = type === "vm" ? "qm" : "pct";
    const result = await this.executeCommand(`${cmd} rollback ${vmid} ${name}`);
    return {
      success: result.success,
      message: result.success ? `Rolled back to snapshot ${name}` : result.stderr,
    };
  }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS - all tests pass

**Step 5: Commit**

```bash
git add src/transports/ssh.ts src/transports/ssh.test.ts
git commit -m "feat: implement SSH transport with Proxmox command parsing"
```

---

## Task 6: API Transport Implementation

**Files:**
- Create: `src/transports/api.ts`
- Create: `src/transports/api.test.ts`

**Step 1: Write failing test for API transport**

```typescript
// src/transports/api.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { APITransport } from "./api.js";
import type { Config } from "../config/index.js";

vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    })),
  },
}));

describe("APITransport", () => {
  const baseConfig: Config = {
    host: "192.168.1.100",
    port: 8006,
    apiTokenId: "user@pam!token",
    apiTokenSecret: "secret-uuid",
    verifySsl: true,
    defaultTransport: "api",
    timeout: 30000,
    safeMode: false,
  };

  it("creates instance with config", () => {
    const transport = new APITransport(baseConfig);
    expect(transport).toBeInstanceOf(APITransport);
  });

  it("builds correct base URL", () => {
    const transport = new APITransport(baseConfig);
    expect(transport.getBaseUrl()).toBe("https://192.168.1.100:8006/api2/json");
  });

  it("builds correct auth header", () => {
    const transport = new APITransport(baseConfig);
    const header = transport.getAuthHeader();
    expect(header).toBe("PVEAPIToken=user@pam!token=secret-uuid");
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL - cannot find module "./api.js"

**Step 3: Write API transport implementation**

```typescript
// src/transports/api.ts
import axios, { type AxiosInstance } from "axios";
import https from "https";
import type { Config } from "../config/index.js";
import type { Transport, CommandResult } from "./types.js";
import type {
  VMStatus,
  ContainerStatus,
  NodeStatus,
  StorageInfo,
  Snapshot,
  TaskResult,
} from "../types/proxmox.js";

export class APITransport implements Transport {
  private config: Config;
  private client: AxiosInstance;
  private connected = false;

  constructor(config: Config) {
    this.config = config;
    this.client = axios.create({
      baseURL: this.getBaseUrl(),
      timeout: config.timeout,
      headers: {
        Authorization: this.getAuthHeader(),
      },
      httpsAgent: new https.Agent({
        rejectUnauthorized: config.verifySsl,
      }),
    });
  }

  getBaseUrl(): string {
    return `https://${this.config.host}:${this.config.port}/api2/json`;
  }

  getAuthHeader(): string {
    return `PVEAPIToken=${this.config.apiTokenId}=${this.config.apiTokenSecret}`;
  }

  async connect(): Promise<void> {
    // Test connection by fetching version
    try {
      await this.client.get("/version");
      this.connected = true;
    } catch (err) {
      this.connected = false;
      throw new Error(`Failed to connect to Proxmox API: ${err}`);
    }
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  async executeCommand(_command: string): Promise<CommandResult> {
    throw new Error("Direct command execution not supported via API transport. Use SSH transport instead.");
  }

  async apiRequest<T>(method: string, endpoint: string, data?: unknown): Promise<T> {
    const response = await this.client.request({
      method,
      url: endpoint,
      data,
    });
    return response.data.data;
  }

  // VM Operations
  async listVMs(node?: string): Promise<VMStatus[]> {
    if (node) {
      const data = await this.apiRequest<Record<string, unknown>[]>("GET", `/nodes/${node}/qemu`);
      return data.map((vm) => this.mapVM(vm, node));
    }
    // Get all nodes and aggregate VMs
    const nodes = await this.listNodes();
    const allVMs: VMStatus[] = [];
    for (const n of nodes) {
      const vms = await this.listVMs(n.node);
      allVMs.push(...vms);
    }
    return allVMs;
  }

  private mapVM(data: Record<string, unknown>, node: string): VMStatus {
    return {
      vmid: data.vmid as number,
      name: data.name as string,
      status: data.status as "running" | "stopped" | "paused",
      node,
      cpu: data.cpu as number,
      mem: data.mem as number,
      maxmem: data.maxmem as number,
      disk: data.disk as number,
      maxdisk: data.maxdisk as number,
      uptime: data.uptime as number,
      template: data.template === 1,
    };
  }

  async getVM(node: string, vmid: number): Promise<VMStatus> {
    const data = await this.apiRequest<Record<string, unknown>>("GET", `/nodes/${node}/qemu/${vmid}/status/current`);
    return this.mapVM({ ...data, vmid }, node);
  }

  async startVM(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/qemu/${vmid}/status/start`);
      return { success: true, taskId, message: `VM ${vmid} start initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async stopVM(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/qemu/${vmid}/status/stop`);
      return { success: true, taskId, message: `VM ${vmid} stop initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async shutdownVM(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/qemu/${vmid}/status/shutdown`);
      return { success: true, taskId, message: `VM ${vmid} shutdown initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async restartVM(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/qemu/${vmid}/status/reboot`);
      return { success: true, taskId, message: `VM ${vmid} restart initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  // Container Operations
  async listContainers(node?: string): Promise<ContainerStatus[]> {
    if (node) {
      const data = await this.apiRequest<Record<string, unknown>[]>("GET", `/nodes/${node}/lxc`);
      return data.map((ct) => this.mapContainer(ct, node));
    }
    const nodes = await this.listNodes();
    const allContainers: ContainerStatus[] = [];
    for (const n of nodes) {
      const containers = await this.listContainers(n.node);
      allContainers.push(...containers);
    }
    return allContainers;
  }

  private mapContainer(data: Record<string, unknown>, node: string): ContainerStatus {
    return {
      vmid: data.vmid as number,
      name: data.name as string,
      status: data.status as "running" | "stopped",
      node,
      cpu: data.cpu as number,
      mem: data.mem as number,
      maxmem: data.maxmem as number,
      disk: data.disk as number,
      maxdisk: data.maxdisk as number,
      uptime: data.uptime as number,
      template: data.template === 1,
    };
  }

  async getContainer(node: string, vmid: number): Promise<ContainerStatus> {
    const data = await this.apiRequest<Record<string, unknown>>("GET", `/nodes/${node}/lxc/${vmid}/status/current`);
    return this.mapContainer({ ...data, vmid }, node);
  }

  async startContainer(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/lxc/${vmid}/status/start`);
      return { success: true, taskId, message: `Container ${vmid} start initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async stopContainer(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/lxc/${vmid}/status/stop`);
      return { success: true, taskId, message: `Container ${vmid} stop initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async restartContainer(node: string, vmid: number): Promise<TaskResult> {
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/lxc/${vmid}/status/reboot`);
      return { success: true, taskId, message: `Container ${vmid} restart initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  // Node Operations
  async listNodes(): Promise<NodeStatus[]> {
    const data = await this.apiRequest<Record<string, unknown>[]>("GET", "/nodes");
    return data.map((n) => ({
      node: n.node as string,
      status: n.status as "online" | "offline",
      cpu: n.cpu as number,
      maxcpu: n.maxcpu as number,
      mem: n.mem as number,
      maxmem: n.maxmem as number,
      disk: n.disk as number,
      maxdisk: n.maxdisk as number,
      uptime: n.uptime as number,
    }));
  }

  async getNodeStatus(node: string): Promise<NodeStatus> {
    const data = await this.apiRequest<Record<string, unknown>>("GET", `/nodes/${node}/status`);
    return {
      node,
      status: "online",
      cpu: data.cpu as number,
      maxcpu: (data.cpuinfo as Record<string, number>)?.cpus ?? 1,
      mem: (data.memory as Record<string, number>)?.used ?? 0,
      maxmem: (data.memory as Record<string, number>)?.total ?? 0,
      disk: (data.rootfs as Record<string, number>)?.used ?? 0,
      maxdisk: (data.rootfs as Record<string, number>)?.total ?? 0,
      uptime: data.uptime as number,
    };
  }

  // Storage Operations
  async listStorage(node?: string): Promise<StorageInfo[]> {
    const targetNode = node ?? this.config.defaultNode ?? "pve";
    const data = await this.apiRequest<Record<string, unknown>[]>("GET", `/nodes/${targetNode}/storage`);
    return data.map((s) => ({
      storage: s.storage as string,
      type: s.type as string,
      content: s.content as string,
      active: s.active === 1,
      enabled: s.enabled === 1,
      shared: s.shared === 1,
      total: s.total as number,
      used: s.used as number,
      avail: s.avail as number,
    }));
  }

  // Snapshot Operations
  async listSnapshots(node: string, vmid: number, type: "vm" | "ct"): Promise<Snapshot[]> {
    const path = type === "vm" ? "qemu" : "lxc";
    const data = await this.apiRequest<Record<string, unknown>[]>("GET", `/nodes/${node}/${path}/${vmid}/snapshot`);
    return data
      .filter((s) => s.name !== "current")
      .map((s) => ({
        name: s.name as string,
        description: (s.description as string) ?? "",
        snaptime: s.snaptime as number,
        parent: s.parent as string,
      }));
  }

  async createSnapshot(
    node: string,
    vmid: number,
    type: "vm" | "ct",
    name: string,
    description?: string
  ): Promise<TaskResult> {
    const path = type === "vm" ? "qemu" : "lxc";
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/${path}/${vmid}/snapshot`, {
        snapname: name,
        description,
      });
      return { success: true, taskId, message: `Snapshot ${name} creation initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async deleteSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string): Promise<TaskResult> {
    const path = type === "vm" ? "qemu" : "lxc";
    try {
      const taskId = await this.apiRequest<string>("DELETE", `/nodes/${node}/${path}/${vmid}/snapshot/${name}`);
      return { success: true, taskId, message: `Snapshot ${name} deletion initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }

  async restoreSnapshot(node: string, vmid: number, type: "vm" | "ct", name: string): Promise<TaskResult> {
    const path = type === "vm" ? "qemu" : "lxc";
    try {
      const taskId = await this.apiRequest<string>("POST", `/nodes/${node}/${path}/${vmid}/snapshot/${name}/rollback`);
      return { success: true, taskId, message: `Rollback to ${name} initiated` };
    } catch (err) {
      return { success: false, message: String(err) };
    }
  }
}
```

**Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS - all tests pass

**Step 5: Commit**

```bash
git add src/transports/api.ts src/transports/api.test.ts
git commit -m "feat: implement Proxmox REST API transport"
```

---

## Task 7: Transport Router

**Files:**
- Create: `src/transports/router.ts`
- Create: `src/transports/index.ts`

**Step 1: Create transport router**

```typescript
// src/transports/router.ts
import type { Config, Transport as TransportType } from "../config/index.js";
import type { Transport } from "./types.js";
import { SSHTransport } from "./ssh.js";
import { APITransport } from "./api.js";

type OperationType = "read" | "write" | "snapshot" | "config";

const AUTO_PREFERENCES: Record<OperationType, TransportType> = {
  read: "api",
  write: "api",
  snapshot: "ssh",
  config: "ssh",
};

export class TransportRouter {
  private sshTransport: SSHTransport | null = null;
  private apiTransport: APITransport | null = null;
  private config: Config;

  constructor(config: Config) {
    this.config = config;

    if (config.sshUser || config.sshKeyPath || config.sshPassword) {
      this.sshTransport = new SSHTransport(config);
    }

    if (config.apiTokenId && config.apiTokenSecret) {
      this.apiTransport = new APITransport(config);
    }

    if (!this.sshTransport && !this.apiTransport) {
      throw new Error("No transport configured. Provide SSH or API credentials.");
    }
  }

  async connect(): Promise<void> {
    const promises: Promise<void>[] = [];
    if (this.sshTransport) promises.push(this.sshTransport.connect());
    if (this.apiTransport) promises.push(this.apiTransport.connect());
    await Promise.all(promises);
  }

  async disconnect(): Promise<void> {
    const promises: Promise<void>[] = [];
    if (this.sshTransport) promises.push(this.sshTransport.disconnect());
    if (this.apiTransport) promises.push(this.apiTransport.disconnect());
    await Promise.all(promises);
  }

  getTransport(
    requestedTransport?: TransportType,
    operationType: OperationType = "read"
  ): Transport {
    const transport = requestedTransport ?? this.config.defaultTransport;

    if (transport === "ssh") {
      if (!this.sshTransport) {
        throw new Error("SSH transport not configured");
      }
      return this.sshTransport;
    }

    if (transport === "api") {
      if (!this.apiTransport) {
        throw new Error("API transport not configured");
      }
      return this.apiTransport;
    }

    // Auto mode - pick based on operation type
    const preferred = AUTO_PREFERENCES[operationType];
    if (preferred === "api" && this.apiTransport) {
      return this.apiTransport;
    }
    if (preferred === "ssh" && this.sshTransport) {
      return this.sshTransport;
    }

    // Fallback to whatever is available
    return this.apiTransport ?? this.sshTransport!;
  }

  hasSSH(): boolean {
    return this.sshTransport !== null;
  }

  hasAPI(): boolean {
    return this.apiTransport !== null;
  }
}
```

**Step 2: Create transports index**

```typescript
// src/transports/index.ts
export { SSHTransport } from "./ssh.js";
export { APITransport } from "./api.js";
export { TransportRouter } from "./router.js";
export type { Transport, CommandResult, TransportType } from "./types.js";
```

**Step 3: Commit**

```bash
git add src/transports/router.ts src/transports/index.ts
git commit -m "feat: add transport router with auto-mode selection"
```

---

## Task 8: MCP Server Entry Point

**Files:**
- Create: `src/index.ts`

**Step 1: Create MCP server**

```typescript
// src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { loadConfig } from "./config/index.js";
import { TransportRouter } from "./transports/index.js";
import { registerVMTools } from "./tools/vm.js";
import { registerContainerTools } from "./tools/container.js";
import { registerNodeTools } from "./tools/node.js";
import { registerStorageTools } from "./tools/storage.js";

async function main() {
  const server = new Server(
    {
      name: "mcp-proxmox-admin",
      version: "0.1.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Load config from MCP settings passed via environment or args
  const mcpSettings = JSON.parse(process.env.MCP_SETTINGS ?? "{}");
  const config = loadConfig(mcpSettings);

  // Initialize transport router
  const router = new TransportRouter(config);

  // Tool registry
  const tools: Map<string, (args: Record<string, unknown>) => Promise<unknown>> = new Map();

  // Register tools from each module
  registerVMTools(tools, router, config);
  registerContainerTools(tools, router, config);
  registerNodeTools(tools, router, config);
  registerStorageTools(tools, router, config);

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        // VM Tools
        {
          name: "proxmox_vm_list",
          description: "List all VMs with their status and resource usage",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name (optional, lists all nodes if omitted)" },
              transport: { type: "string", enum: ["ssh", "api", "auto"], description: "Transport to use" },
            },
          },
        },
        {
          name: "proxmox_vm_start",
          description: "Start a VM",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        {
          name: "proxmox_vm_stop",
          description: "Stop a VM (immediate, may cause data loss)",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        {
          name: "proxmox_vm_shutdown",
          description: "Gracefully shutdown a VM",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        {
          name: "proxmox_vm_restart",
          description: "Restart a VM",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        // Container Tools
        {
          name: "proxmox_ct_list",
          description: "List all containers with their status",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name (optional)" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
          },
        },
        {
          name: "proxmox_ct_start",
          description: "Start a container",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "Container ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        {
          name: "proxmox_ct_stop",
          description: "Stop a container",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "Container ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        {
          name: "proxmox_ct_restart",
          description: "Restart a container",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "Container ID" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid"],
          },
        },
        // Node Tools
        {
          name: "proxmox_node_list",
          description: "List all nodes in the cluster",
          inputSchema: {
            type: "object",
            properties: {
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
          },
        },
        {
          name: "proxmox_node_status",
          description: "Get detailed status of a node",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node"],
          },
        },
        // Storage Tools
        {
          name: "proxmox_storage_list",
          description: "List storage pools",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name (optional)" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
          },
        },
        // Snapshot Tools
        {
          name: "proxmox_snapshot_list",
          description: "List snapshots for a VM or container",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM or container ID" },
              type: { type: "string", enum: ["vm", "ct"], description: "Type: vm or ct" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid", "type"],
          },
        },
        {
          name: "proxmox_snapshot_create",
          description: "Create a snapshot",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM or container ID" },
              type: { type: "string", enum: ["vm", "ct"] },
              name: { type: "string", description: "Snapshot name" },
              description: { type: "string", description: "Snapshot description" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid", "type", "name"],
          },
        },
        {
          name: "proxmox_snapshot_restore",
          description: "Restore a snapshot (WARNING: current state will be lost)",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM or container ID" },
              type: { type: "string", enum: ["vm", "ct"] },
              name: { type: "string", description: "Snapshot name to restore" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid", "type", "name"],
          },
        },
        {
          name: "proxmox_snapshot_delete",
          description: "Delete a snapshot (requires confirm: true)",
          inputSchema: {
            type: "object",
            properties: {
              node: { type: "string", description: "Node name" },
              vmid: { type: "number", description: "VM or container ID" },
              type: { type: "string", enum: ["vm", "ct"] },
              name: { type: "string", description: "Snapshot name to delete" },
              confirm: { type: "boolean", description: "Must be true to confirm deletion" },
              transport: { type: "string", enum: ["ssh", "api", "auto"] },
            },
            required: ["node", "vmid", "type", "name", "confirm"],
          },
        },
      ],
    };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const handler = tools.get(name);

    if (!handler) {
      throw new Error(`Unknown tool: ${name}`);
    }

    try {
      const result = await handler(args ?? {});
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });

  // Connect transports
  await router.connect();

  // Start server
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
```

**Step 2: Commit**

```bash
git add src/index.ts
git commit -m "feat: add MCP server entry point with tool registration"
```

---

## Task 9: Tool Implementations

**Files:**
- Create: `src/tools/vm.ts`
- Create: `src/tools/container.ts`
- Create: `src/tools/node.ts`
- Create: `src/tools/storage.ts`

**Step 1: Create VM tools**

```typescript
// src/tools/vm.ts
import type { Config, Transport } from "../config/index.js";
import type { TransportRouter } from "../transports/index.js";

type ToolHandler = (args: Record<string, unknown>) => Promise<unknown>;

export function registerVMTools(
  tools: Map<string, ToolHandler>,
  router: TransportRouter,
  config: Config
): void {
  tools.set("proxmox_vm_list", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "read");
    return transport.listVMs(args.node as string | undefined);
  });

  tools.set("proxmox_vm_start", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.startVM(args.node as string, args.vmid as number);
  });

  tools.set("proxmox_vm_stop", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.stopVM(args.node as string, args.vmid as number);
  });

  tools.set("proxmox_vm_shutdown", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.shutdownVM(args.node as string, args.vmid as number);
  });

  tools.set("proxmox_vm_restart", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.restartVM(args.node as string, args.vmid as number);
  });
}
```

**Step 2: Create container tools**

```typescript
// src/tools/container.ts
import type { Config, Transport } from "../config/index.js";
import type { TransportRouter } from "../transports/index.js";

type ToolHandler = (args: Record<string, unknown>) => Promise<unknown>;

export function registerContainerTools(
  tools: Map<string, ToolHandler>,
  router: TransportRouter,
  config: Config
): void {
  tools.set("proxmox_ct_list", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "read");
    return transport.listContainers(args.node as string | undefined);
  });

  tools.set("proxmox_ct_start", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.startContainer(args.node as string, args.vmid as number);
  });

  tools.set("proxmox_ct_stop", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.stopContainer(args.node as string, args.vmid as number);
  });

  tools.set("proxmox_ct_restart", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "write");
    return transport.restartContainer(args.node as string, args.vmid as number);
  });
}
```

**Step 3: Create node tools**

```typescript
// src/tools/node.ts
import type { Config, Transport } from "../config/index.js";
import type { TransportRouter } from "../transports/index.js";

type ToolHandler = (args: Record<string, unknown>) => Promise<unknown>;

export function registerNodeTools(
  tools: Map<string, ToolHandler>,
  router: TransportRouter,
  config: Config
): void {
  tools.set("proxmox_node_list", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "read");
    return transport.listNodes();
  });

  tools.set("proxmox_node_status", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "read");
    return transport.getNodeStatus(args.node as string);
  });
}
```

**Step 4: Create storage tools**

```typescript
// src/tools/storage.ts
import type { Config, Transport } from "../config/index.js";
import type { TransportRouter } from "../transports/index.js";

type ToolHandler = (args: Record<string, unknown>) => Promise<unknown>;

export function registerStorageTools(
  tools: Map<string, ToolHandler>,
  router: TransportRouter,
  config: Config
): void {
  tools.set("proxmox_storage_list", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "read");
    return transport.listStorage(args.node as string | undefined);
  });

  tools.set("proxmox_snapshot_list", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "snapshot");
    return transport.listSnapshots(
      args.node as string,
      args.vmid as number,
      args.type as "vm" | "ct"
    );
  });

  tools.set("proxmox_snapshot_create", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "snapshot");
    return transport.createSnapshot(
      args.node as string,
      args.vmid as number,
      args.type as "vm" | "ct",
      args.name as string,
      args.description as string | undefined
    );
  });

  tools.set("proxmox_snapshot_restore", async (args) => {
    const transport = router.getTransport(args.transport as Transport, "snapshot");
    return transport.restoreSnapshot(
      args.node as string,
      args.vmid as number,
      args.type as "vm" | "ct",
      args.name as string
    );
  });

  tools.set("proxmox_snapshot_delete", async (args) => {
    if (args.confirm !== true) {
      throw new Error("Deletion requires confirm: true");
    }
    const transport = router.getTransport(args.transport as Transport, "snapshot");
    return transport.deleteSnapshot(
      args.node as string,
      args.vmid as number,
      args.type as "vm" | "ct",
      args.name as string
    );
  });
}
```

**Step 5: Commit**

```bash
git add src/tools/
git commit -m "feat: implement MCP tool handlers for VM, container, node, storage"
```

---

## Task 10: README and Documentation

**Files:**
- Create: `README.md`
- Create: `examples/claude-desktop-config.json`

**Step 1: Create README**

Create comprehensive README with quick start, configuration reference, available tools, and examples.

**Step 2: Create example config**

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "npx",
      "args": ["mcp-proxmox-admin"],
      "env": {
        "PROXMOX_HOST": "192.168.1.100",
        "PROXMOX_API_TOKEN_ID": "user@pam!mytoken",
        "PROXMOX_API_TOKEN_SECRET": "your-secret-here",
        "PROXMOX_SSH_USER": "root",
        "PROXMOX_SSH_KEY_PATH": "~/.ssh/id_rsa",
        "PROXMOX_DEFAULT_TRANSPORT": "auto"
      }
    }
  }
}
```

**Step 3: Commit**

```bash
git add README.md examples/
git commit -m "docs: add README and Claude Desktop configuration example"
```

---

## Task 11: Build and Test

**Step 1: Build the project**

Run: `npm run build`
Expected: Compiles to dist/ without errors

**Step 2: Run all tests**

Run: `npm test`
Expected: All tests pass

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: finalize build configuration"
```

---

## Summary

| Task | Description | Commits |
|------|-------------|---------|
| 1 | Project initialization | 1 |
| 2 | Configuration schema | 1 |
| 3 | Configuration loader | 1 |
| 4 | Transport types | 1 |
| 5 | SSH transport | 1 |
| 6 | API transport | 1 |
| 7 | Transport router | 1 |
| 8 | MCP server entry | 1 |
| 9 | Tool implementations | 1 |
| 10 | Documentation | 1 |
| 11 | Build & test | 1 |

**Total: 11 tasks, ~11 commits**
