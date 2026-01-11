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
