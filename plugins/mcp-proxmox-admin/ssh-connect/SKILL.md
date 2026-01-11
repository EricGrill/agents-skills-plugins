# SSH Connect Skill

SSH into remote machines using credentials from `.env` file - no password prompts.

## Setup

1. Create `.env` file in project root with your SSH credentials:

```bash
# Required
SSH_HOST=192.168.1.100
SSH_USER=ubuntu

# Authentication (choose one)
SSH_KEY_PATH=~/.ssh/id_rsa          # Recommended: path to private key
SSH_PASSWORD=your_password           # Alternative: password auth
```

2. Ensure Python dependencies are installed:
```bash
pip install paramiko python-dotenv
```

## Usage

### CLI
```bash
# Interactive shell
python .claude/skills/ssh-connect/ssh_connect.py

# Run single command
python .claude/skills/ssh-connect/ssh_connect.py "ls -la"

# Run multiple commands
python .claude/skills/ssh-connect/ssh_connect.py "cd /app && git pull && docker-compose restart"
```

### Python API
```python
from ssh_connect import SSHClient

# Auto-loads from .env
with SSHClient() as ssh:
    output = ssh.run("hostname")
    print(output)

# Or specify credentials directly
with SSHClient(host="192.168.1.100", user="ubuntu", key_path="~/.ssh/id_rsa") as ssh:
    output = ssh.run("uptime")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SSH_HOST` | Yes | Remote hostname or IP |
| `SSH_USER` | Yes | SSH username |
| `SSH_PORT` | No | SSH port (default: 22) |
| `SSH_KEY_PATH` | No* | Path to SSH private key |
| `SSH_PASSWORD` | No* | SSH password |

*One of `SSH_KEY_PATH` or `SSH_PASSWORD` is required.

## Security Notes

- **Prefer SSH keys** over passwords when possible
- Add `.env` to `.gitignore` to prevent credential leaks
- Never commit credentials to version control
