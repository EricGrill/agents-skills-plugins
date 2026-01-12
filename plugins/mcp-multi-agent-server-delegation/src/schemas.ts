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
  env: z.record(z.string(), z.string()).optional(),
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
