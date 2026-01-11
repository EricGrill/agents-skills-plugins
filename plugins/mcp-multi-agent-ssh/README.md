<p align="center">
  <h1 align="center">MCP Multi-Agent SSH</h1>
  <p align="center">
    <strong>Stateful SSH connections for Claude Code via MCP</strong>
  </p>
  <p align="center">
    <a href="https://github.com/EricGrill/mcp-multi-agent-ssh/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/tools-10-purple.svg" alt="10 Tools">
    <img src="https://img.shields.io/badge/MCP-compatible-orange.svg" alt="MCP Compatible">
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> |
    <a href="#-tools">Tools</a> |
    <a href="#-examples">Examples</a> |
    <a href="#-security">Security</a>
  </p>
</p>

---

## What is this?

An MCP server that gives Claude Code persistent SSH connections. Instead of opening and closing connections for every command, connections stay alive for 10 minutes—making remote server management fast and seamless.

**Part of the [Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins)** — discover more plugins, agents, and skills for Claude Code.

---

## Quick Start

### Using NPX

```bash
npx mcp-multi-agent-ssh
```

### Using Docker

```bash
docker run -it --rm \
  -v ~/.mcp-multi-agent-ssh:/root/.mcp-multi-agent-ssh \
  -e MCP_SSH_MASTER_PASSWORD=your-password \
  mcp-multi-agent-ssh
```

---

## Claude Code Setup

Add to your Claude Code MCP configuration:

**NPX Method:**

```json
{
  "mcpServers": {
    "ssh": {
      "command": "npx",
      "args": ["mcp-multi-agent-ssh"],
      "env": {
        "MCP_SSH_MASTER_PASSWORD": "your-master-password"
      }
    }
  }
}
```

**Docker Method:**

```json
{
  "mcpServers": {
    "ssh": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "~/.mcp-multi-agent-ssh:/root/.mcp-multi-agent-ssh",
        "-e", "MCP_SSH_MASTER_PASSWORD",
        "mcp-multi-agent-ssh"
      ],
      "env": {
        "MCP_SSH_MASTER_PASSWORD": "your-master-password"
      }
    }
  }
}
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Persistent Connections** | SSH connections stay open for 10 minutes of inactivity |
| **Encrypted Credentials** | Per-host credentials stored with AES-256-GCM encryption |
| **Auto-Reconnect** | Transparently reconnects when connections expire or drop |
| **SFTP Support** | Upload, download, and list files on remote servers |
| **Host-Based Auth** | Credentials automatically matched by hostname |

---

## Tools

### Connection Management

| Tool | Description |
|------|-------------|
| `ssh_connect` | Connect to an SSH server. Stores credentials for future use. |
| `ssh_disconnect` | Close connection to a specific host. |
| `ssh_list_connections` | List all active connections with idle time. |

### Command Execution

| Tool | Description |
|------|-------------|
| `ssh_exec` | Run a command on a remote server. Auto-connects if needed. |

### File Operations (SFTP)

| Tool | Description |
|------|-------------|
| `sftp_upload` | Upload a local file to a remote server. |
| `sftp_download` | Download a file from a remote server. |
| `sftp_list` | List files in a remote directory. |

### Credential Management

| Tool | Description |
|------|-------------|
| `ssh_list_credentials` | List hosts with stored credentials. |
| `ssh_delete_credentials` | Remove stored credentials for a host. |

---

## Examples

### Connect and Run Commands

```
User: Connect to my server at example.com as user "deploy" with password "secret123"

Claude: [calls ssh_connect]
Connected! Credentials saved for future use.

User: What's the disk usage?

Claude: [calls ssh_exec with command="df -h"]
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       100G   45G   55G  45% /
```

### Transfer Files

```
User: Upload my config file to the server

Claude: [calls sftp_upload]
Uploaded 2.3 KB to /etc/app/config.yml
```

### Auto-Reconnect

After 10 minutes of inactivity, connections automatically close with a notification. The next command reconnects using stored credentials:

```
[mcp-multi-agent-ssh] Connection to example.com:22 expired after 10 minutes of inactivity

User: Check the server status

Claude: [calls ssh_exec — automatically reconnects]
● app.service - My Application
   Active: active (running)
```

---

## Security

### Credential Storage

| Aspect | Implementation |
|--------|----------------|
| **Location** | `~/.mcp-multi-agent-ssh/credentials.enc` |
| **Encryption** | AES-256-GCM |
| **Key Derivation** | PBKDF2 with 100,000 iterations |
| **File Permissions** | 600 (owner read/write only) |

### Master Password

The master password encrypts/decrypts stored credentials:

1. **Environment Variable** (recommended):
   ```bash
   export MCP_SSH_MASTER_PASSWORD="your-password"
   ```

2. **Interactive Prompt**: If not set, you'll be prompted on first run.

---

## Development

### Prerequisites

- Python 3.10+
- Node.js 18+ (for NPX launcher)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/ericgrill/mcp-multi-agent-ssh.git
cd mcp-multi-agent-ssh

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
mcp-multi-agent-ssh/
├── src/mcp_multi_agent_ssh/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point
│   ├── connection_pool.py # SSH connection management
│   ├── credentials.py     # Encrypted credential storage
│   └── types.py           # Pydantic models
├── bin/
│   └── launcher.js        # NPX launcher script
├── tests/
├── Dockerfile
├── docker-compose.yml
├── package.json
├── pyproject.toml
└── README.md
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Master password required"** | Set `MCP_SSH_MASTER_PASSWORD` environment variable |
| **"Python 3.10+ not found"** | Install Python 3.10+ from https://www.python.org/ |
| **Connection timeouts** | Check network, verify port (default: 22), check firewall |
| **"Failed to decrypt credentials"** | Wrong password. Delete `~/.mcp-multi-agent-ssh/credentials.enc` and `salt` to reset |

---

## Related

**[Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins)** — Discover 40+ plugins, 70+ agents, and 110+ skills for Claude Code including:

- **superpowers** — TDD, debugging, code review skills
- **python-development** — Django, FastAPI, async Python
- **llm-application-dev** — RAG, embeddings, LangChain

---

## License

MIT
