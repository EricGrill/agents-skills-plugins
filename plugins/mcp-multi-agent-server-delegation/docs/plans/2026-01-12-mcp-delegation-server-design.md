# MCP Multi-Agent Server Delegation - Design Document

## Overview

An MCP server that delegates tasks to isolated Proxmox VMs, enabling secure execution of untrusted code, long-running builds/tests, and user-submitted jobs. Agents inside VMs report back via HTTP callbacks.

## Requirements

- **Use Cases**: Untrusted code execution, builds/tests in clean environments, user-submitted jobs
- **Interface**: MCP server (tools callable by Claude/agents)
- **Agent Types**: Claude Code, custom scripts, configurable per job
- **VM Lifecycle**: Configurable (ephemeral default, persistent optional)
- **Communication**: HTTP webhook callbacks from agent to orchestrator
- **Status**: Configurable granularity (simple → detailed → streaming)
- **State Storage**: In-memory (non-persistent)

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
│  │ (in-memory) │  │ (in-memory) │  │ (receives agent results)│  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ MCP Protocol
┌─────────────────────────────▼───────────────────────────────────┐
│                    mcp-proxmox-admin                            │
│            (VM creation, management, destruction)               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                     Proxmox Cluster                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   VM Job 1   │  │   VM Job 2   │  │   VM Job 3   │          │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │          │
│  │ │Job Runner│ │  │ │Job Runner│ │  │ │Job Runner│ │          │
│  │ │  + Agent │ │  │ │  + Agent │ │  │ │  + Agent │ │          │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Tools

### `submit_job`
Submit a new job for execution.
- **Input**: Job manifest
- **Returns**: `job_id`

### `get_job_status`
Check current status of a job.
- **Input**: `job_id`
- **Returns**: Status, progress info, error message if failed

### `get_job_result`
Retrieve completed job results.
- **Input**: `job_id`
- **Returns**: Output/artifacts, execution logs, timing info

### `cancel_job`
Cancel a running or pending job.
- **Input**: `job_id`
- **Returns**: Success/failure

### `list_jobs`
List all jobs with optional filtering.
- **Input**: Optional status filter
- **Returns**: Array of job summaries

### `stream_job_output` (optional)
Real-time log stream for streaming mode jobs.
- **Input**: `job_id`
- **Returns**: Log stream

## Job Manifest

```typescript
interface JobManifest {
  // Required
  task: string;                    // What the agent should do
  agentType: 'claude' | 'script' | 'custom';

  // Agent configuration
  agent: {
    command?: string;              // Entry command for script/custom
    claudeModel?: string;          // Model for Claude agent
  };

  // Files to inject into VM
  files?: Array<{
    path: string;                  // Destination path in VM
    content: string;               // File content (base64 for binary)
  }>;

  // Environment
  env?: Record<string, string>;    // Environment variables
  secrets?: string[];              // Secret names to inject

  // Resources & limits
  resources?: {
    cpu?: number;                  // CPU cores
    memory?: string;               // e.g., "2G"
    disk?: string;                 // e.g., "10G"
  };
  timeout?: number;                // Max execution time in seconds

  // Lifecycle
  lifecycle?: 'ephemeral' | 'persistent';
  vmTemplate?: string;             // Proxmox template to use

  // Status reporting
  statusMode?: 'simple' | 'detailed' | 'streaming';
}
```

## Job Runner (Inside VM)

Lightweight script (~200 lines) injected into each VM:

### Startup Flow
1. VM boots from template
2. Job runner starts automatically (cloud-init/systemd)
3. Fetches job manifest from orchestrator
4. Sets up environment (env vars, files, secrets)

### Execution
1. Spawns appropriate agent (Claude CLI, script, custom binary)
2. Captures stdout/stderr
3. Sends progress updates based on `statusMode`
4. Monitors for timeout

### Completion
1. Collects exit code, output, artifacts
2. POSTs callback:
```json
{
  "job_id": "abc123",
  "status": "success",
  "exit_code": 0,
  "output": "...",
  "artifacts": [...],
  "duration_seconds": 142
}
```
3. Signals ready for cleanup if ephemeral

## Callback & Status

### HTTP Endpoints
```
POST /callback/:job_id/status    - Progress updates
POST /callback/:job_id/complete  - Final result
POST /callback/:job_id/heartbeat - Keep-alive
```

### Status State Machine
```
pending → provisioning → running → success
                ↓           ↓
              failed     failed/timeout
```

### In-Memory Store
```typescript
interface JobState {
  id: string;
  manifest: JobManifest;
  status: 'pending' | 'provisioning' | 'running' | 'success' | 'failed' | 'timeout';
  vmId?: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  output?: string;
  error?: string;
  artifacts?: any[];
  lastHeartbeat?: Date;
}
```

### Background Tasks
Every 30 seconds:
- Check for timed-out jobs → mark failed, destroy VM
- Check for stale heartbeats → mark failed, destroy VM
- Clean up completed ephemeral VMs

## Proxmox Integration

Uses mcp-proxmox-admin as MCP client:

```typescript
// Create VM
const vm = await proxmoxMcp.call('create_vm', {
  template: manifest.vmTemplate || 'default-agent-template',
  name: `job-${jobId}`,
  cpu: manifest.resources?.cpu || 2,
  memory: manifest.resources?.memory || '2G',
  disk: manifest.resources?.disk || '10G'
});

// Configure via cloud-init
await proxmoxMcp.call('configure_vm', {
  vmId: vm.id,
  cloudInit: { userData: generateCloudInit(jobId, manifest, callbackUrl) }
});

// Start
await proxmoxMcp.call('start_vm', { vmId: vm.id });

// Cleanup
await proxmoxMcp.call('destroy_vm', { vmId: job.vmId });
```

### VM Templates
Pre-configured with:
- Minimal base OS (Ubuntu/Debian)
- Job runner script
- Claude CLI (for claude agent type)
- Python/Node for scripts
- Network access to callback URL

## Security

### Network Isolation
- VMs in isolated VLAN
- Outbound restricted to callback URL only
- No VM-to-VM communication
- No internal infrastructure access

### Secrets Handling
- Never stored in manifest
- Injected at runtime via secure channel
- Scoped per-job
- Cleared after agent starts

### Resource Limits
- CPU/memory/disk quotas via Proxmox
- Timeouts enforced at multiple levels
- Optional network bandwidth limits

### VM Hardening
- Minimal base images
- Read-only root where possible
- No SSH access
- Unprivileged job runner user

### Orchestrator Protection
- Callback job_id validation
- Rate limiting
- Payload size limits
- HTTPS for callbacks
