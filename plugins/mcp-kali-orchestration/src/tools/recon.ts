import type { Backend } from "../backends/interface.js";
import type { ToolDefinition } from "../server.js";

// Helper to create a tool that runs a command in the Kali instance
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

export function registerReconTools(
  backend: Backend,
  tools: Map<string, ToolDefinition>
): void {
  // nmap_scan - Port scanning
  tools.set("nmap_scan", {
    name: "nmap_scan",
    description:
      "Run nmap port scan against a target. Returns scan results.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: {
          type: "string",
          description: "Kali instance ID to run the scan from",
        },
        target: {
          type: "string",
          description: "Target IP, hostname, or CIDR range",
        },
        ports: {
          type: "string",
          description: "Port specification (e.g., '22,80,443' or '1-1000')",
        },
        flags: {
          type: "string",
          description: "Additional nmap flags (e.g., '-sV -sC')",
        },
        output_format: {
          type: "string",
          enum: ["normal", "xml", "json"],
          description: "Output format (default: normal)",
        },
      },
      required: ["instance_id", "target"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["nmap"];
        if (args.ports) cmd.push("-p", args.ports as string);
        if (args.flags) cmd.push(...(args.flags as string).split(/\s+/));
        if (args.output_format === "xml") cmd.push("-oX", "-");
        cmd.push(args.target as string);
        return cmd;
      },
      600000 // 10 min timeout for scans
    ),
  });

  // nmap_vuln_scan - Vulnerability scanning
  tools.set("nmap_vuln_scan", {
    name: "nmap_vuln_scan",
    description:
      "Run nmap with vulnerability detection scripts.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: {
          type: "string",
          description: "Kali instance ID",
        },
        target: {
          type: "string",
          description: "Target IP or hostname",
        },
        scripts: {
          type: "string",
          description: "Script category or specific scripts (default: vuln)",
        },
      },
      required: ["instance_id", "target"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const scripts = (args.scripts as string) || "vuln";
        return ["nmap", "--script", scripts, "-sV", args.target as string];
      },
      900000 // 15 min timeout
    ),
  });

  // whois_lookup - Domain WHOIS
  tools.set("whois_lookup", {
    name: "whois_lookup",
    description: "Perform WHOIS lookup on a domain.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Domain to lookup" },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(backend, "instance_id", (args) => [
      "whois",
      args.domain as string,
    ]),
  });

  // dig_lookup - DNS queries
  tools.set("dig_lookup", {
    name: "dig_lookup",
    description: "Perform DNS lookup using dig.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Domain to query" },
        record_type: {
          type: "string",
          description: "Record type (A, AAAA, MX, NS, TXT, etc.)",
        },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(backend, "instance_id", (args) => {
      const cmd = ["dig"];
      if (args.record_type) cmd.push(args.record_type as string);
      cmd.push(args.domain as string);
      return cmd;
    }),
  });

  // dnsrecon_scan - DNS enumeration
  tools.set("dnsrecon_scan", {
    name: "dnsrecon_scan",
    description: "DNS reconnaissance and enumeration.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Domain to enumerate" },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => ["dnsrecon", "-d", args.domain as string],
      300000
    ),
  });

  // theharvester_search - Email and subdomain harvesting
  tools.set("theharvester_search", {
    name: "theharvester_search",
    description:
      "Gather emails, subdomains, hosts, and other info from public sources.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Target domain" },
        sources: {
          type: "string",
          description:
            "Data sources to use (e.g., 'google,bing,linkedin'). Default: all",
        },
        limit: {
          type: "number",
          description: "Limit number of results (default: 500)",
        },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["theHarvester", "-d", args.domain as string];
        if (args.sources) {
          cmd.push("-b", args.sources as string);
        } else {
          cmd.push("-b", "all");
        }
        if (args.limit) cmd.push("-l", String(args.limit));
        return cmd;
      },
      600000
    ),
  });

  // amass_enum - Subdomain enumeration
  tools.set("amass_enum", {
    name: "amass_enum",
    description: "Subdomain enumeration using OWASP Amass.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Target domain" },
        passive: {
          type: "boolean",
          description: "Passive mode only (no DNS resolution)",
        },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["amass", "enum", "-d", args.domain as string];
        if (args.passive) cmd.push("-passive");
        return cmd;
      },
      1800000 // 30 min - amass can take a while
    ),
  });

  // masscan_scan - High-speed port scanning
  tools.set("masscan_scan", {
    name: "masscan_scan",
    description:
      "High-speed port scanner. Use with caution - can be very noisy.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        target: {
          type: "string",
          description: "Target IP range (CIDR notation)",
        },
        ports: { type: "string", description: "Port range (e.g., '0-65535')" },
        rate: {
          type: "number",
          description: "Packets per second (default: 1000)",
        },
      },
      required: ["instance_id", "target", "ports"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const rate = (args.rate as number) || 1000;
        return [
          "masscan",
          args.target as string,
          "-p",
          args.ports as string,
          "--rate",
          String(rate),
        ];
      },
      600000
    ),
  });

  // sublist3r_scan - Subdomain enumeration
  tools.set("sublist3r_scan", {
    name: "sublist3r_scan",
    description: "Fast subdomains enumeration tool.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        domain: { type: "string", description: "Target domain" },
      },
      required: ["instance_id", "domain"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => ["sublist3r", "-d", args.domain as string],
      300000
    ),
  });
}
