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
