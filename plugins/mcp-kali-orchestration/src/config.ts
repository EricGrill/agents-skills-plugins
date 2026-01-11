import { z } from "zod";
import dotenv from "dotenv";

dotenv.config();

const dockerConfigSchema = z.object({
  socket: z.string().default("/var/run/docker.sock"),
  image: z.string().default("mcp-kali:latest"),
});

const proxmoxConfigSchema = z.object({
  host: z.string(),
  port: z.number().default(8006),
  apiTokenId: z.string(),
  apiTokenSecret: z.string(),
  sshUser: z.string().default("root"),
  sshKeyPath: z.string().optional(),
  kaliTemplate: z.string(),
  targetNode: z.string(),
});

const configSchema = z.object({
  backend: z.enum(["docker", "proxmox"]).default("docker"),
  docker: dockerConfigSchema,
  proxmox: proxmoxConfigSchema.optional(),
  execution: z.object({
    defaultTimeoutMs: z.number().default(120000),
    longRunningTimeoutMs: z.number().default(1800000),
    streamThresholdMs: z.number().default(60000),
  }),
});

export type Config = z.infer<typeof configSchema>;
export type DockerConfig = z.infer<typeof dockerConfigSchema>;
export type ProxmoxConfig = z.infer<typeof proxmoxConfigSchema>;

function loadConfig(): Config {
  const rawConfig = {
    backend: process.env.KALI_BACKEND || "docker",
    docker: {
      socket: process.env.DOCKER_SOCKET || "/var/run/docker.sock",
      image: process.env.KALI_IMAGE || "mcp-kali:latest",
    },
    proxmox: process.env.PROXMOX_HOST
      ? {
          host: process.env.PROXMOX_HOST,
          port: parseInt(process.env.PROXMOX_PORT || "8006", 10),
          apiTokenId: process.env.PROXMOX_API_TOKEN_ID || "",
          apiTokenSecret: process.env.PROXMOX_API_TOKEN_SECRET || "",
          sshUser: process.env.PROXMOX_SSH_USER || "root",
          sshKeyPath: process.env.PROXMOX_SSH_KEY_PATH,
          kaliTemplate: process.env.PROXMOX_KALI_TEMPLATE || "",
          targetNode: process.env.PROXMOX_TARGET_NODE || "",
        }
      : undefined,
    execution: {
      defaultTimeoutMs: parseInt(
        process.env.DEFAULT_TIMEOUT_MS || "120000",
        10
      ),
      longRunningTimeoutMs: parseInt(
        process.env.LONG_RUNNING_TIMEOUT_MS || "1800000",
        10
      ),
      streamThresholdMs: parseInt(
        process.env.STREAM_THRESHOLD_MS || "60000",
        10
      ),
    },
  };

  const result = configSchema.safeParse(rawConfig);

  if (!result.success) {
    console.error("Configuration validation failed:", result.error.format());
    throw new Error("Invalid configuration");
  }

  // Validate that proxmox config exists if backend is proxmox
  if (result.data.backend === "proxmox" && !result.data.proxmox) {
    throw new Error(
      "Proxmox backend selected but PROXMOX_HOST not configured"
    );
  }

  return result.data;
}

export const config = loadConfig();
