import { Client } from "ssh2";
import { readFileSync } from "fs";
import { homedir } from "os";
import type {
  Backend,
  KaliInstance,
  StartOptions,
  ExecOptions,
  ExecResult,
} from "./interface.js";
import type { ProxmoxConfig } from "../config.js";

interface ProxmoxVM {
  vmid: number;
  name: string;
  status: string;
  node: string;
}

export class ProxmoxBackend implements Backend {
  private config: ProxmoxConfig;
  private baseUrl: string;
  private authHeaders: Record<string, string>;
  private templateVmid: number | null = null;

  constructor(config: ProxmoxConfig) {
    this.config = config;
    this.baseUrl = `https://${config.host}:${config.port}/api2/json`;
    this.authHeaders = {
      Authorization: `PVEAPIToken=${config.apiTokenId}=${config.apiTokenSecret}`,
    };
  }

  private async apiRequest<T>(
    method: string,
    endpoint: string,
    body?: Record<string, unknown>
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const options: RequestInit = {
      method,
      headers: {
        ...this.authHeaders,
        "Content-Type": "application/json",
      },
    };

    if (body && (method === "POST" || method === "PUT")) {
      options.body = JSON.stringify(body);
    }

    // Note: In production, you'd want proper SSL cert handling
    const response = await fetch(url, options);

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Proxmox API error: ${response.status} - ${text}`);
    }

    const json = (await response.json()) as { data: T };
    return json.data;
  }

  async isAvailable(): Promise<boolean> {
    try {
      await this.apiRequest<{ version: string }>("GET", "/version");
      return true;
    } catch {
      return false;
    }
  }

  private async findNextVmid(): Promise<number> {
    // Get list of all VMs to find a free VMID
    const vms = await this.apiRequest<ProxmoxVM[]>(
      "GET",
      `/nodes/${this.config.targetNode}/qemu`
    );
    const usedIds = new Set(vms.map((vm) => vm.vmid));

    // Find first available ID starting from 100
    let vmid = 100;
    while (usedIds.has(vmid)) {
      vmid++;
    }
    return vmid;
  }

  private async getTemplateVmid(): Promise<number> {
    if (this.templateVmid !== null) {
      return this.templateVmid;
    }

    // Find the template VM by name or use configured template
    const vms = await this.apiRequest<ProxmoxVM[]>(
      "GET",
      `/nodes/${this.config.targetNode}/qemu`
    );

    // Look for a VM named "kali-template" or configured template
    const template = vms.find(
      (vm) => vm.name === "kali-template" || vm.name.includes("kali")
    );

    if (!template) {
      throw new Error(
        "No Kali template VM found. Please create a template VM named 'kali-template'"
      );
    }

    this.templateVmid = template.vmid;
    return this.templateVmid;
  }

  async start(options?: StartOptions): Promise<KaliInstance> {
    const name = options?.name || `kali-${Date.now()}`;
    const templateVmid = await this.getTemplateVmid();
    const newVmid = await this.findNextVmid();

    // Clone the template
    await this.apiRequest(
      "POST",
      `/nodes/${this.config.targetNode}/qemu/${templateVmid}/clone`,
      {
        newid: newVmid,
        name,
        full: 1, // Full clone, not linked
      }
    );

    // Wait for clone to complete
    await this.waitForTask(newVmid);

    // Start the VM
    await this.apiRequest(
      "POST",
      `/nodes/${this.config.targetNode}/qemu/${newVmid}/status/start`,
      {}
    );

    // Wait for VM to be running and get IP
    const ip = await this.waitForVmIp(newVmid);

    return {
      id: String(newVmid),
      name,
      status: "running",
      createdAt: new Date(),
      backend: "proxmox",
      ip,
    };
  }

  private async waitForTask(_vmid: number): Promise<void> {
    // Simple wait - in production, you'd poll the task status
    await new Promise((resolve) => setTimeout(resolve, 10000));
  }

  private async waitForVmIp(vmid: number, maxWaitMs = 120000): Promise<string> {
    const startTime = Date.now();

    while (Date.now() - startTime < maxWaitMs) {
      try {
        const agentInfo = await this.apiRequest<{
          result: Array<{ "ip-addresses"?: Array<{ "ip-address": string }> }>;
        }>(
          "GET",
          `/nodes/${this.config.targetNode}/qemu/${vmid}/agent/network-get-interfaces`
        );

        for (const iface of agentInfo.result || []) {
          const addresses = iface["ip-addresses"] || [];
          for (const addr of addresses) {
            const ip = addr["ip-address"];
            // Skip loopback and link-local
            if (ip && !ip.startsWith("127.") && !ip.startsWith("fe80:")) {
              return ip;
            }
          }
        }
      } catch {
        // QEMU agent might not be ready yet
      }

      await new Promise((resolve) => setTimeout(resolve, 5000));
    }

    throw new Error(`Timeout waiting for VM ${vmid} to get an IP address`);
  }

  async stop(instanceId: string): Promise<void> {
    const vmid = parseInt(instanceId, 10);

    // Stop the VM
    try {
      await this.apiRequest(
        "POST",
        `/nodes/${this.config.targetNode}/qemu/${vmid}/status/stop`,
        {}
      );
      await new Promise((resolve) => setTimeout(resolve, 5000));
    } catch {
      // VM might already be stopped
    }

    // Delete the VM
    await this.apiRequest(
      "DELETE",
      `/nodes/${this.config.targetNode}/qemu/${vmid}`
    );
  }

  async list(): Promise<KaliInstance[]> {
    const vms = await this.apiRequest<ProxmoxVM[]>(
      "GET",
      `/nodes/${this.config.targetNode}/qemu`
    );

    // Filter to only show VMs with "kali" in the name (excluding template)
    const kaliVms = vms.filter(
      (vm) =>
        vm.name.toLowerCase().includes("kali") &&
        !vm.name.toLowerCase().includes("template")
    );

    const instances: KaliInstance[] = [];

    for (const vm of kaliVms) {
      let ip: string | undefined;
      try {
        const agentInfo = await this.apiRequest<{
          result: Array<{ "ip-addresses"?: Array<{ "ip-address": string }> }>;
        }>(
          "GET",
          `/nodes/${this.config.targetNode}/qemu/${vm.vmid}/agent/network-get-interfaces`
        );
        for (const iface of agentInfo.result || []) {
          const addresses = iface["ip-addresses"] || [];
          for (const addr of addresses) {
            const ipAddr = addr["ip-address"];
            if (ipAddr && !ipAddr.startsWith("127.") && !ipAddr.startsWith("fe80:")) {
              ip = ipAddr;
              break;
            }
          }
          if (ip) break;
        }
      } catch {
        // Agent not available
      }

      instances.push({
        id: String(vm.vmid),
        name: vm.name,
        status: vm.status === "running" ? "running" : "stopped",
        createdAt: new Date(), // Proxmox doesn't easily expose creation time
        backend: "proxmox",
        ip,
      });
    }

    return instances;
  }

  /**
   * Run a command in a Proxmox VM via SSH.
   * Note: Uses ssh2 library's channel.exec method for SSH command execution.
   */
  async execCommand(
    instanceId: string,
    command: string[],
    options?: ExecOptions
  ): Promise<ExecResult> {
    const vmid = parseInt(instanceId, 10);

    // Get VM IP
    const instances = await this.list();
    const instance = instances.find((i) => i.id === instanceId);

    if (!instance?.ip) {
      throw new Error(`Cannot get IP for VM ${vmid}`);
    }

    return this.sshRunCommand(instance.ip, command, options);
  }

  /**
   * Execute a command over SSH using ssh2 library.
   * Commands are passed as array and joined - SSH inherently provides shell context.
   */
  private async sshRunCommand(
    host: string,
    command: string[],
    options?: ExecOptions
  ): Promise<ExecResult> {
    return new Promise((resolve, reject) => {
      const conn = new Client();
      const user = options?.user || this.config.sshUser;
      const keyPath =
        this.config.sshKeyPath?.replace("~", homedir()) ||
        `${homedir()}/.ssh/id_rsa`;

      let stdout = "";
      let stderr = "";

      conn.on("ready", () => {
        const cmdString = command.join(" ");
        // Using ssh2's channel exec - not Node.js child_process
        conn.exec(cmdString, (err, stream) => {
          if (err) {
            conn.end();
            return reject(err);
          }

          stream.on("close", (code: number) => {
            conn.end();
            resolve({
              stdout: stdout.trim(),
              stderr: stderr.trim(),
              exitCode: code,
            });
          });

          stream.on("data", (data: Buffer) => {
            stdout += data.toString();
          });

          stream.stderr.on("data", (data: Buffer) => {
            stderr += data.toString();
          });
        });
      });

      conn.on("error", (err) => {
        reject(err);
      });

      try {
        const privateKey = readFileSync(keyPath);
        conn.connect({
          host,
          port: 22,
          username: user,
          privateKey,
          timeout: options?.timeoutMs || 120000,
        });
      } catch (err) {
        reject(new Error(`Failed to read SSH key: ${err}`));
      }
    });
  }

  async upload(
    instanceId: string,
    localPath: string,
    remotePath: string
  ): Promise<void> {
    const instances = await this.list();
    const instance = instances.find((i) => i.id === instanceId);

    if (!instance?.ip) {
      throw new Error(`Cannot get IP for VM ${instanceId}`);
    }

    return new Promise((resolve, reject) => {
      const conn = new Client();
      const keyPath =
        this.config.sshKeyPath?.replace("~", homedir()) ||
        `${homedir()}/.ssh/id_rsa`;

      conn.on("ready", () => {
        conn.sftp((err, sftp) => {
          if (err) {
            conn.end();
            return reject(err);
          }

          sftp.fastPut(localPath, remotePath, (err) => {
            conn.end();
            if (err) reject(err);
            else resolve();
          });
        });
      });

      conn.on("error", reject);

      const privateKey = readFileSync(keyPath);
      conn.connect({
        host: instance.ip,
        port: 22,
        username: this.config.sshUser,
        privateKey,
      });
    });
  }

  async download(
    instanceId: string,
    remotePath: string,
    localPath: string
  ): Promise<void> {
    const instances = await this.list();
    const instance = instances.find((i) => i.id === instanceId);

    if (!instance?.ip) {
      throw new Error(`Cannot get IP for VM ${instanceId}`);
    }

    return new Promise((resolve, reject) => {
      const conn = new Client();
      const keyPath =
        this.config.sshKeyPath?.replace("~", homedir()) ||
        `${homedir()}/.ssh/id_rsa`;

      conn.on("ready", () => {
        conn.sftp((err, sftp) => {
          if (err) {
            conn.end();
            return reject(err);
          }

          sftp.fastGet(remotePath, localPath, (err) => {
            conn.end();
            if (err) reject(err);
            else resolve();
          });
        });
      });

      conn.on("error", reject);

      const privateKey = readFileSync(keyPath);
      conn.connect({
        host: instance.ip,
        port: 22,
        username: this.config.sshUser,
        privateKey,
      });
    });
  }
}
