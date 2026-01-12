import { describe, it, expect, beforeEach } from 'vitest';
import { JobStore } from './store.js';
import type { JobManifest } from './types.js';

describe('JobStore', () => {
  let store: JobStore;

  const testManifest: JobManifest = {
    task: 'Run tests',
    agentType: 'script',
  };

  beforeEach(() => {
    store = new JobStore();
  });

  it('creates a job and returns id', () => {
    const id = store.createJob(testManifest);
    expect(id).toMatch(/^[0-9a-f-]{36}$/);
  });

  it('retrieves a job by id', () => {
    const id = store.createJob(testManifest);
    const job = store.getJob(id);
    expect(job).toBeDefined();
    expect(job?.manifest.task).toBe('Run tests');
    expect(job?.status).toBe('pending');
  });

  it('returns undefined for unknown job', () => {
    const job = store.getJob('nonexistent');
    expect(job).toBeUndefined();
  });

  it('updates job status', () => {
    const id = store.createJob(testManifest);
    store.updateJob(id, { status: 'running', vmId: 'vm-123' });
    const job = store.getJob(id);
    expect(job?.status).toBe('running');
    expect(job?.vmId).toBe('vm-123');
  });

  it('lists all jobs', () => {
    store.createJob(testManifest);
    store.createJob({ ...testManifest, task: 'Build app' });
    const jobs = store.listJobs();
    expect(jobs).toHaveLength(2);
  });

  it('filters jobs by status', () => {
    const id1 = store.createJob(testManifest);
    store.createJob(testManifest);
    store.updateJob(id1, { status: 'running' });

    const running = store.listJobs('running');
    expect(running).toHaveLength(1);
  });

  it('deletes a job', () => {
    const id = store.createJob(testManifest);
    store.deleteJob(id);
    expect(store.getJob(id)).toBeUndefined();
  });
});
