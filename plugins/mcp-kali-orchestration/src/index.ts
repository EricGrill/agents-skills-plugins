#!/usr/bin/env node

import { McpKaliServer } from "./server.js";

const server = new McpKaliServer();
server.run().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
