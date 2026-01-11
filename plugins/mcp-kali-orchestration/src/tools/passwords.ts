import type { Backend } from "../backends/interface.js";
import type { ToolDefinition } from "../server.js";

function createToolRunner(
  backend: Backend,
  instanceIdArg: string,
  buildCommand: (args: Record<string, unknown>) => string[],
  timeoutMs = 300000
) {
  return async (args: Record<string, unknown>) => {
    const instanceId = args[instanceIdArg] as string;
    const command = buildCommand(args);

    const result = await backend.execCommand(instanceId, command, {
      user: "root",
      timeoutMs,
    });

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
  };
}

export function registerPasswordTools(
  backend: Backend,
  tools: Map<string, ToolDefinition>
): void {
  // hydra_attack - Online password cracking
  tools.set("hydra_attack", {
    name: "hydra_attack",
    description:
      "Online password cracking against network services (SSH, FTP, HTTP, etc.).",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        target: { type: "string", description: "Target IP or hostname" },
        service: {
          type: "string",
          description: "Service to attack (ssh, ftp, http-get, http-post-form, smb, rdp, etc.)",
        },
        username: { type: "string", description: "Single username" },
        userlist: { type: "string", description: "Path to username list" },
        password: { type: "string", description: "Single password" },
        passlist: { type: "string", description: "Path to password list" },
        port: { type: "number", description: "Service port" },
        threads: { type: "number", description: "Number of threads (default: 16)" },
        additional_args: {
          type: "string",
          description: "Additional hydra arguments (e.g., for http-post-form)",
        },
      },
      required: ["instance_id", "target", "service"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["hydra"];

        if (args.username) cmd.push("-l", args.username as string);
        if (args.userlist) cmd.push("-L", args.userlist as string);
        if (args.password) cmd.push("-p", args.password as string);
        if (args.passlist) cmd.push("-P", args.passlist as string);
        if (args.port) cmd.push("-s", String(args.port));
        if (args.threads) cmd.push("-t", String(args.threads));

        cmd.push(args.target as string);
        cmd.push(args.service as string);

        if (args.additional_args) {
          cmd.push(...(args.additional_args as string).split(/\s+/));
        }

        return cmd;
      },
      1800000 // 30 min
    ),
  });

  // medusa_attack - Parallel password cracker
  tools.set("medusa_attack", {
    name: "medusa_attack",
    description: "Parallel, modular login brute-forcer.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        target: { type: "string", description: "Target IP or hostname" },
        module: {
          type: "string",
          description: "Module to use (ssh, ftp, http, smb, rdp, etc.)",
        },
        username: { type: "string", description: "Single username" },
        userlist: { type: "string", description: "Path to username list" },
        password: { type: "string", description: "Single password" },
        passlist: { type: "string", description: "Path to password list" },
        port: { type: "number", description: "Service port" },
        threads: { type: "number", description: "Number of parallel threads" },
      },
      required: ["instance_id", "target", "module"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["medusa", "-h", args.target as string, "-M", args.module as string];

        if (args.username) cmd.push("-u", args.username as string);
        if (args.userlist) cmd.push("-U", args.userlist as string);
        if (args.password) cmd.push("-p", args.password as string);
        if (args.passlist) cmd.push("-P", args.passlist as string);
        if (args.port) cmd.push("-n", String(args.port));
        if (args.threads) cmd.push("-t", String(args.threads));

        return cmd;
      },
      1800000
    ),
  });

  // john_crack - Offline hash cracking
  tools.set("john_crack", {
    name: "john_crack",
    description: "Crack password hashes using John the Ripper.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        hashfile: { type: "string", description: "Path to file containing hashes" },
        format: {
          type: "string",
          description: "Hash format (e.g., 'md5', 'sha256', 'ntlm')",
        },
        wordlist: { type: "string", description: "Path to wordlist" },
        rules: { type: "string", description: "Rules to use (e.g., 'best64')" },
        show: {
          type: "boolean",
          description: "Show cracked passwords instead of cracking",
        },
      },
      required: ["instance_id", "hashfile"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["john"];

        if (args.show) {
          cmd.push("--show");
        } else {
          if (args.format) cmd.push(`--format=${args.format}`);
          if (args.wordlist) cmd.push(`--wordlist=${args.wordlist}`);
          if (args.rules) cmd.push(`--rules=${args.rules}`);
        }

        cmd.push(args.hashfile as string);
        return cmd;
      },
      3600000 // 1 hour for hash cracking
    ),
  });

  // hashcat_crack - GPU hash cracking
  tools.set("hashcat_crack", {
    name: "hashcat_crack",
    description:
      "GPU-accelerated password cracking. Note: GPU support depends on container setup.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        hashfile: { type: "string", description: "Path to file containing hashes" },
        mode: {
          type: "number",
          description: "Hash mode (e.g., 0=MD5, 1000=NTLM, 1800=sha512crypt)",
        },
        wordlist: { type: "string", description: "Path to wordlist" },
        rules: { type: "string", description: "Rules file" },
        attack_mode: {
          type: "number",
          description: "Attack mode (0=straight, 1=combination, 3=brute-force, 6=hybrid)",
        },
        show: { type: "boolean", description: "Show cracked passwords" },
      },
      required: ["instance_id", "hashfile", "mode"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["hashcat", "-m", String(args.mode)];

        if (args.show) {
          cmd.push("--show");
        } else {
          if (args.attack_mode !== undefined) cmd.push("-a", String(args.attack_mode));
          if (args.rules) cmd.push("-r", args.rules as string);
        }

        cmd.push(args.hashfile as string);
        if (args.wordlist && !args.show) cmd.push(args.wordlist as string);

        return cmd;
      },
      3600000
    ),
  });

  // hash_identifier - Identify hash type
  tools.set("hash_identifier", {
    name: "hash_identifier",
    description: "Identify the type of a hash.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        hash: { type: "string", description: "Hash to identify" },
      },
      required: ["instance_id", "hash"],
    },
    handler: createToolRunner(backend, "instance_id", (args) => [
      "/bin/bash",
      "-c",
      `echo '${args.hash}' | hash-identifier`,
    ]),
  });

  // cewl_generate - Custom wordlist generator from website
  tools.set("cewl_generate", {
    name: "cewl_generate",
    description: "Generate custom wordlist by spidering a website.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "Target URL to spider" },
        depth: { type: "number", description: "Spider depth (default: 2)" },
        min_word_length: {
          type: "number",
          description: "Minimum word length (default: 3)",
        },
        output: { type: "string", description: "Output file path" },
        with_numbers: {
          type: "boolean",
          description: "Include words with numbers",
        },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["cewl", args.url as string];

        if (args.depth) cmd.push("-d", String(args.depth));
        if (args.min_word_length) cmd.push("-m", String(args.min_word_length));
        if (args.output) cmd.push("-w", args.output as string);
        if (args.with_numbers) cmd.push("--with-numbers");

        return cmd;
      },
      600000
    ),
  });

  // crunch_generate - Pattern-based wordlist generator
  tools.set("crunch_generate", {
    name: "crunch_generate",
    description: "Generate wordlists based on patterns and character sets.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        min_length: {
          type: "number",
          description: "Minimum word length",
        },
        max_length: {
          type: "number",
          description: "Maximum word length",
        },
        charset: {
          type: "string",
          description: "Character set to use (e.g., 'abc123' or preset like 'lalpha')",
        },
        pattern: {
          type: "string",
          description: "Pattern with placeholders (@ = lowercase, , = uppercase, % = numbers, ^ = symbols)",
        },
        output: { type: "string", description: "Output file path" },
      },
      required: ["instance_id", "min_length", "max_length"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = [
          "crunch",
          String(args.min_length),
          String(args.max_length),
        ];

        if (args.charset) cmd.push(args.charset as string);
        if (args.pattern) cmd.push("-t", args.pattern as string);
        if (args.output) cmd.push("-o", args.output as string);

        return cmd;
      },
      600000
    ),
  });
}
