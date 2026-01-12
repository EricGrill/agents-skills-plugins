# MCP Delegation Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MCP server that delegates tasks to isolated Proxmox VMs with HTTP callback status reporting.

**Architecture:** TypeScript MCP server using @modelcontextprotocol/sdk. Connects to mcp-proxmox-admin as MCP client for VM management. HTTP server for callbacks. In-memory job state.

**Tech Stack:** TypeScript, @modelcontextprotocol/sdk, Express (callbacks), node-fetch, uuid

**Prerequisites:** mcp-proxmox-admin extended with `proxmox_vm_create` and `proxmox_vm_destroy` tools.

---

## Task 1: Project Setup

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `src/index.ts`

**Step 1: Initialize npm project**

Run:
```bash
npm init -y
```

**Step 2: Install dependencies**

Run:
```bash
npm install @modelcontextprotocol/sdk express uuid zod
npm install -D typescript @types/node @types/express @types/uuid tsx
```

**Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Step 4: Update package.json scripts**

Add to package.json:
```json
{
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts"
  }
}
```

**Step 5: Create minimal src/index.ts**

```typescript
console.log('MCP Delegation Server starting...');
```

**Step 6: Verify setup**

Run: `npm run dev`
Expected: "MCP Delegation Server starting..."

**Step 7: Commit**

```bash
git add package.json tsconfig.json src/index.ts package-lock.json
git commit -m "feat: initialize project with TypeScript and MCP SDK"
```

---

## Task 2: Job Types & Schema

**Files:**
- Create: `src/types.ts`
- Create: `src/schemas.ts`

**Step 1: Create type definitions**

Create `src/types.ts`:
```typescript
export type AgentType = 'claude' | 'script' | 'custom';
export type JobStatus = 'pending' | 'provisioning' | 'running' | 'success' | 'failed' | 'timeout';
export type StatusMode = 'simple' | 'detailed' | 'streaming';
export type Lifecycle = 'ephemeral' | 'persistent';

export interface JobFile {
  path: string;
  content: string;  // base64 for binary
}

export interface JobResources {
  cpu?: number;
  memory?: string;
  disk?: string;
}

export interface AgentConfig {
  command?: string;
  claudeModel?: string;
}

export interface JobManifest {
  task: string;
  agentType: AgentType;
  agent?: AgentConfig;
  files?: JobFile[];
  env?: Record<string, string>;
  secrets?: string[];
  resources?: JobResources;
  timeout?: number;
  lifecycle?: Lifecycle;
  vmTemplate?: string;
  statusMode?: StatusMode;
}

export interface JobState {
  id: string;
  manifest: JobManifest;
  status: JobStatus;
  vmId?: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  output?: string;
  error?: string;
  artifacts?: unknown[];
  lastHeartbeat?: Date;
  progress?: string;
}

export interface CallbackPayload {
  job_id: string;
  status: 'success' | 'failed';
  exit_code: number;
  output: string;
  artifacts?: unknown[];
  duration_seconds: number;
  error?: string;
}

export interface StatusUpdate {
  job_id: string;
  progress: string;
  output?: string;
}
```

**Step 2: Create Zod schemas for validation**

Create `src/schemas.ts`:
```typescript
import { z } from 'zod';

export const AgentConfigSchema = z.object({
  command: z.string().optional(),
  claudeModel: z.string().optional(),
});

export const JobFileSchema = z.object({
  path: z.string(),
  content: z.string(),
});

export const JobResourcesSchema = z.object({
  cpu: z.number().min(1).max(32).optional(),
  memory: z.string().regex(/^\d+[GMK]$/).optional(),
  disk: z.string().regex(/^\d+[GMK]$/).optional(),
});

export const JobManifestSchema = z.object({
  task: z.string().min(1),
  agentType: z.enum(['claude', 'script', 'custom']),
  agent: AgentConfigSchema.optional(),
  files: z.array(JobFileSchema).optional(),
  env: z.record(z.string()).optional(),
  secrets: z.array(z.string()).optional(),
  resources: JobResourcesSchema.optional(),
  timeout: z.number().min(1).max(86400).optional(),
  lifecycle: z.enum(['ephemeral', 'persistent']).optional(),
  vmTemplate: z.string().optional(),
  statusMode: z.enum(['simple', 'detailed', 'streaming']).optional(),
});

export const CallbackPayloadSchema = z.object({
  job_id: z.string().uuid(),
  status: z.enum(['success', 'failed']),
  exit_code: z.number(),
  output: z.string(),
  artifacts: z.array(z.unknown()).optional(),
  duration_seconds: z.number(),
  error: z.string().optional(),
});

export const StatusUpdateSchema = z.object({
  job_id: z.string().uuid(),
  progress: z.string(),
  output: z.string().optional(),
});
```

**Step 3: Verify types compile**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 4: Commit**

```bash
git add src/types.ts src/schemas.ts
git commit -m "feat: add job types and validation schemas"
```

---

## Task 3: Job Store

**Files:**
- Create: `src/store.ts`
- Create: `src/store.test.ts`

**Step 1: Write failing test for job store**

Create `src/store.test.ts`:
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { JobStore } from './store.js';
import type { JobManifest } from './types.js';

describe('JobStore', () => {
  let store: JobStore;

  const testManifest: JobManifest = {
    task: 'Run tests',
    agentType: 'script',
  };

  beforeEach(() => {
    store = new JobStore();
  });

  it('creates a job and returns id', () => {
    const id = store.createJob(testManifest);
    expect(id).toMatch(/^[0-9a-f-]{36}$/);
  });

  it('retrieves a job by id', () => {
    const id = store.createJob(testManifest);
    const job = store.getJob(id);
    expect(job).toBeDefined();
    expect(job?.manifest.task).toBe('Run tests');
    expect(job?.status).toBe('pending');
  });

  it('returns undefined for unknown job', () => {
    const job = store.getJob('nonexistent');
    expect(job).toBeUndefined();
  });

  it('updates job status', () => {
    const id = store.createJob(testManifest);
    store.updateJob(id, { status: 'running', vmId: 'vm-123' });
    const job = store.getJob(id);
    expect(job?.status).toBe('running');
    expect(job?.vmId).toBe('vm-123');
  });

  it('lists all jobs', () => {
    store.createJob(testManifest);
    store.createJob({ ...testManifest, task: 'Build app' });
    const jobs = store.listJobs();
    expect(jobs).toHaveLength(2);
  });

  it('filters jobs by status', () => {
    const id1 = store.createJob(testManifest);
    store.createJob(testManifest);
    store.updateJob(id1, { status: 'running' });

    const running = store.listJobs('running');
    expect(running).toHaveLength(1);
  });

  it('deletes a job', () => {
    const id = store.createJob(testManifest);
    store.deleteJob(id);
    expect(store.getJob(id)).toBeUndefined();
  });
});
```

**Step 2: Install vitest**

Run: `npm install -D vitest`

Add to package.json scripts:
```json
"test": "vitest run",
"test:watch": "vitest"
```

**Step 3: Run test to verify it fails**

Run: `npm test`
Expected: FAIL - cannot find module './store.js'

**Step 4: Implement job store**

Create `src/store.ts`:
```typescript
import { randomUUID } from 'crypto';
import type { JobManifest, JobState, JobStatus } from './types.js';

export class JobStore {
  private jobs = new Map<string, JobState>();

  createJob(manifest: JobManifest): string {
    const id = randomUUID();
    const job: JobState = {
      id,
      manifest,
      status: 'pending',
      createdAt: new Date(),
    };
    this.jobs.set(id, job);
    return id;
  }

  getJob(id: string): JobState | undefined {
    return this.jobs.get(id);
  }

  updateJob(id: string, updates: Partial<Omit<JobState, 'id' | 'manifest' | 'createdAt'>>): boolean {
    const job = this.jobs.get(id);
    if (!job) return false;
    Object.assign(job, updates);
    return true;
  }

  listJobs(status?: JobStatus): JobState[] {
    const jobs = Array.from(this.jobs.values());
    if (status) {
      return jobs.filter(j => j.status === status);
    }
    return jobs;
  }

  deleteJob(id: string): boolean {
    return this.jobs.delete(id);
  }

  getTimedOutJobs(now: Date = new Date()): JobState[] {
    return Array.from(this.jobs.values()).filter(job => {
      if (job.status !== 'running' || !job.startedAt || !job.manifest.timeout) {
        return false;
      }
      const elapsed = (now.getTime() - job.startedAt.getTime()) / 1000;
      return elapsed > job.manifest.timeout;
    });
  }

  getStaleJobs(heartbeatThresholdSeconds: number, now: Date = new Date()): JobState[] {
    return Array.from(this.jobs.values()).filter(job => {
      if (job.status !== 'running' || !job.lastHeartbeat) {
        return false;
      }
      const elapsed = (now.getTime() - job.lastHeartbeat.getTime()) / 1000;
      return elapsed > heartbeatThresholdSeconds;
    });
  }
}
```

**Step 5: Run tests to verify they pass**

Run: `npm test`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/store.ts src/store.test.ts package.json package-lock.json
git commit -m "feat: add in-memory job store with tests"
```

---

## Task 4: Callback HTTP Server

**Files:**
- Create: `src/callback-server.ts`
- Create: `src/callback-server.test.ts`

**Step 1: Write failing test**

Create `src/callback-server.test.ts`:
```typescript
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { CallbackServer } from './callback-server.js';
import { JobStore } from './store.js';

describe('CallbackServer', () => {
  let server: CallbackServer;
  let store: JobStore;
  let jobId: string;
  const port = 9876;
  const baseUrl = `http://localhost:${port}`;

  beforeAll(async () => {
    store = new JobStore();
    server = new CallbackServer(store, port);
    await server.start();
  });

  afterAll(async () => {
    await server.stop();
  });

  beforeEach(() => {
    jobId = store.createJob({ task: 'test', agentType: 'script' });
    store.updateJob(jobId, { status: 'running', startedAt: new Date() });
  });

  it('receives completion callback', async () => {
    const response = await fetch(`${baseUrl}/callback/${jobId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: jobId,
        status: 'success',
        exit_code: 0,
        output: 'Done!',
        duration_seconds: 10,
      }),
    });

    expect(response.status).toBe(200);
    const job = store.getJob(jobId);
    expect(job?.status).toBe('success');
    expect(job?.output).toBe('Done!');
  });

  it('receives status update', async () => {
    const response = await fetch(`${baseUrl}/callback/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: jobId,
        progress: 'Step 2 of 5',
      }),
    });

    expect(response.status).toBe(200);
    const job = store.getJob(jobId);
    expect(job?.progress).toBe('Step 2 of 5');
  });

  it('receives heartbeat', async () => {
    const response = await fetch(`${baseUrl}/callback/${jobId}/heartbeat`, {
      method: 'POST',
    });

    expect(response.status).toBe(200);
    const job = store.getJob(jobId);
    expect(job?.lastHeartbeat).toBeDefined();
  });

  it('rejects unknown job id', async () => {
    const response = await fetch(`${baseUrl}/callback/unknown-id/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: 'unknown-id',
        status: 'success',
        exit_code: 0,
        output: 'Done!',
        duration_seconds: 10,
      }),
    });

    expect(response.status).toBe(404);
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm test`
Expected: FAIL - cannot find module './callback-server.js'

**Step 3: Implement callback server**

Create `src/callback-server.ts`:
```typescript
import express, { type Express, type Request, type Response } from 'express';
import type { Server } from 'http';
import { CallbackPayloadSchema, StatusUpdateSchema } from './schemas.js';
import type { JobStore } from './store.js';

export class CallbackServer {
  private app: Express;
  private server: Server | null = null;

  constructor(
    private store: JobStore,
    private port: number
  ) {
    this.app = express();
    this.app.use(express.json({ limit: '10mb' }));
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (_req: Request, res: Response) => {
      res.json({ status: 'ok' });
    });

    // Completion callback
    this.app.post('/callback/:jobId/complete', (req: Request, res: Response) => {
      const { jobId } = req.params;
      const job = this.store.getJob(jobId);

      if (!job) {
        res.status(404).json({ error: 'Job not found' });
        return;
      }

      const parsed = CallbackPayloadSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'Invalid payload', details: parsed.error });
        return;
      }

      const { status, output, error, artifacts, exit_code } = parsed.data;
      this.store.updateJob(jobId, {
        status: status === 'success' ? 'success' : 'failed',
        output,
        error,
        artifacts,
        completedAt: new Date(),
      });

      res.json({ received: true });
    });

    // Status update
    this.app.post('/callback/:jobId/status', (req: Request, res: Response) => {
      const { jobId } = req.params;
      const job = this.store.getJob(jobId);

      if (!job) {
        res.status(404).json({ error: 'Job not found' });
        return;
      }

      const parsed = StatusUpdateSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'Invalid payload', details: parsed.error });
        return;
      }

      const { progress, output } = parsed.data;
      this.store.updateJob(jobId, {
        progress,
        ...(output && { output }),
        lastHeartbeat: new Date(),
      });

      res.json({ received: true });
    });

    // Heartbeat
    this.app.post('/callback/:jobId/heartbeat', (req: Request, res: Response) => {
      const { jobId } = req.params;
      const job = this.store.getJob(jobId);

      if (!job) {
        res.status(404).json({ error: 'Job not found' });
        return;
      }

      this.store.updateJob(jobId, { lastHeartbeat: new Date() });
      res.json({ received: true });
    });
  }

  async start(): Promise<void> {
    return new Promise((resolve) => {
      this.server = this.app.listen(this.port, () => {
        console.log(`Callback server listening on port ${this.port}`);
        resolve();
      });
    });
  }

  async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.server) {
        resolve();
        return;
      }
      this.server.close((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  getCallbackUrl(): string {
    return `http://localhost:${this.port}`;
  }
}
```

**Step 4: Run tests to verify they pass**

Run: `npm test`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/callback-server.ts src/callback-server.test.ts
git commit -m "feat: add HTTP callback server for job status"
```

---

## Task 5: Proxmox MCP Client

**Files:**
- Create: `src/proxmox-client.ts`

**Step 1: Create Proxmox MCP client wrapper**

Create `src/proxmox-client.ts`:
```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import type { JobManifest } from './types.js';

export interface VMInfo {
  vmId: string;
  node: string;
  status: string;
}

export class ProxmoxClient {
  private client: Client | null = null;
  private transport: StdioClientTransport | null = null;

  constructor(
    private proxmoxAdminPath: string,
    private callbackUrl: string
  ) {}

  async connect(): Promise<void> {
    this.transport = new StdioClientTransport({
      command: 'node',
      args: [this.proxmoxAdminPath],
    });

    this.client = new Client({
      name: 'mcp-delegation-server',
      version: '1.0.0',
    }, {
      capabilities: {},
    });

    await this.client.connect(this.transport);
  }

  async disconnect(): Promise<void> {
    await this.client?.close();
  }

  async createVM(jobId: string, manifest: JobManifest): Promise<VMInfo> {
    if (!this.client) throw new Error('Client not connected');

    const result = await this.client.callTool({
      name: 'proxmox_vm_create',
      arguments: {
        template: manifest.vmTemplate || 'agent-template',
        name: `job-${jobId}`,
        cpu: manifest.resources?.cpu || 2,
        memory: manifest.resources?.memory || '2G',
        disk: manifest.resources?.disk || '10G',
        cloudInit: this.generateCloudInit(jobId, manifest),
      },
    });

    // Parse result - adjust based on actual mcp-proxmox-admin response
    const content = result.content[0];
    if (content.type !== 'text') {
      throw new Error('Unexpected response type');
    }

    const data = JSON.parse(content.text);
    return {
      vmId: data.vmid?.toString() || data.vmId,
      node: data.node,
      status: 'created',
    };
  }

  async startVM(vmId: string): Promise<void> {
    if (!this.client) throw new Error('Client not connected');

    await this.client.callTool({
      name: 'proxmox_vm_start',
      arguments: { vmid: vmId },
    });
  }

  async destroyVM(vmId: string): Promise<void> {
    if (!this.client) throw new Error('Client not connected');

    // Stop first, then destroy
    try {
      await this.client.callTool({
        name: 'proxmox_vm_stop',
        arguments: { vmid: vmId },
      });
    } catch {
      // VM might already be stopped
    }

    await this.client.callTool({
      name: 'proxmox_vm_destroy',
      arguments: { vmid: vmId, confirm: true },
    });
  }

  private generateCloudInit(jobId: string, manifest: JobManifest): string {
    const jobRunner = this.generateJobRunnerScript(jobId, manifest);

    return `#cloud-config
write_files:
  - path: /opt/job-runner/manifest.json
    content: ${Buffer.from(JSON.stringify(manifest)).toString('base64')}
    encoding: base64
  - path: /opt/job-runner/run.sh
    content: ${Buffer.from(jobRunner).toString('base64')}
    encoding: base64
    permissions: '0755'
${manifest.files?.map(f => `  - path: ${f.path}
    content: ${f.content}
    encoding: base64`).join('\n') || ''}
runcmd:
  - /opt/job-runner/run.sh
`;
  }

  private generateJobRunnerScript(jobId: string, manifest: JobManifest): string {
    const envVars = Object.entries(manifest.env || {})
      .map(([k, v]) => `export ${k}="${v}"`)
      .join('\n');

    return `#!/bin/bash
set -e

JOB_ID="${jobId}"
CALLBACK_URL="${this.callbackUrl}"
TIMEOUT=${manifest.timeout || 3600}
STATUS_MODE="${manifest.statusMode || 'simple'}"

# Set environment
${envVars}

# Function to send callback
send_callback() {
  local status=$1
  local exit_code=$2
  local output=$3
  local error=$4

  curl -s -X POST "$CALLBACK_URL/callback/$JOB_ID/complete" \\
    -H "Content-Type: application/json" \\
    -d "{
      \\"job_id\\": \\"$JOB_ID\\",
      \\"status\\": \\"$status\\",
      \\"exit_code\\": $exit_code,
      \\"output\\": $(echo "$output" | jq -Rs .),
      \\"error\\": $(echo "$error" | jq -Rs .),
      \\"duration_seconds\\": $SECONDS
    }"
}

send_heartbeat() {
  while true; do
    sleep 30
    curl -s -X POST "$CALLBACK_URL/callback/$JOB_ID/heartbeat" || true
  done
}

# Start heartbeat in background
send_heartbeat &
HEARTBEAT_PID=$!
trap "kill $HEARTBEAT_PID 2>/dev/null || true" EXIT

# Run the agent
cd /opt/job-runner
OUTPUT_FILE=$(mktemp)
ERROR_FILE=$(mktemp)

${manifest.agentType === 'claude' ? `
# Run Claude agent
timeout $TIMEOUT claude --print "${manifest.task}" > "$OUTPUT_FILE" 2> "$ERROR_FILE"
EXIT_CODE=$?
` : manifest.agentType === 'script' ? `
# Run script
timeout $TIMEOUT ${manifest.agent?.command || 'bash -c "${manifest.task}"'} > "$OUTPUT_FILE" 2> "$ERROR_FILE"
EXIT_CODE=$?
` : `
# Run custom command
timeout $TIMEOUT ${manifest.agent?.command} > "$OUTPUT_FILE" 2> "$ERROR_FILE"
EXIT_CODE=$?
`}

OUTPUT=$(cat "$OUTPUT_FILE")
ERROR=$(cat "$ERROR_FILE")

if [ $EXIT_CODE -eq 0 ]; then
  send_callback "success" $EXIT_CODE "$OUTPUT" ""
else
  send_callback "failed" $EXIT_CODE "$OUTPUT" "$ERROR"
fi
`;
  }
}
```

**Step 2: Verify it compiles**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/proxmox-client.ts
git commit -m "feat: add Proxmox MCP client wrapper"
```

---

## Task 6: MCP Server with Tools

**Files:**
- Create: `src/server.ts`
- Modify: `src/index.ts`

**Step 1: Create MCP server with tools**

Create `src/server.ts`:
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { JobManifestSchema } from './schemas.js';
import { JobStore } from './store.js';
import { CallbackServer } from './callback-server.js';
import { ProxmoxClient } from './proxmox-client.js';
import type { JobStatus } from './types.js';

export class DelegationServer {
  private server: Server;
  private store: JobStore;
  private callbackServer: CallbackServer;
  private proxmox: ProxmoxClient;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(config: {
    callbackPort: number;
    proxmoxAdminPath: string;
  }) {
    this.store = new JobStore();
    this.callbackServer = new CallbackServer(this.store, config.callbackPort);
    this.proxmox = new ProxmoxClient(
      config.proxmoxAdminPath,
      this.callbackServer.getCallbackUrl()
    );

    this.server = new Server(
      {
        name: 'mcp-delegation-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'submit_job',
          description: 'Submit a job for execution in an isolated VM',
          inputSchema: {
            type: 'object',
            properties: {
              manifest: {
                type: 'object',
                description: 'Job manifest with task, agentType, and optional config',
                properties: {
                  task: { type: 'string', description: 'Task description for the agent' },
                  agentType: { type: 'string', enum: ['claude', 'script', 'custom'] },
                  agent: {
                    type: 'object',
                    properties: {
                      command: { type: 'string' },
                      claudeModel: { type: 'string' },
                    },
                  },
                  files: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        path: { type: 'string' },
                        content: { type: 'string' },
                      },
                    },
                  },
                  env: { type: 'object' },
                  resources: {
                    type: 'object',
                    properties: {
                      cpu: { type: 'number' },
                      memory: { type: 'string' },
                      disk: { type: 'string' },
                    },
                  },
                  timeout: { type: 'number' },
                  lifecycle: { type: 'string', enum: ['ephemeral', 'persistent'] },
                  vmTemplate: { type: 'string' },
                  statusMode: { type: 'string', enum: ['simple', 'detailed', 'streaming'] },
                },
                required: ['task', 'agentType'],
              },
            },
            required: ['manifest'],
          },
        },
        {
          name: 'get_job_status',
          description: 'Get the current status of a job',
          inputSchema: {
            type: 'object',
            properties: {
              job_id: { type: 'string', description: 'The job ID' },
            },
            required: ['job_id'],
          },
        },
        {
          name: 'get_job_result',
          description: 'Get the result of a completed job',
          inputSchema: {
            type: 'object',
            properties: {
              job_id: { type: 'string', description: 'The job ID' },
            },
            required: ['job_id'],
          },
        },
        {
          name: 'cancel_job',
          description: 'Cancel a running or pending job',
          inputSchema: {
            type: 'object',
            properties: {
              job_id: { type: 'string', description: 'The job ID' },
            },
            required: ['job_id'],
          },
        },
        {
          name: 'list_jobs',
          description: 'List all jobs, optionally filtered by status',
          inputSchema: {
            type: 'object',
            properties: {
              status: {
                type: 'string',
                enum: ['pending', 'provisioning', 'running', 'success', 'failed', 'timeout'],
                description: 'Filter by status',
              },
            },
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'submit_job':
          return this.handleSubmitJob(args as { manifest: unknown });

        case 'get_job_status':
          return this.handleGetJobStatus(args as { job_id: string });

        case 'get_job_result':
          return this.handleGetJobResult(args as { job_id: string });

        case 'cancel_job':
          return this.handleCancelJob(args as { job_id: string });

        case 'list_jobs':
          return this.handleListJobs(args as { status?: JobStatus });

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  private async handleSubmitJob(args: { manifest: unknown }) {
    const parsed = JobManifestSchema.safeParse(args.manifest);
    if (!parsed.success) {
      return {
        content: [{ type: 'text' as const, text: `Invalid manifest: ${parsed.error.message}` }],
        isError: true,
      };
    }

    const manifest = parsed.data;
    const jobId = this.store.createJob(manifest);

    // Start provisioning asynchronously
    this.provisionJob(jobId).catch((error) => {
      this.store.updateJob(jobId, {
        status: 'failed',
        error: `Provisioning failed: ${error.message}`,
        completedAt: new Date(),
      });
    });

    return {
      content: [{ type: 'text' as const, text: JSON.stringify({ job_id: jobId }) }],
    };
  }

  private async provisionJob(jobId: string): Promise<void> {
    const job = this.store.getJob(jobId);
    if (!job) return;

    this.store.updateJob(jobId, { status: 'provisioning' });

    try {
      const vm = await this.proxmox.createVM(jobId, job.manifest);
      await this.proxmox.startVM(vm.vmId);

      this.store.updateJob(jobId, {
        status: 'running',
        vmId: vm.vmId,
        startedAt: new Date(),
      });
    } catch (error) {
      throw error;
    }
  }

  private handleGetJobStatus(args: { job_id: string }) {
    const job = this.store.getJob(args.job_id);
    if (!job) {
      return {
        content: [{ type: 'text' as const, text: 'Job not found' }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify({
          job_id: job.id,
          status: job.status,
          progress: job.progress,
          error: job.error,
          created_at: job.createdAt,
          started_at: job.startedAt,
          completed_at: job.completedAt,
        }),
      }],
    };
  }

  private handleGetJobResult(args: { job_id: string }) {
    const job = this.store.getJob(args.job_id);
    if (!job) {
      return {
        content: [{ type: 'text' as const, text: 'Job not found' }],
        isError: true,
      };
    }

    if (job.status !== 'success' && job.status !== 'failed') {
      return {
        content: [{ type: 'text' as const, text: `Job not complete. Status: ${job.status}` }],
        isError: true,
      };
    }

    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify({
          job_id: job.id,
          status: job.status,
          output: job.output,
          error: job.error,
          artifacts: job.artifacts,
          duration_seconds: job.completedAt && job.startedAt
            ? (job.completedAt.getTime() - job.startedAt.getTime()) / 1000
            : null,
        }),
      }],
    };
  }

  private async handleCancelJob(args: { job_id: string }) {
    const job = this.store.getJob(args.job_id);
    if (!job) {
      return {
        content: [{ type: 'text' as const, text: 'Job not found' }],
        isError: true,
      };
    }

    if (job.status === 'success' || job.status === 'failed') {
      return {
        content: [{ type: 'text' as const, text: 'Job already completed' }],
        isError: true,
      };
    }

    if (job.vmId) {
      try {
        await this.proxmox.destroyVM(job.vmId);
      } catch {
        // VM might already be gone
      }
    }

    this.store.updateJob(args.job_id, {
      status: 'failed',
      error: 'Cancelled by user',
      completedAt: new Date(),
    });

    return {
      content: [{ type: 'text' as const, text: JSON.stringify({ cancelled: true }) }],
    };
  }

  private handleListJobs(args: { status?: JobStatus }) {
    const jobs = this.store.listJobs(args.status);
    const summaries = jobs.map(j => ({
      job_id: j.id,
      status: j.status,
      task: j.manifest.task.substring(0, 100),
      created_at: j.createdAt,
    }));

    return {
      content: [{ type: 'text' as const, text: JSON.stringify(summaries) }],
    };
  }

  private startCleanupInterval(): void {
    this.cleanupInterval = setInterval(async () => {
      // Handle timed out jobs
      const timedOut = this.store.getTimedOutJobs();
      for (const job of timedOut) {
        if (job.vmId) {
          try {
            await this.proxmox.destroyVM(job.vmId);
          } catch {
            // Continue anyway
          }
        }
        this.store.updateJob(job.id, {
          status: 'timeout',
          error: 'Job exceeded timeout',
          completedAt: new Date(),
        });
      }

      // Clean up completed ephemeral VMs
      const completed = this.store.listJobs().filter(
        j => (j.status === 'success' || j.status === 'failed' || j.status === 'timeout')
          && j.vmId
          && j.manifest.lifecycle !== 'persistent'
      );
      for (const job of completed) {
        if (job.vmId) {
          try {
            await this.proxmox.destroyVM(job.vmId);
            this.store.updateJob(job.id, { vmId: undefined });
          } catch {
            // Will retry next interval
          }
        }
      }
    }, 30000);
  }

  async start(): Promise<void> {
    await this.callbackServer.start();
    await this.proxmox.connect();
    this.startCleanupInterval();

    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }

  async stop(): Promise<void> {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    await this.callbackServer.stop();
    await this.proxmox.disconnect();
    await this.server.close();
  }
}
```

**Step 2: Update index.ts**

Replace `src/index.ts`:
```typescript
import { DelegationServer } from './server.js';

const CALLBACK_PORT = parseInt(process.env.CALLBACK_PORT || '8765', 10);
const PROXMOX_ADMIN_PATH = process.env.PROXMOX_ADMIN_PATH || './node_modules/mcp-proxmox-admin/dist/index.js';

async function main() {
  const server = new DelegationServer({
    callbackPort: CALLBACK_PORT,
    proxmoxAdminPath: PROXMOX_ADMIN_PATH,
  });

  process.on('SIGINT', async () => {
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await server.stop();
    process.exit(0);
  });

  await server.start();
}

main().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
```

**Step 3: Verify it compiles**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 4: Commit**

```bash
git add src/server.ts src/index.ts
git commit -m "feat: add MCP server with job delegation tools"
```

---

## Task 7: Configuration & Environment

**Files:**
- Create: `.env.example`
- Create: `src/config.ts`

**Step 1: Create config module**

Create `src/config.ts`:
```typescript
import { z } from 'zod';

const ConfigSchema = z.object({
  callbackPort: z.number().min(1).max(65535).default(8765),
  callbackHost: z.string().default('0.0.0.0'),
  proxmoxAdminPath: z.string(),
  defaultVmTemplate: z.string().default('agent-template'),
  defaultTimeout: z.number().min(1).default(3600),
  defaultCpu: z.number().min(1).default(2),
  defaultMemory: z.string().default('2G'),
  defaultDisk: z.string().default('10G'),
  heartbeatThresholdSeconds: z.number().min(30).default(120),
  cleanupIntervalSeconds: z.number().min(10).default(30),
});

export type Config = z.infer<typeof ConfigSchema>;

export function loadConfig(): Config {
  return ConfigSchema.parse({
    callbackPort: parseInt(process.env.CALLBACK_PORT || '8765', 10),
    callbackHost: process.env.CALLBACK_HOST || '0.0.0.0',
    proxmoxAdminPath: process.env.PROXMOX_ADMIN_PATH || './node_modules/mcp-proxmox-admin/dist/index.js',
    defaultVmTemplate: process.env.DEFAULT_VM_TEMPLATE || 'agent-template',
    defaultTimeout: parseInt(process.env.DEFAULT_TIMEOUT || '3600', 10),
    defaultCpu: parseInt(process.env.DEFAULT_CPU || '2', 10),
    defaultMemory: process.env.DEFAULT_MEMORY || '2G',
    defaultDisk: process.env.DEFAULT_DISK || '10G',
    heartbeatThresholdSeconds: parseInt(process.env.HEARTBEAT_THRESHOLD_SECONDS || '120', 10),
    cleanupIntervalSeconds: parseInt(process.env.CLEANUP_INTERVAL_SECONDS || '30', 10),
  });
}
```

**Step 2: Create .env.example**

Create `.env.example`:
```bash
# Callback server configuration
CALLBACK_PORT=8765
CALLBACK_HOST=0.0.0.0

# Path to mcp-proxmox-admin
PROXMOX_ADMIN_PATH=./node_modules/mcp-proxmox-admin/dist/index.js

# Default VM settings
DEFAULT_VM_TEMPLATE=agent-template
DEFAULT_TIMEOUT=3600
DEFAULT_CPU=2
DEFAULT_MEMORY=2G
DEFAULT_DISK=10G

# Monitoring
HEARTBEAT_THRESHOLD_SECONDS=120
CLEANUP_INTERVAL_SECONDS=30
```

**Step 3: Add .env to .gitignore**

Create `.gitignore`:
```
node_modules/
dist/
.env
*.log
```

**Step 4: Commit**

```bash
git add src/config.ts .env.example .gitignore
git commit -m "feat: add configuration management"
```

---

## Task 8: Build & Documentation

**Files:**
- Modify: `package.json`
- Create: `README.md`

**Step 1: Update package.json with bin entry**

Add to package.json:
```json
{
  "bin": {
    "mcp-delegation-server": "./dist/index.js"
  }
}
```

**Step 2: Build the project**

Run: `npm run build`
Expected: Compiles to dist/ without errors

**Step 3: Create README**

Create `README.md`:
```markdown
# MCP Multi-Agent Server Delegation

An MCP server that delegates tasks to isolated Proxmox VMs for secure execution.

## Features

- Execute untrusted code in isolated VMs
- Support for Claude, scripts, or custom agents
- HTTP callback status reporting
- Configurable VM lifecycle (ephemeral/persistent)
- Automatic timeout and cleanup

## Installation

```bash
npm install
npm run build
```

## Configuration

Copy `.env.example` to `.env` and configure:

- `CALLBACK_PORT` - Port for callback server (default: 8765)
- `PROXMOX_ADMIN_PATH` - Path to mcp-proxmox-admin

## Usage

### As MCP Server

Add to your MCP client config:

```json
{
  "mcpServers": {
    "delegation": {
      "command": "node",
      "args": ["/path/to/dist/index.js"],
      "env": {
        "CALLBACK_PORT": "8765",
        "PROXMOX_ADMIN_PATH": "/path/to/mcp-proxmox-admin"
      }
    }
  }
}
```

### Available Tools

- `submit_job` - Submit a job for execution
- `get_job_status` - Check job status
- `get_job_result` - Get completed job results
- `cancel_job` - Cancel a job
- `list_jobs` - List all jobs

## Development

```bash
npm run dev      # Run in development mode
npm test         # Run tests
npm run build    # Build for production
```
```

**Step 4: Commit**

```bash
git add package.json README.md
git commit -m "feat: add build config and documentation"
```

---

## Summary

**Total Tasks: 8**

1. Project Setup - Initialize TypeScript project with MCP SDK
2. Job Types & Schema - Define types and Zod validation
3. Job Store - In-memory job state management
4. Callback Server - HTTP server for VM callbacks
5. Proxmox Client - MCP client for VM management
6. MCP Server - Main server with delegation tools
7. Configuration - Environment-based config
8. Build & Docs - Production build and README

**Architecture Notes:**
- Thin orchestrator pattern - complexity in job runner script
- Assumes mcp-proxmox-admin has `proxmox_vm_create` and `proxmox_vm_destroy` tools
- Job runner script injected via cloud-init
- Callback URL must be accessible from VMs (configure network accordingly)
