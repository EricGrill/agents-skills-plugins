// src/transports/ssh.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { SSHTransport } from "./ssh.js";
import type { Config } from "../config/index.js";

// Mock ssh2
vi.mock("ssh2", () => {
  const mockExec = vi.fn();
  const mockConnect = vi.fn();
  const mockEnd = vi.fn();
  const mockOn = vi.fn();

  class MockClient {
    exec = mockExec;
    connect = mockConnect;
    end = mockEnd;
    on = mockOn;
  }

  return { Client: MockClient };
});

describe("SSHTransport", () => {
  const baseConfig: Config = {
    host: "192.168.1.100",
    port: 8006,
    sshUser: "root",
    sshPort: 22,
    sshKeyPath: "/home/user/.ssh/id_rsa",
    defaultTransport: "ssh",
    verifySsl: true,
    timeout: 30000,
    safeMode: false,
  };

  it("creates instance with config", () => {
    const transport = new SSHTransport(baseConfig);
    expect(transport).toBeInstanceOf(SSHTransport);
  });

  it("isConnected returns false initially", () => {
    const transport = new SSHTransport(baseConfig);
    expect(transport.isConnected()).toBe(false);
  });

  it("parseVMListOutput parses qm list output", () => {
    const transport = new SSHTransport(baseConfig);
    const output = `      VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID
       100 ubuntu-server        running    4096              32.00 12345
       101 windows-desktop      stopped    8192              64.00 0`;

    const result = transport.parseVMListOutput(output, "pve");
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      vmid: 100,
      name: "ubuntu-server",
      status: "running",
      node: "pve",
    });
    expect(result[1]).toMatchObject({
      vmid: 101,
      name: "windows-desktop",
      status: "stopped",
      node: "pve",
    });
  });

  it("parseContainerListOutput parses pct list output", () => {
    const transport = new SSHTransport(baseConfig);
    const output = `VMID       Status     Lock         Name
100        running                 ubuntu-container
101        stopped                 debian-container`;

    const result = transport.parseContainerListOutput(output, "pve");
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      vmid: 100,
      name: "ubuntu-container",
      status: "running",
      node: "pve",
    });
    expect(result[1]).toMatchObject({
      vmid: 101,
      name: "debian-container",
      status: "stopped",
      node: "pve",
    });
  });

  it("parseSnapshotListOutput parses snapshot list output", () => {
    const transport = new SSHTransport(baseConfig);
    const output = `[
  {"name": "snap1", "description": "First snapshot", "snaptime": 1700000000},
  {"name": "snap2", "description": "Second snapshot", "snaptime": 1700001000}
]`;

    const result = transport.parseSnapshotListOutput(output);
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({
      name: "snap1",
      description: "First snapshot",
      snaptime: 1700000000,
    });
  });

  it("handles empty VM list output", () => {
    const transport = new SSHTransport(baseConfig);
    const output = `      VMID NAME                 STATUS     MEM(MB)    BOOTDISK(GB) PID`;

    const result = transport.parseVMListOutput(output, "pve");
    expect(result).toHaveLength(0);
  });

  it("handles empty container list output", () => {
    const transport = new SSHTransport(baseConfig);
    const output = `VMID       Status     Lock         Name`;

    const result = transport.parseContainerListOutput(output, "pve");
    expect(result).toHaveLength(0);
  });
});
