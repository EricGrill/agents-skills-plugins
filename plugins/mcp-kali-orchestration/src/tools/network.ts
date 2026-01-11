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

export function registerNetworkTools(
  backend: Backend,
  tools: Map<string, ToolDefinition>
): void {
  // netcat_connect - Network utility
  tools.set("netcat_connect", {
    name: "netcat_connect",
    description: "Connect to a host:port using netcat. Can send data or create listeners.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        host: { type: "string", description: "Target host (for connect mode)" },
        port: { type: "number", description: "Port number" },
        listen: {
          type: "boolean",
          description: "Listen mode instead of connect",
        },
        data: { type: "string", description: "Data to send" },
        udp: { type: "boolean", description: "Use UDP instead of TCP" },
        timeout: {
          type: "number",
          description: "Timeout in seconds (default: 30)",
        },
      },
      required: ["instance_id", "port"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["nc"];
        if (args.listen) {
          cmd.push("-l");
        }
        if (args.udp) cmd.push("-u");
        const timeout = (args.timeout as number) || 30;
        cmd.push("-w", String(timeout));

        if (!args.listen && args.host) {
          cmd.push(args.host as string);
        }
        cmd.push(String(args.port));

        // If sending data, we need to use echo
        if (args.data) {
          return ["/bin/bash", "-c", `echo '${args.data}' | ${cmd.join(" ")}`];
        }

        return cmd;
      },
      60000
    ),
  });

  // tcpdump_capture - Packet capture
  tools.set("tcpdump_capture", {
    name: "tcpdump_capture",
    description: "Capture network packets. Limited duration for safety.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        interface: {
          type: "string",
          description: "Network interface (default: any)",
        },
        filter: {
          type: "string",
          description: "BPF filter (e.g., 'port 80', 'host 192.168.1.1')",
        },
        count: {
          type: "number",
          description: "Number of packets to capture (default: 100)",
        },
        output: {
          type: "string",
          description: "Output pcap file path",
        },
        verbose: { type: "boolean", description: "Verbose output" },
      },
      required: ["instance_id"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["tcpdump"];
        const iface = (args.interface as string) || "any";
        cmd.push("-i", iface);

        const count = (args.count as number) || 100;
        cmd.push("-c", String(count));

        if (args.output) cmd.push("-w", args.output as string);
        if (args.verbose) cmd.push("-v");
        if (args.filter) cmd.push(...(args.filter as string).split(/\s+/));

        return cmd;
      },
      120000
    ),
  });

  // wireshark_cli - tshark packet analysis
  tools.set("wireshark_cli", {
    name: "wireshark_cli",
    description: "Analyze packets using tshark (command-line Wireshark).",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        interface: { type: "string", description: "Capture interface" },
        read_file: { type: "string", description: "Read from pcap file" },
        filter: { type: "string", description: "Display filter" },
        count: { type: "number", description: "Number of packets" },
        fields: {
          type: "string",
          description: "Fields to extract (comma-separated)",
        },
      },
      required: ["instance_id"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["tshark"];

        if (args.read_file) {
          cmd.push("-r", args.read_file as string);
        } else if (args.interface) {
          cmd.push("-i", args.interface as string);
        }

        if (args.filter) cmd.push("-Y", args.filter as string);
        if (args.count) cmd.push("-c", String(args.count));
        if (args.fields) {
          cmd.push("-T", "fields");
          for (const field of (args.fields as string).split(",")) {
            cmd.push("-e", field.trim());
          }
        }

        return cmd;
      },
      120000
    ),
  });

  // responder_run - LLMNR/NBT-NS poisoner
  tools.set("responder_run", {
    name: "responder_run",
    description:
      "Run Responder to capture credentials via LLMNR/NBT-NS poisoning. Use in authorized environments only.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        interface: { type: "string", description: "Network interface" },
        analyze: {
          type: "boolean",
          description: "Analyze mode only (no poisoning)",
        },
        fingerprint: { type: "boolean", description: "Fingerprint hosts" },
        wpad: { type: "boolean", description: "Enable WPAD rogue proxy" },
        duration_seconds: {
          type: "number",
          description: "Duration to run (default: 60 seconds)",
        },
      },
      required: ["instance_id", "interface"],
    },
    handler: async (args) => {
      const instanceId = args.instance_id as string;
      const duration = (args.duration_seconds as number) || 60;

      const cmd = ["responder", "-I", args.interface as string];
      if (args.analyze) cmd.push("-A");
      if (args.fingerprint) cmd.push("-f");
      if (args.wpad) cmd.push("-w");

      // Run responder for limited time
      const timeoutCmd = ["timeout", String(duration), ...cmd];

      const result = await backend.execCommand(instanceId, timeoutCmd, {
        user: "root",
        timeoutMs: (duration + 10) * 1000,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: true,
                message: `Responder ran for ${duration} seconds`,
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

  // bettercap_run - Network attacks framework
  tools.set("bettercap_run", {
    name: "bettercap_run",
    description:
      "Run bettercap for network attacks (ARP spoofing, sniffing, etc.).",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        interface: { type: "string", description: "Network interface" },
        caplet: { type: "string", description: "Caplet file to run" },
        eval: {
          type: "string",
          description: "Commands to evaluate (semicolon-separated)",
        },
        silent: { type: "boolean", description: "Suppress banner" },
      },
      required: ["instance_id"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = ["bettercap"];
        if (args.interface) cmd.push("-iface", args.interface as string);
        if (args.caplet) cmd.push("-caplet", args.caplet as string);
        if (args.eval) cmd.push("-eval", args.eval as string);
        if (args.silent) cmd.push("-silent");
        return cmd;
      },
      600000
    ),
  });

  // socat_relay - Advanced network relay
  tools.set("socat_relay", {
    name: "socat_relay",
    description: "Create network relays and tunnels using socat.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        source: {
          type: "string",
          description: "Source address (e.g., TCP-LISTEN:8080,fork)",
        },
        destination: {
          type: "string",
          description: "Destination address (e.g., TCP:target:80)",
        },
      },
      required: ["instance_id", "source", "destination"],
    },
    handler: createToolRunner(backend, "instance_id", (args) => [
      "socat",
      args.source as string,
      args.destination as string,
    ]),
  });

  // Wireless tools (may not work in containers without special setup)
  tools.set("aircrack_crack", {
    name: "aircrack_crack",
    description:
      "Crack WPA/WPA2 handshakes. Requires capture file from airodump-ng.",
    inputSchema: {
      type: "object",
      properties: {
        instance_id: { type: "string", description: "Kali instance ID" },
        capture_file: { type: "string", description: "Path to .cap file" },
        wordlist: { type: "string", description: "Path to wordlist" },
        bssid: { type: "string", description: "Target BSSID (optional)" },
      },
      required: ["instance_id", "capture_file", "wordlist"],
    },
    handler: createToolRunner(
      backend,
      "instance_id",
      (args) => {
        const cmd = [
          "aircrack-ng",
          "-w",
          args.wordlist as string,
          args.capture_file as string,
        ];
        if (args.bssid) cmd.push("-b", args.bssid as string);
        return cmd;
      },
      3600000
    ),
  });
}
