// src/transports/ssh.ts
import { Client, type ConnectConfig, type ClientChannel } from "ssh2";
import { readFileSync } from "fs";
import type { Config } from "../config/index.js";
import type { Transport, CommandResult } from "./types.js";
import type {
  VMStatus,
  ContainerStatus,
  NodeStatus,
  StorageInfo,
  Snapshot,
  TaskResult,
} from "../types/proxmox.js";

export class SSHTransport implements Transport {
  private client: Client;
  private config: Config;
  private connected: boolean = false;

  constructor(config: Config) {
    this.config = config;
    this.client = new Client();
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const connectConfig: ConnectConfig = {
        host: this.config.host,
        port: this.config.sshPort,
        username: this.config.sshUser,
        readyTimeout: this.config.timeout,
      };

      if (this.config.sshKeyPath) {
        connectConfig.privateKey = readFileSync(this.config.sshKeyPath);
      } else if (this.config.sshPassword) {
        connectConfig.password = this.config.sshPassword;
      }

      this.client.on("ready", () => {
        this.connected = true;
        resolve();
      });

      this.client.on("error", (err) => {
        this.connected = false;
        reject(err);
      });

      this.client.connect(connectConfig);
    });
  }

  async disconnect(): Promise<void> {
    this.client.end();
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  async executeCommand(command: string): Promise<CommandResult> {
    return new Promise((resolve, reject) => {
      if (!this.connected) {
        reject(new Error("SSH client not connected"));
        return;
      }

      this.client.exec(command, (err, stream: ClientChannel) => {
        if (err) {
          reject(err);
          return;
        }

        let stdout = "";
        let stderr = "";

        stream.on("close", (code: number) => {
          resolve({
            success: code === 0,
            stdout,
            stderr,
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
  }

  async apiRequest<T>(_method: string, _endpoint: string, _data?: unknown): Promise<T> {
    throw new Error("SSH transport does not support direct API requests. Use executeCommand with pvesh instead.");
  }

  // Parse output from `qm list`
  parseVMListOutput(output: string, node: string): VMStatus[] {
    const lines = output.trim().split("\n");
    const vms: VMStatus[] = [];

    // Skip header line
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Format: VMID NAME STATUS MEM(MB) BOOTDISK(GB) PID
      const parts = line.split(/\s+/);
      if (parts.length >= 4) {
        const vmid = parseInt(parts[0], 10);
        const name = parts[1];
        const status = parts[2].toLowerCase() as "running" | "stopped" | "paused";
        const mem = parseInt(parts[3], 10) * 1024 * 1024; // Convert MB to bytes

        vms.push({
          vmid,
          name,
          status,
          node,
          cpu: 0,
          mem,
          maxmem: mem,
          disk: 0,
          maxdisk: 0,
          uptime: 0,
          template: false,
        });
      }
    }

    return vms;
  }

  // Parse output from `pct list`
  parseContainerListOutput(output: string, node: string): ContainerStatus[] {
    const lines = output.trim().split("\n");
    const containers: ContainerStatus[] = [];

    // Skip header line
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Format: VMID Status Lock Name
      const parts = line.split(/\s+/);
      if (parts.length >= 2) {
        const vmid = parseInt(parts[0], 10);
        const status = parts[1].toLowerCase() as "running" | "stopped";
        // Name is last part (Lock might be empty)
        const name = parts[parts.length - 1];

        containers.push({
          vmid,
          name,
          status,
          node,
          cpu: 0,
          mem: 0,
          maxmem: 0,
          disk: 0,
          maxdisk: 0,
          uptime: 0,
          template: false,
        });
      }
    }

    return containers;
  }

  // Parse JSON output from pvesh commands
  parseSnapshotListOutput(output: string): Snapshot[] {
    try {
      const data = JSON.parse(output);
      return data.map((item: Record<string, unknown>) => ({
        name: item.name as string,
        description: (item.description as string) || "",
        snaptime: item.snaptime as number | undefined,
        parent: item.parent as string | undefined,
      }));
    } catch {
      return [];
    }
  }

  private async getDefaultNode(): Promise<string> {
    if (this.config.defaultNode) {
      return this.config.defaultNode;
    }
    const nodes = await this.listNodes();
    if (nodes.length === 0) {
      throw new Error("No nodes available");
    }
    return nodes[0].node;
  }

  // VM Operations
  async listVMs(node?: string): Promise<VMStatus[]> {
    const targetNode = node || (await this.getDefaultNode());
    const result = await this.executeCommand("qm list");
    if (!result.success) {
      throw new Error(`Failed to list VMs: ${result.stderr}`);
    }
    return this.parseVMListOutput(result.stdout, targetNode);
  }

  async getVM(node: string, vmid: number): Promise<VMStatus> {
    const result = await this.executeCommand(`pvesh get /nodes/${node}/qemu/${vmid}/status/current --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to get VM ${vmid}: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return {
      vmid,
      name: data.name || `vm-${vmid}`,
      status: data.status as "running" | "stopped" | "paused",
      node,
      cpu: data.cpu || 0,
      mem: data.mem || 0,
      maxmem: data.maxmem || 0,
      disk: data.disk || 0,
      maxdisk: data.maxdisk || 0,
      uptime: data.uptime || 0,
      template: data.template === 1,
    };
  }

  async startVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm start ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} started` : result.stderr,
    };
  }

  async stopVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm stop ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} stopped` : result.stderr,
    };
  }

  async shutdownVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm shutdown ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} shutdown initiated` : result.stderr,
    };
  }

  async restartVM(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`qm reboot ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `VM ${vmid} restarted` : result.stderr,
    };
  }

  // Container Operations
  async listContainers(node?: string): Promise<ContainerStatus[]> {
    const targetNode = node || (await this.getDefaultNode());
    const result = await this.executeCommand("pct list");
    if (!result.success) {
      throw new Error(`Failed to list containers: ${result.stderr}`);
    }
    return this.parseContainerListOutput(result.stdout, targetNode);
  }

  async getContainer(node: string, vmid: number): Promise<ContainerStatus> {
    const result = await this.executeCommand(`pvesh get /nodes/${node}/lxc/${vmid}/status/current --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to get container ${vmid}: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return {
      vmid,
      name: data.name || `ct-${vmid}`,
      status: data.status as "running" | "stopped",
      node,
      cpu: data.cpu || 0,
      mem: data.mem || 0,
      maxmem: data.maxmem || 0,
      disk: data.disk || 0,
      maxdisk: data.maxdisk || 0,
      uptime: data.uptime || 0,
      template: data.template === 1,
    };
  }

  async startContainer(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`pct start ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `Container ${vmid} started` : result.stderr,
    };
  }

  async stopContainer(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`pct stop ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `Container ${vmid} stopped` : result.stderr,
    };
  }

  async restartContainer(node: string, vmid: number): Promise<TaskResult> {
    const result = await this.executeCommand(`pct reboot ${vmid}`);
    return {
      success: result.success,
      message: result.success ? `Container ${vmid} restarted` : result.stderr,
    };
  }

  // Node Operations
  async listNodes(): Promise<NodeStatus[]> {
    const result = await this.executeCommand("pvesh get /nodes --output-format json");
    if (!result.success) {
      throw new Error(`Failed to list nodes: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return data.map((item: Record<string, unknown>) => ({
      node: item.node as string,
      status: item.status as "online" | "offline",
      cpu: item.cpu as number || 0,
      maxcpu: item.maxcpu as number || 0,
      mem: item.mem as number || 0,
      maxmem: item.maxmem as number || 0,
      disk: item.disk as number || 0,
      maxdisk: item.maxdisk as number || 0,
      uptime: item.uptime as number || 0,
    }));
  }

  async getNodeStatus(node: string): Promise<NodeStatus> {
    const result = await this.executeCommand(`pvesh get /nodes/${node}/status --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to get node status: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return {
      node,
      status: "online",
      cpu: data.cpu || 0,
      maxcpu: data.cpuinfo?.cpus || 0,
      mem: data.memory?.used || 0,
      maxmem: data.memory?.total || 0,
      disk: data.rootfs?.used || 0,
      maxdisk: data.rootfs?.total || 0,
      uptime: data.uptime || 0,
    };
  }

  // Storage Operations
  async listStorage(node?: string): Promise<StorageInfo[]> {
    const targetNode = node || (await this.getDefaultNode());
    const result = await this.executeCommand(`pvesh get /nodes/${targetNode}/storage --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to list storage: ${result.stderr}`);
    }
    const data = JSON.parse(result.stdout);
    return data.map((item: Record<string, unknown>) => ({
      storage: item.storage as string,
      type: item.type as string,
      content: item.content as string || "",
      active: (item.active as number) === 1,
      enabled: (item.enabled as number) === 1,
      shared: (item.shared as number) === 1,
      total: item.total as number || 0,
      used: item.used as number || 0,
      avail: item.avail as number || 0,
    }));
  }

  // Snapshot Operations
  async listSnapshots(node: string, vmid: number, type: "vm" | "ct"): Promise<Snapshot[]> {
    const apiPath = type === "vm" ? "qemu" : "lxc";
    const result = await this.executeCommand(`pvesh get /nodes/${node}/${apiPath}/${vmid}/snapshot --output-format json`);
    if (!result.success) {
      throw new Error(`Failed to list snapshots: ${result.stderr}`);
    }
    return this.parseSnapshotListOutput(result.stdout);
  }

  async createSnapshot(
    node: string,
    vmid: number,
    type: "vm" | "ct",
    name: string,
    description?: string
  ): Promise<TaskResult> {
    const cmd = type === "vm" ? "qm" : "pct";
    let command = `${cmd} snapshot ${vmid} ${name}`;
    if (description) {
      command += ` --description "${description}"`;
    }
    const result = await this.executeCommand(command);
    return {
      success: result.success,
      message: result.success ? `Snapshot ${name} created` : result.stderr,
    };
  }

  async deleteSnapshot(
    node: string,
    vmid: number,
    type: "vm" | "ct",
    name: string
  ): Promise<TaskResult> {
    const cmd = type === "vm" ? "qm" : "pct";
    const result = await this.executeCommand(`${cmd} delsnapshot ${vmid} ${name}`);
    return {
      success: result.success,
      message: result.success ? `Snapshot ${name} deleted` : result.stderr,
    };
  }

  async restoreSnapshot(
    node: string,
    vmid: number,
    type: "vm" | "ct",
    name: string
  ): Promise<TaskResult> {
    const cmd = type === "vm" ? "qm" : "pct";
    const result = await this.executeCommand(`${cmd} rollback ${vmid} ${name}`);
    return {
      success: result.success,
      message: result.success ? `Snapshot ${name} restored` : result.stderr,
    };
  }
}
