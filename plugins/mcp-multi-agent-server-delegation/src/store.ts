import { randomUUID } from 'crypto';
import type { JobManifest, JobState, JobStatus } from './types.js';

export class JobStore {
  private jobs = new Map<string, JobState>();

  createJob(manifest: JobManifest): string {
    const id = randomUUID();
    const job: JobState = {
      id,
      manifest,
      status: 'pending',
      createdAt: new Date(),
    };
    this.jobs.set(id, job);
    return id;
  }

  getJob(id: string): JobState | undefined {
    return this.jobs.get(id);
  }

  updateJob(id: string, updates: Partial<Omit<JobState, 'id' | 'manifest' | 'createdAt'>>): boolean {
    const job = this.jobs.get(id);
    if (!job) return false;
    Object.assign(job, updates);
    return true;
  }

  listJobs(status?: JobStatus): JobState[] {
    const jobs = Array.from(this.jobs.values());
    if (status) {
      return jobs.filter(j => j.status === status);
    }
    return jobs;
  }

  deleteJob(id: string): boolean {
    return this.jobs.delete(id);
  }

  getTimedOutJobs(now: Date = new Date()): JobState[] {
    return Array.from(this.jobs.values()).filter(job => {
      if (job.status !== 'running' || !job.startedAt || !job.manifest.timeout) {
        return false;
      }
      const elapsed = (now.getTime() - job.startedAt.getTime()) / 1000;
      return elapsed > job.manifest.timeout;
    });
  }

  getStaleJobs(heartbeatThresholdSeconds: number, now: Date = new Date()): JobState[] {
    return Array.from(this.jobs.values()).filter(job => {
      if (job.status !== 'running' || !job.lastHeartbeat) {
        return false;
      }
      const elapsed = (now.getTime() - job.lastHeartbeat.getTime()) / 1000;
      return elapsed > heartbeatThresholdSeconds;
    });
  }
}
