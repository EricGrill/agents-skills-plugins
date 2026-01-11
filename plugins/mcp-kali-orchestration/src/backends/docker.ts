import Docker from "dockerode";
import { Readable, Writable } from "stream";
import { createWriteStream, createReadStream } from "fs";
import { mkdir } from "fs/promises";
import path from "path";
import type {
  Backend,
  KaliInstance,
  StartOptions,
  ExecOptions,
  ExecResult,
} from "./interface.js";
import type { DockerConfig } from "../config.js";

const CONTAINER_LABEL = "mcp-kali";

export class DockerBackend implements Backend {
  private docker: Docker;
  private config: DockerConfig;

  constructor(config: DockerConfig) {
    this.config = config;
    this.docker = new Docker({ socketPath: config.socket });
  }

  async isAvailable(): Promise<boolean> {
    try {
      await this.docker.ping();
      return true;
    } catch {
      return false;
    }
  }

  async start(options?: StartOptions): Promise<KaliInstance> {
    const name = options?.name || `kali-${Date.now()}`;

    const containerConfig: Docker.ContainerCreateOptions = {
      Image: this.config.image,
      name,
      Labels: {
        [CONTAINER_LABEL]: "true",
      },
      Tty: true,
      OpenStdin: true,
      HostConfig: {
        NetworkMode: options?.networkMode || "bridge",
        CapAdd: ["NET_ADMIN", "NET_RAW"], // Needed for many security tools
        SecurityOpt: ["seccomp=unconfined"], // Allow syscalls for tools
      },
    };

    if (options?.cpuLimit) {
      containerConfig.HostConfig!.NanoCpus = options.cpuLimit * 1e9;
    }

    if (options?.memoryLimitMb) {
      containerConfig.HostConfig!.Memory = options.memoryLimitMb * 1024 * 1024;
    }

    const container = await this.docker.createContainer(containerConfig);
    await container.start();

    const info = await container.inspect();

    return {
      id: container.id,
      name,
      status: "running",
      createdAt: new Date(info.Created),
      backend: "docker",
      ip: info.NetworkSettings.IPAddress || undefined,
    };
  }

  async stop(instanceId: string): Promise<void> {
    const container = this.docker.getContainer(instanceId);
    try {
      await container.stop({ t: 5 });
    } catch {
      // Container might already be stopped
    }
    await container.remove({ force: true });
  }

  async list(): Promise<KaliInstance[]> {
    const containers = await this.docker.listContainers({
      all: true,
      filters: {
        label: [CONTAINER_LABEL],
      },
    });

    return containers.map((c) => ({
      id: c.Id,
      name: c.Names[0]?.replace(/^\//, "") || c.Id.slice(0, 12),
      status: c.State === "running" ? "running" : "stopped",
      createdAt: new Date(c.Created * 1000),
      backend: "docker" as const,
      ip:
        c.NetworkSettings?.Networks?.bridge?.IPAddress ||
        Object.values(c.NetworkSettings?.Networks || {})[0]?.IPAddress,
    }));
  }

  /**
   * Run a command inside a Docker container using Docker's API.
   * Note: This uses Docker's container exec API, not Node.js child_process.
   * Commands are passed as an array to prevent shell injection.
   */
  async execCommand(
    instanceId: string,
    command: string[],
    options?: ExecOptions
  ): Promise<ExecResult> {
    const container = this.docker.getContainer(instanceId);

    // Using Docker's exec API - commands passed as array (safe)
    const dockerExecConfig: Docker.ExecCreateOptions = {
      Cmd: command,
      AttachStdout: true,
      AttachStderr: true,
      User: options?.user || "root",
      WorkingDir: options?.workdir,
      Env: options?.env
        ? Object.entries(options.env).map(([k, v]) => `${k}=${v}`)
        : undefined,
    };

    const dockerExec = await container.exec(dockerExecConfig);

    return new Promise((resolve, reject) => {
      const timeoutMs = options?.timeoutMs || 120000;
      let stdout = "";
      let stderr = "";
      let timedOut = false;

      const timeout = setTimeout(() => {
        timedOut = true;
        reject(new Error(`Command timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      dockerExec.start({ Tty: false }, (err, stream) => {
        if (err) {
          clearTimeout(timeout);
          return reject(err);
        }

        if (!stream) {
          clearTimeout(timeout);
          return reject(new Error("No stream returned from Docker exec"));
        }

        // Demux stdout and stderr from the multiplexed stream
        const stdoutStream = new Writable({
          write(chunk, _encoding, callback) {
            stdout += chunk.toString();
            callback();
          },
        });

        const stderrStream = new Writable({
          write(chunk, _encoding, callback) {
            stderr += chunk.toString();
            callback();
          },
        });

        this.docker.modem.demuxStream(stream, stdoutStream, stderrStream);

        stream.on("end", async () => {
          if (timedOut) return;
          clearTimeout(timeout);

          try {
            const inspectResult = await dockerExec.inspect();
            resolve({
              stdout: stdout.trim(),
              stderr: stderr.trim(),
              exitCode: inspectResult.ExitCode ?? 0,
            });
          } catch (inspectErr) {
            reject(inspectErr);
          }
        });

        stream.on("error", (streamErr) => {
          clearTimeout(timeout);
          reject(streamErr);
        });
      });
    });
  }

  async upload(
    instanceId: string,
    localPath: string,
    remotePath: string
  ): Promise<void> {
    const container = this.docker.getContainer(instanceId);
    const remoteDir = path.dirname(remotePath);
    const fileName = path.basename(remotePath);

    // Create a tar archive with the file
    const tar = await import("tar-stream");
    const pack = tar.pack();

    const fileStream = createReadStream(localPath);
    const chunks: Buffer[] = [];

    for await (const chunk of fileStream) {
      chunks.push(chunk as Buffer);
    }

    const fileContent = Buffer.concat(chunks);

    pack.entry({ name: fileName }, fileContent);
    pack.finalize();

    await container.putArchive(pack as unknown as Readable, { path: remoteDir });
  }

  async download(
    instanceId: string,
    remotePath: string,
    localPath: string
  ): Promise<void> {
    const container = this.docker.getContainer(instanceId);

    const stream = await container.getArchive({ path: remotePath });

    const tar = await import("tar-stream");
    const extract = tar.extract();

    // Ensure local directory exists
    await mkdir(path.dirname(localPath), { recursive: true });

    return new Promise((resolve, reject) => {
      extract.on("entry", (header, entryStream, next) => {
        const writeStream = createWriteStream(localPath);
        entryStream.pipe(writeStream);
        entryStream.on("end", () => {
          writeStream.end();
          next();
        });
      });

      extract.on("finish", resolve);
      extract.on("error", reject);

      stream.pipe(extract);
    });
  }
}
