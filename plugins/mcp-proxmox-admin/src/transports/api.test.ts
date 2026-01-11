// src/transports/api.test.ts
import { describe, it, expect, vi, beforeEach } from "vitest";
import { APITransport } from "./api.js";
import type { Config } from "../config/index.js";

vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    })),
  },
}));

describe("APITransport", () => {
  const baseConfig: Config = {
    host: "192.168.1.100",
    port: 8006,
    apiTokenId: "user@pam!token",
    apiTokenSecret: "secret-uuid",
    verifySsl: true,
    defaultTransport: "api",
    timeout: 30000,
    safeMode: false,
  };

  it("creates instance with config", () => {
    const transport = new APITransport(baseConfig);
    expect(transport).toBeInstanceOf(APITransport);
  });

  it("builds correct base URL", () => {
    const transport = new APITransport(baseConfig);
    expect(transport.getBaseUrl()).toBe("https://192.168.1.100:8006/api2/json");
  });

  it("builds correct auth header", () => {
    const transport = new APITransport(baseConfig);
    const header = transport.getAuthHeader();
    expect(header).toBe("PVEAPIToken=user@pam!token=secret-uuid");
  });

  it("throws error for executeCommand", async () => {
    const transport = new APITransport(baseConfig);
    await expect(transport.executeCommand("test")).rejects.toThrow(
      "API transport does not support direct command execution"
    );
  });

  it("uses custom port in base URL", () => {
    const configWithPort: Config = { ...baseConfig, port: 443 };
    const transport = new APITransport(configWithPort);
    expect(transport.getBaseUrl()).toBe("https://192.168.1.100:443/api2/json");
  });
});
