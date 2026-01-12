import express, { type Express, type Request, type Response } from 'express';
import type { Server } from 'http';
import { CallbackPayloadSchema, StatusUpdateSchema } from './schemas.js';
import type { JobStore } from './store.js';

export class CallbackServer {
  private app: Express;
  private server: Server | null = null;

  constructor(
    private store: JobStore,
    private port: number
  ) {
    this.app = express();
    this.app.use(express.json({ limit: '10mb' }));
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (_req: Request, res: Response) => {
      res.json({ status: 'ok' });
    });

    // Completion callback
    this.app.post('/callback/:jobId/complete', (req: Request, res: Response) => {
      const jobId = req.params.jobId as string;
      const job = this.store.getJob(jobId);

      if (!job) {
        res.status(404).json({ error: 'Job not found' });
        return;
      }

      const parsed = CallbackPayloadSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'Invalid payload', details: parsed.error });
        return;
      }

      const { status, output, error, artifacts } = parsed.data;
      this.store.updateJob(jobId, {
        status: status === 'success' ? 'success' : 'failed',
        output,
        error,
        artifacts,
        completedAt: new Date(),
      });

      res.json({ received: true });
    });

    // Status update
    this.app.post('/callback/:jobId/status', (req: Request, res: Response) => {
      const jobId = req.params.jobId as string;
      const job = this.store.getJob(jobId);

      if (!job) {
        res.status(404).json({ error: 'Job not found' });
        return;
      }

      const parsed = StatusUpdateSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'Invalid payload', details: parsed.error });
        return;
      }

      const { progress, output } = parsed.data;
      this.store.updateJob(jobId, {
        progress,
        ...(output && { output }),
        lastHeartbeat: new Date(),
      });

      res.json({ received: true });
    });

    // Heartbeat
    this.app.post('/callback/:jobId/heartbeat', (req: Request, res: Response) => {
      const jobId = req.params.jobId as string;
      const job = this.store.getJob(jobId);

      if (!job) {
        res.status(404).json({ error: 'Job not found' });
        return;
      }

      this.store.updateJob(jobId, { lastHeartbeat: new Date() });
      res.json({ received: true });
    });
  }

  async start(): Promise<void> {
    return new Promise((resolve) => {
      this.server = this.app.listen(this.port, () => {
        console.log(`Callback server listening on port ${this.port}`);
        resolve();
      });
    });
  }

  async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.server) {
        resolve();
        return;
      }
      this.server.close((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  getCallbackUrl(): string {
    return `http://localhost:${this.port}`;
  }
}
