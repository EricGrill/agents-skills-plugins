export type AgentType = 'claude' | 'script' | 'custom';
export type JobStatus = 'pending' | 'provisioning' | 'running' | 'success' | 'failed' | 'timeout';
export type StatusMode = 'simple' | 'detailed' | 'streaming';
export type Lifecycle = 'ephemeral' | 'persistent';

export interface JobFile {
  path: string;
  content: string;  // base64 for binary
}

export interface JobResources {
  cpu?: number;
  memory?: string;
  disk?: string;
}

export interface AgentConfig {
  command?: string;
  claudeModel?: string;
}

export interface JobManifest {
  task: string;
  agentType: AgentType;
  agent?: AgentConfig;
  files?: JobFile[];
  env?: Record<string, string>;
  secrets?: string[];
  resources?: JobResources;
  timeout?: number;
  lifecycle?: Lifecycle;
  vmTemplate?: string;
  statusMode?: StatusMode;
}

export interface JobState {
  id: string;
  manifest: JobManifest;
  status: JobStatus;
  vmId?: string;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  output?: string;
  error?: string;
  artifacts?: unknown[];
  lastHeartbeat?: Date;
  progress?: string;
}

export interface CallbackPayload {
  job_id: string;
  status: 'success' | 'failed';
  exit_code: number;
  output: string;
  artifacts?: unknown[];
  duration_seconds: number;
  error?: string;
}

export interface StatusUpdate {
  job_id: string;
  progress: string;
  output?: string;
}
