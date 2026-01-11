// src/config/schema.test.ts
import { describe, it, expect } from "vitest";
import { configSchema, type Config } from "./schema.js";

describe("configSchema", () => {
  it("validates minimal config with host", () => {
    const config = { host: "192.168.1.100" };
    const result = configSchema.safeParse(config);
    expect(result.success).toBe(true);
  });

  it("applies default values", () => {
    const config = { host: "192.168.1.100" };
    const result = configSchema.parse(config);
    expect(result.port).toBe(8006);
    expect(result.sshPort).toBe(22);
    expect(result.defaultTransport).toBe("auto");
    expect(result.verifySsl).toBe(true);
    expect(result.timeout).toBe(30000);
  });

  it("rejects config without host", () => {
    const config = { port: 8006 };
    const result = configSchema.safeParse(config);
    expect(result.success).toBe(false);
  });

  it("validates transport enum", () => {
    const validTransports = ["ssh", "api", "auto"];
    for (const transport of validTransports) {
      const config = { host: "192.168.1.100", defaultTransport: transport };
      const result = configSchema.safeParse(config);
      expect(result.success).toBe(true);
    }
  });

  it("rejects invalid transport", () => {
    const config = { host: "192.168.1.100", defaultTransport: "invalid" };
    const result = configSchema.safeParse(config);
    expect(result.success).toBe(false);
  });
});
