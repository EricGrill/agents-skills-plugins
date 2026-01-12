#!/usr/bin/env node
import { DelegationServer } from './server.js';

const CALLBACK_PORT = parseInt(process.env.CALLBACK_PORT || '8765', 10);
const PROXMOX_ADMIN_PATH = process.env.PROXMOX_ADMIN_PATH || './node_modules/mcp-proxmox-admin/dist/index.js';

async function main() {
  const server = new DelegationServer({
    callbackPort: CALLBACK_PORT,
    proxmoxAdminPath: PROXMOX_ADMIN_PATH,
  });

  process.on('SIGINT', async () => {
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await server.stop();
    process.exit(0);
  });

  await server.start();
}

main().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
