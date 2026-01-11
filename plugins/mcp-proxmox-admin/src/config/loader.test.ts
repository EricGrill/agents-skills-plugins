// src/config/loader.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { loadConfig } from "./loader.js";

describe("loadConfig", () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it("loads config from environment variables", () => {
    process.env.PROXMOX_HOST = "10.0.0.1";
    process.env.PROXMOX_PORT = "8007";
    process.env.PROXMOX_SSH_USER = "admin";

    const config = loadConfig({});
    expect(config.host).toBe("10.0.0.1");
    expect(config.port).toBe(8007);
    expect(config.sshUser).toBe("admin");
  });

  it("MCP settings override environment variables", () => {
    process.env.PROXMOX_HOST = "10.0.0.1";

    const config = loadConfig({ host: "192.168.1.1" });
    expect(config.host).toBe("192.168.1.1");
  });

  it("throws error when host is missing", () => {
    expect(() => loadConfig({})).toThrow();
  });

  it("parses boolean env vars correctly", () => {
    process.env.PROXMOX_HOST = "10.0.0.1";
    process.env.PROXMOX_VERIFY_SSL = "false";
    process.env.PROXMOX_SAFE_MODE = "true";

    const config = loadConfig({});
    expect(config.verifySsl).toBe(false);
    expect(config.safeMode).toBe(true);
  });
});
