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
