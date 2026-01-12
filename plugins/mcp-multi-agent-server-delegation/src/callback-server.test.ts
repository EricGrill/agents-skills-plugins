import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { CallbackServer } from './callback-server.js';
import { JobStore } from './store.js';

describe('CallbackServer', () => {
  let server: CallbackServer;
  let store: JobStore;
  let jobId: string;
  const port = 9876;
  const baseUrl = `http://localhost:${port}`;

  beforeAll(async () => {
    store = new JobStore();
    server = new CallbackServer(store, port);
    await server.start();
  });

  afterAll(async () => {
    await server.stop();
  });

  beforeEach(() => {
    jobId = store.createJob({ task: 'test', agentType: 'script' });
    store.updateJob(jobId, { status: 'running', startedAt: new Date() });
  });

  it('receives completion callback', async () => {
    const response = await fetch(`${baseUrl}/callback/${jobId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: jobId,
        status: 'success',
        exit_code: 0,
        output: 'Done!',
        duration_seconds: 10,
      }),
    });

    expect(response.status).toBe(200);
    const job = store.getJob(jobId);
    expect(job?.status).toBe('success');
    expect(job?.output).toBe('Done!');
  });

  it('receives status update', async () => {
    const response = await fetch(`${baseUrl}/callback/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: jobId,
        progress: 'Step 2 of 5',
      }),
    });

    expect(response.status).toBe(200);
    const job = store.getJob(jobId);
    expect(job?.progress).toBe('Step 2 of 5');
  });

  it('receives heartbeat', async () => {
    const response = await fetch(`${baseUrl}/callback/${jobId}/heartbeat`, {
      method: 'POST',
    });

    expect(response.status).toBe(200);
    const job = store.getJob(jobId);
    expect(job?.lastHeartbeat).toBeDefined();
  });

  it('rejects unknown job id', async () => {
    const response = await fetch(`${baseUrl}/callback/unknown-id/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_id: 'unknown-id',
        status: 'success',
        exit_code: 0,
        output: 'Done!',
        duration_seconds: 10,
      }),
    });

    expect(response.status).toBe(404);
  });
});
