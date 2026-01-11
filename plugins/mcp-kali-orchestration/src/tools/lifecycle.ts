import type { Backend } from "../backends/interface.js";
import type { ToolDefinition } from "../server.js";

export function registerLifecycleTools(
  backend: Backend,
  tools: Map<string, ToolDefinition>
): void {
  // kali_start - Spin up a new Kali instance
  tools.set("kali_start", {
    name: "kali_start",
    description:
      "Start a new Kali Linux instance. Returns the instance ID to use with other tools.",
    inputSchema: {
      type: "object",
      properties: {
        name: {
          type: "string",
          description: "Optional name for the instance",
        },
        network_mode: {
          type: "string",
          enum: ["bridge", "host"],
          description: "Network mode (default: bridge)",
        },
        cpu_limit: {
          type: "number",
          description: "CPU limit in cores (e.g., 2.0)",
        },
        memory_limit_mb: {
          type: "number",
          description: "Memory limit in MB (e.g., 4096)",
        },
      },
    },
    handler: async (args) => {
      const instance = await backend.start({
        name: args.name as string | undefined,
        networkMode: args.network_mode as "bridge" | "host" | undefined,
        cpuLimit: args.cpu_limit as number | undefined,
        memoryLimitMb: args.memory_limit_mb as number | undefined,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: true,
                instance: {
                  id: instance.id,
                  name: instance.name,
                  status: instance.status,
                  ip: instance.ip,
                  backend: instance.backend,
                },
              },
              null,
              2
            ),
          },
        ],
      };
    },
  });

  // kali_stop - Stop and remove a Kali instance
  tools.set("kali_stop", {
    name: "kali_stop",
    description: "Stop and remove a Kali instance by ID or name.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: {
          type: "string",
          description: "The instance ID or name to stop",
        },
      },
      required: ["instance_id"],
    },
    handler: async (args) => {
      await backend.stop(args.instance_id as string);

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: true,
              message: `Instance ${args.instance_id} stopped and removed`,
            }),
          },
        ],
      };
    },
  });

  // kali_list - List all Kali instances
  tools.set("kali_list", {
    name: "kali_list",
    description: "List all running Kali instances.",
    inputSchema: {
      type: "object",
      properties: {},
    },
    handler: async () => {
      const instances = await backend.list();

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: true,
                instances: instances.map((i) => ({
                  id: i.id.slice(0, 12),
                  name: i.name,
                  status: i.status,
                  ip: i.ip,
                  created: i.createdAt.toISOString(),
                })),
                count: instances.length,
              },
              null,
              2
            ),
          },
        ],
      };
    },
  });

  // kali_exec - Run arbitrary command in a Kali instance
  tools.set("kali_exec", {
    name: "kali_exec",
    description:
      "Execute a command in a Kali instance. Use this for tools not explicitly wrapped.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: {
          type: "string",
          description: "The instance ID to run the command in",
        },
        command: {
          type: "string",
          description: "The command to execute (will be run via /bin/bash -c)",
        },
        user: {
          type: "string",
          enum: ["root", "kali"],
          description: "User to run as (default: root)",
        },
        timeout_ms: {
          type: "number",
          description: "Timeout in milliseconds (default: 120000)",
        },
      },
      required: ["instance_id", "command"],
    },
    handler: async (args) => {
      // Run command via bash to support pipes, redirects, etc.
      const result = await backend.execCommand(
        args.instance_id as string,
        ["/bin/bash", "-c", args.command as string],
        {
          user: (args.user as "root" | "kali") || "root",
          timeoutMs: (args.timeout_ms as number) || 120000,
        }
      );

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: result.exitCode === 0,
                exit_code: result.exitCode,
                stdout: result.stdout,
                stderr: result.stderr,
              },
              null,
              2
            ),
          },
        ],
      };
    },
  });

  // kali_upload - Upload file to instance
  tools.set("kali_upload", {
    name: "kali_upload",
    description:
      "Upload a file from the host to a Kali instance.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: {
          type: "string",
          description: "The instance ID",
        },
        local_path: {
          type: "string",
          description: "Path to the file on the host",
        },
        remote_path: {
          type: "string",
          description: "Destination path in the container",
        },
      },
      required: ["instance_id", "local_path", "remote_path"],
    },
    handler: async (args) => {
      await backend.upload(
        args.instance_id as string,
        args.local_path as string,
        args.remote_path as string
      );

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: true,
              message: `Uploaded ${args.local_path} to ${args.remote_path}`,
            }),
          },
        ],
      };
    },
  });

  // kali_download - Download file from instance
  tools.set("kali_download", {
    name: "kali_download",
    description:
      "Download a file from a Kali instance to the host.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: {
          type: "string",
          description: "The instance ID",
        },
        remote_path: {
          type: "string",
          description: "Path to the file in the container",
        },
        local_path: {
          type: "string",
          description: "Destination path on the host",
        },
      },
      required: ["instance_id", "remote_path", "local_path"],
    },
    handler: async (args) => {
      await backend.download(
        args.instance_id as string,
        args.remote_path as string,
        args.local_path as string
      );

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: true,
              message: `Downloaded ${args.remote_path} to ${args.local_path}`,
            }),
          },
        ],
      };
    },
  });
}
