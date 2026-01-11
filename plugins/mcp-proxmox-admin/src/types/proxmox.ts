// src/types/proxmox.ts
export interface VMStatus {
  vmid: number;
  name: string;
  status: "running" | "stopped" | "paused";
  node: string;
  cpu: number;
  mem: number;
  maxmem: number;
  disk: number;
  maxdisk: number;
  uptime: number;
  template: boolean;
}

export interface ContainerStatus {
  vmid: number;
  name: string;
  status: "running" | "stopped";
  node: string;
  cpu: number;
  mem: number;
  maxmem: number;
  disk: number;
  maxdisk: number;
  uptime: number;
  template: boolean;
}

export interface NodeStatus {
  node: string;
  status: "online" | "offline";
  cpu: number;
  maxcpu: number;
  mem: number;
  maxmem: number;
  disk: number;
  maxdisk: number;
  uptime: number;
}

export interface StorageInfo {
  storage: string;
  type: string;
  content: string;
  active: boolean;
  enabled: boolean;
  shared: boolean;
  total: number;
  used: number;
  avail: number;
}

export interface Snapshot {
  name: string;
  description: string;
  snaptime?: number;
  parent?: string;
}

export interface TaskResult {
  success: boolean;
  taskId?: string;
  message?: string;
  data?: unknown;
}
