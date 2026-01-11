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

export function registerWebTools(
  backend: Backend,
  tools: Map<string, ToolDefinition>
): void {
  // nikto_scan - Web server scanner
  tools.set("nikto_scan", {
    name: "nikto_scan",
    description: "Scan web server for vulnerabilities using Nikto.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        target: { type: "string", description: "Target URL or IP" },
        port: { type: "number", description: "Port (default: 80)" },
        tuning: {
          type: "string",
          description: "Nikto tuning options (e.g., '1234' for specific tests)",
        },
        ssl: { type: "boolean", description: "Use SSL" },
      },
      required: ["instance_id", "target"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["nikto", "-h", args.target as string];
        if (args.port) cmd.push("-p", String(args.port));
        if (args.tuning) cmd.push("-Tuning", args.tuning as string);
        if (args.ssl) cmd.push("-ssl");
        return cmd;
      },
      600000
    ),
  });

  // dirb_scan - Directory brute-forcing
  tools.set("dirb_scan", {
    name: "dirb_scan",
    description: "Brute-force directories and files on web server.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "Target URL" },
        wordlist: {
          type: "string",
          description: "Wordlist path (default: /usr/share/dirb/wordlists/common.txt)",
        },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const wordlist =
          (args.wordlist as string) || "/usr/share/dirb/wordlists/common.txt";
        return ["dirb", args.url as string, wordlist];
      },
      600000
    ),
  });

  // gobuster_dir - Directory enumeration
  tools.set("gobuster_dir", {
    name: "gobuster_dir",
    description: "Directory/file enumeration using gobuster.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "Target URL" },
        wordlist: {
          type: "string",
          description: "Wordlist path (default: /usr/share/wordlists/dirb/common.txt)",
        },
        extensions: {
          type: "string",
          description: "File extensions to search for (e.g., 'php,html,txt')",
        },
        threads: { type: "number", description: "Number of threads (default: 10)" },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = [
          "gobuster",
          "dir",
          "-u",
          args.url as string,
          "-w",
          (args.wordlist as string) || "/usr/share/wordlists/dirb/common.txt",
        ];
        if (args.extensions) cmd.push("-x", args.extensions as string);
        if (args.threads) cmd.push("-t", String(args.threads));
        return cmd;
      },
      600000
    ),
  });

  // gobuster_dns - DNS subdomain brute-forcing
  tools.set("gobuster_dns", {
    name: "gobuster_dns",
    description: "DNS subdomain enumeration using gobuster.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Target domain" },
        wordlist: {
          type: "string",
          description: "Wordlist path",
        },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = [
          "gobuster",
          "dns",
          "-d",
          args.domain as string,
          "-w",
          (args.wordlist as string) ||
            "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt",
        ];
        return cmd;
      },
      600000
    ),
  });

  // ffuf_fuzz - Fast web fuzzer
  tools.set("ffuf_fuzz", {
    name: "ffuf_fuzz",
    description: "Fast web fuzzer for directories, parameters, etc.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: {
          type: "string",
          description: "Target URL with FUZZ keyword (e.g., http://target/FUZZ)",
        },
        wordlist: { type: "string", description: "Wordlist path" },
        filter_code: {
          type: "string",
          description: "Filter out responses by status code (e.g., '404,403')",
        },
        filter_size: {
          type: "string",
          description: "Filter out responses by size",
        },
        threads: { type: "number", description: "Number of threads (default: 40)" },
      },
      required: ["instance_id", "url", "wordlist"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = [
          "ffuf",
          "-u",
          args.url as string,
          "-w",
          args.wordlist as string,
        ];
        if (args.filter_code) cmd.push("-fc", args.filter_code as string);
        if (args.filter_size) cmd.push("-fs", args.filter_size as string);
        if (args.threads) cmd.push("-t", String(args.threads));
        return cmd;
      },
      600000
    ),
  });

  // sqlmap_scan - SQL injection
  tools.set("sqlmap_scan", {
    name: "sqlmap_scan",
    description: "Automatic SQL injection detection and exploitation.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: {
          type: "string",
          description: "Target URL with parameter (e.g., http://target/page?id=1)",
        },
        data: {
          type: "string",
          description: "POST data (e.g., 'username=test&password=test')",
        },
        level: {
          type: "number",
          description: "Level of tests (1-5, default: 1)",
        },
        risk: {
          type: "number",
          description: "Risk of tests (1-3, default: 1)",
        },
        dbs: { type: "boolean", description: "Enumerate databases" },
        tables: { type: "boolean", description: "Enumerate tables" },
        dump: { type: "boolean", description: "Dump data" },
        batch: {
          type: "boolean",
          description: "Non-interactive mode (default: true)",
        },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["sqlmap", "-u", args.url as string];
        if (args.data) cmd.push("--data", args.data as string);
        if (args.level) cmd.push("--level", String(args.level));
        if (args.risk) cmd.push("--risk", String(args.risk));
        if (args.dbs) cmd.push("--dbs");
        if (args.tables) cmd.push("--tables");
        if (args.dump) cmd.push("--dump");
        if (args.batch !== false) cmd.push("--batch");
        return cmd;
      },
      900000 // 15 min
    ),
  });

  // wpscan_scan - WordPress scanner
  tools.set("wpscan_scan", {
    name: "wpscan_scan",
    description: "WordPress vulnerability scanner.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "WordPress site URL" },
        api_token: {
          type: "string",
          description: "WPScan API token for vulnerability data",
        },
        enumerate: {
          type: "string",
          description: "Enumerate: u (users), p (plugins), t (themes), vp (vulnerable plugins)",
        },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["wpscan", "--url", args.url as string];
        if (args.api_token) cmd.push("--api-token", args.api_token as string);
        if (args.enumerate) cmd.push("-e", args.enumerate as string);
        return cmd;
      },
      600000
    ),
  });

  // whatweb_scan - Technology fingerprinting
  tools.set("whatweb_scan", {
    name: "whatweb_scan",
    description: "Identify technologies used by a website.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "Target URL" },
        aggression: {
          type: "number",
          description: "Aggression level (1-4, default: 1)",
        },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(backend, "instance_id", (args) => {
      const cmd = ["whatweb"];
      if (args.aggression) cmd.push("-a", String(args.aggression));
      cmd.push(args.url as string);
      return cmd;
    }),
  });

  // wafw00f_detect - WAF detection
  tools.set("wafw00f_detect", {
    name: "wafw00f_detect",
    description: "Detect Web Application Firewalls.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "Target URL" },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(backend, "instance_id", (args) => [
      "wafw00f",
      args.url as string,
    ]),
  });

  // nuclei_scan - Template-based scanner
  tools.set("nuclei_scan", {
    name: "nuclei_scan",
    description:
      "Fast vulnerability scanner using community templates.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        target: { type: "string", description: "Target URL" },
        templates: {
          type: "string",
          description: "Template tags to use (e.g., 'cve,sqli')",
        },
        severity: {
          type: "string",
          description: "Filter by severity (e.g., 'critical,high')",
        },
      },
      required: ["instance_id", "target"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["nuclei", "-u", args.target as string];
        if (args.templates) cmd.push("-tags", args.templates as string);
        if (args.severity) cmd.push("-severity", args.severity as string);
        return cmd;
      },
      900000
    ),
  });

  // xsser_scan - XSS scanner
  tools.set("xsser_scan", {
    name: "xsser_scan",
    description: "Cross-site scripting (XSS) vulnerability scanner.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: {
          type: "string",
          description: "Target URL with XSS parameter marker",
        },
        auto: { type: "boolean", description: "Automatic mode" },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["xsser", "-u", args.url as string];
        if (args.auto) cmd.push("--auto");
        return cmd;
      },
      600000
    ),
  });

  // commix_scan - Command injection
  tools.set("commix_scan", {
    name: "commix_scan",
    description: "Automated command injection exploitation tool.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        url: { type: "string", description: "Target URL" },
        data: { type: "string", description: "POST data" },
        batch: { type: "boolean", description: "Non-interactive mode" },
      },
      required: ["instance_id", "url"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["commix", "-u", args.url as string];
        if (args.data) cmd.push("--data", args.data as string);
        if (args.batch) cmd.push("--batch");
        return cmd;
      },
      600000
    ),
  });
}
