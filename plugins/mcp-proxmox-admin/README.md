<p align="center">
  <h1 align="center">MCP Proxmox Admin</h1>
  <p align="center">
    <strong>Manage Proxmox VE infrastructure through Claude</strong>
  </p>
  <p align="center">
    <a href="https://github.com/EricGrill/mcp-proxmox-admin/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/tools-16-green.svg" alt="16 Tools">
    <img src="https://img.shields.io/badge/transport-SSH%20%2B%20API-purple.svg" alt="SSH + API">
    <img src="https://img.shields.io/badge/node-%3E%3D18-orange.svg" alt="Node >= 18">
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> |
    <a href="#-available-tools">Tools</a> |
    <a href="#%EF%B8%8F-configuration">Configuration</a> |
    <a href="#-contributing">Contributing</a>
  </p>
</p>

---

## What is this?

An MCP (Model Context Protocol) server that enables Claude to manage your Proxmox VE infrastructure. Control VMs, containers, snapshots, and monitor cluster health through natural language.

**Works with Claude Desktop, Cursor, and any MCP-compatible client.**

---

## Quick Start

```bash
# Install globally
npm install -g mcp-proxmox-admin

# Or run directly with npx
npx mcp-proxmox-admin
```

Add to your Claude Desktop config and start managing your Proxmox cluster:

> "Show me all running VMs on my Proxmox cluster"

---

## Why Use This?

| Feature | Description |
|---------|-------------|
| **Full VM Control** | Start, stop, shutdown, restart virtual machines |
| **Container Management** | Manage LXC containers with the same ease |
| **Snapshot Operations** | Create, restore, and delete snapshots |
| **Hybrid Transport** | Auto-selects SSH or REST API based on operation |
| **Safe Mode** | Optional read-only mode for monitoring |

---

## Available Tools

### Virtual Machines

| Tool | Description |
|------|-------------|
| `proxmox_vm_list` | List all VMs across nodes |
| `proxmox_vm_start` | Start a VM |
| `proxmox_vm_stop` | Stop a VM immediately |
| `proxmox_vm_shutdown` | Graceful ACPI shutdown |
| `proxmox_vm_restart` | Restart a VM |

### Containers

| Tool | Description |
|------|-------------|
| `proxmox_ct_list` | List all LXC containers |
| `proxmox_ct_start` | Start a container |
| `proxmox_ct_stop` | Stop a container |
| `proxmox_ct_restart` | Restart a container |

### Infrastructure

| Tool | Description |
|------|-------------|
| `proxmox_node_list` | List cluster nodes |
| `proxmox_node_status` | Get node CPU, memory, disk |
| `proxmox_storage_list` | List storage pools |

### Snapshots

| Tool | Description |
|------|-------------|
| `proxmox_snapshot_list` | List snapshots for VM/container |
| `proxmox_snapshot_create` | Create a new snapshot |
| `proxmox_snapshot_restore` | Restore to a snapshot |
| `proxmox_snapshot_delete` | Delete a snapshot (requires confirm) |

---

## Configuration

### Claude Desktop Setup

Add to your Claude Desktop config:

| Platform | Config Path |
|----------|-------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "npx",
      "args": ["mcp-proxmox-admin"],
      "env": {
        "PROXMOX_HOST": "192.168.1.100",
        "PROXMOX_API_TOKEN_ID": "user@pam!mytoken",
        "PROXMOX_API_TOKEN_SECRET": "your-secret-here",
        "PROXMOX_SSH_USER": "root",
        "PROXMOX_SSH_KEY_PATH": "~/.ssh/id_rsa"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROXMOX_HOST` | Proxmox host/IP | *required* |
| `PROXMOX_PORT` | API port | `8006` |
| `PROXMOX_API_TOKEN_ID` | API token (format: `user@realm!tokenid`) | |
| `PROXMOX_API_TOKEN_SECRET` | API token secret | |
| `PROXMOX_VERIFY_SSL` | Verify SSL certificates | `true` |
| `PROXMOX_SSH_USER` | SSH username | |
| `PROXMOX_SSH_PORT` | SSH port | `22` |
| `PROXMOX_SSH_KEY_PATH` | Path to SSH private key | |
| `PROXMOX_SSH_PASSWORD` | SSH password (alternative to key) | |
| `PROXMOX_DEFAULT_TRANSPORT` | `ssh`, `api`, or `auto` | `auto` |
| `PROXMOX_DEFAULT_NODE` | Default node name | |
| `PROXMOX_TIMEOUT` | Request timeout (ms) | `30000` |
| `PROXMOX_SAFE_MODE` | Disable destructive operations | `false` |

### Config Priority

1. **MCP client settings** (highest priority)
2. **Environment variables**
3. **proxmox-config.json file** (lowest priority)

---

## Transport Modes

| Mode | Description |
|------|-------------|
| `auto` | Best transport per operation (recommended) |
| `api` | REST API only |
| `ssh` | SSH commands only |

In `auto` mode: API for reads, SSH for snapshots and config changes.

---

## Examples

<details>
<summary><b>VM Management</b></summary>

```
"Show me all running VMs"
"Start VM 100 on node pve"
"Gracefully shutdown VM 101"
"Stop VM 102 immediately"
```

</details>

<details>
<summary><b>Container Management</b></summary>

```
"List all LXC containers"
"Start container 200"
"Restart container 201"
```

</details>

<details>
<summary><b>Snapshots</b></summary>

```
"Create a snapshot of VM 100 named 'before-upgrade'"
"List snapshots for VM 100"
"Restore VM 100 to snapshot 'before-upgrade'"
"Delete snapshot 'old-backup' from VM 100"
```

</details>

<details>
<summary><b>Cluster Monitoring</b></summary>

```
"What's the status of node pve?"
"Show me CPU and memory usage for all nodes"
"List all storage pools and available space"
```

</details>

---

## Authentication

### API Token (Recommended)

1. Proxmox UI → Datacenter → Permissions → API Tokens
2. Create token for your user
3. Assign `PVEVMAdmin` role for full VM control
4. Add token ID and secret to config

### SSH Key

```bash
# Generate key if needed
ssh-keygen -t ed25519

# Copy to Proxmox
ssh-copy-id root@proxmox-host
```

---

## Safe Mode

Enable for read-only monitoring:

```bash
PROXMOX_SAFE_MODE=true
```

Disables: snapshot deletion and other destructive operations.

---

## Development

```bash
# Clone
git clone https://github.com/EricGrill/mcp-proxmox-admin.git
cd mcp-proxmox-admin

# Install & build
npm install
npm run build

# Test
npm test

# Dev mode (watch)
npm run dev
```

---

## Troubleshooting

<details>
<summary><b>Cannot connect to Proxmox</b></summary>

1. Verify host and port
2. Check connectivity: `ping <proxmox-host>`
3. Test API: `curl -k https://<proxmox-host>:8006/api2/json`

</details>

<details>
<summary><b>Authentication failed</b></summary>

1. API token format: `user@realm!tokenid`
2. Verify token hasn't expired
3. SSH key permissions: `chmod 600 ~/.ssh/id_rsa`

</details>

<details>
<summary><b>Permission denied</b></summary>

Required Proxmox permissions:
- `VM.PowerMgmt` - start/stop/restart
- `VM.Snapshot` - snapshot operations
- `Sys.Audit` - node/storage info

</details>

<details>
<summary><b>SSL certificate errors</b></summary>

For self-signed certs:
- Set `PROXMOX_VERIFY_SSL=false` (dev only)
- Or add Proxmox CA to system trust store

</details>

---

## Contributing

Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `npm test`
4. Commit: `git commit -m 'Add my feature'`
5. Push: `git push origin feature/my-feature`
6. Open a Pull Request

---

## License

MIT
