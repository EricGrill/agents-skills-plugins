export interface KaliInstance {
  id: string;
  name: string;
  status: "running" | "stopped" | "creating" | "error";
  createdAt: Date;
  backend: "docker" | "proxmox";
  ip?: string;
}

export interface StartOptions {
  name?: string;
  networkMode?: "bridge" | "host";
  cpuLimit?: number;
  memoryLimitMb?: number;
}

export interface ExecOptions {
  user?: "root" | "kali";
  workdir?: string;
  env?: Record<string, string>;
  timeoutMs?: number;
}

export interface ExecResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface Backend {
  /**
   * Start a new Kali instance
   */
  start(options?: StartOptions): Promise<KaliInstance>;

  /**
   * Stop and remove a Kali instance
   */
  stop(instanceId: string): Promise<void>;

  /**
   * List all Kali instances
   */
  list(): Promise<KaliInstance[]>;

  /**
   * Execute a command in a Kali instance
   * Note: This uses Docker exec API, not child_process.exec
   */
  execCommand(
    instanceId: string,
    command: string[],
    options?: ExecOptions
  ): Promise<ExecResult>;

  /**
   * Upload a file to a Kali instance
   */
  upload(
    instanceId: string,
    localPath: string,
    remotePath: string
  ): Promise<void>;

  /**
   * Download a file from a Kali instance
   */
  download(
    instanceId: string,
    remotePath: string,
    localPath: string
  ): Promise<void>;

  /**
   * Check if the backend is available
   */
  isAvailable(): Promise<boolean>;
}
