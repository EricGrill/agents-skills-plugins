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
    if (!('content' in result) || !Array.isArray(result.content) || result.content.length === 0) {
      throw new Error('Unexpected response format');
    }

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
