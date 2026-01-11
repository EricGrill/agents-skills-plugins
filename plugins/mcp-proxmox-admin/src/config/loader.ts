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
