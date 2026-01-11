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
