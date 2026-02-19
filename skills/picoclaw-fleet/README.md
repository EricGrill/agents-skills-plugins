<p align="center">
  <h1 align="center">🐦 picoclaw-fleet</h1>
  <p align="center"><strong>Deploy and orchestrate PicoClaw workers from OpenClaw over SSH.</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/language-bash-1f425f.svg" alt="Language: Bash" />
    <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS-blue" alt="Platform: Linux/Mac" />
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT" />
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-fleet-config">Fleet Config</a> •
    <a href="#-features">Features</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-about">About</a>
  </p>
</p>

---

## 🚀 Quick Start

```bash
cd skills/picoclaw-fleet
chmod +x scripts/*.sh

# 1) Check fleet status
./scripts/fleet-status.sh

# 2) Deploy PicoClaw to a host
ANTHROPIC_API_KEY=... ./scripts/deploy.sh 192.168.50.57 eric arm64 ~/.ssh/id_rsa

# 3) Run one-shot task
./scripts/dispatch.sh 192.168.50.57 eric "Summarize the last 24h syslog events" 120
```

---

## 🐦 Fleet Config

Config file path:

`~/.openclaw/workspace/config/picoclaw-fleet.json`

Example:

```json
{
  "hosts": [
    {
      "name": "darth",
      "host": "192.168.50.57",
      "user": "eric",
      "arch": "arm64",
      "ssh_key": "~/.ssh/id_rsa"
    }
  ],
  "defaults": {
    "provider": "anthropic",
    "api_key_env": "ANTHROPIC_API_KEY"
  }
}
```

---

## ✨ Features

| Feature | What it does |
|---|---|
| Fleet health checks | Reports host reachability + PicoClaw install state |
| Zero-to-ready deploy | Pulls latest PicoClaw binary from GitHub releases by arch |
| One-shot execution | Runs `picoclaw agent -m "task"` remotely and returns stdout |
| Parallel fanout | Dispatches multiple tasks to multiple hosts concurrently |
| Ephemeral teardown | Optionally removes PicoClaw after task completion |

---

## 🧰 Included Scripts

- `scripts/deploy.sh`
  - Usage: `deploy.sh <host> <user> <arch> [ssh_key]`
  - Installs PicoClaw, writes `~/.picoclaw/.env`, runs `picoclaw onboard`

- `scripts/dispatch.sh`
  - Usage: `dispatch.sh <host> <user> <task> [timeout_seconds]`
  - Runs one-shot task with timeout and prints output

- `scripts/fleet-status.sh`
  - Usage: `fleet-status.sh [config_path]`
  - Reads fleet config and reports status table

---

## 🧠 OpenClaw Skill Behavior

The companion `SKILL.md` guides OpenClaw to:

1. Always read/create fleet config first
2. Deploy missing/invalid hosts before dispatch
3. Select least-loaded (or first available) host for single-task runs
4. Use parallel SSH for multi-host execution
5. Return outputs inline with graceful SSH/timeout error handling

---

## 🏗️ Architecture

```text
                +------------------------------+
                |         OpenClaw Skill       |
                |      (skills/picoclaw-fleet) |
                +---------------+--------------+
                                |
          +---------------------+----------------------+
          |                                            |
+---------v----------+                      +----------v---------+
| scripts/deploy.sh  |                      | scripts/dispatch.sh|
| install + onboard  |                      | one-shot execution |
+---------+----------+                      +----------+---------+
          |                                            |
          +---------------------+----------------------+
                                |
                     +----------v-------------------+
                     |   Remote Fleet SSH Hosts     |
                     |  (~/.local/bin/picoclaw)     |
                     +-------------------------------+
```

---

## 🧪 Parallel Example

```bash
./scripts/dispatch.sh 192.168.50.57 eric "Analyze host A logs" 120 > /tmp/a.out 2>&1 &
./scripts/dispatch.sh 192.168.50.58 eric "Analyze host B logs" 120 > /tmp/b.out 2>&1 &
wait

echo "=== Host A ==="; cat /tmp/a.out
echo "=== Host B ==="; cat /tmp/b.out
```

---

## 🧹 Optional Teardown

```bash
ssh eric@192.168.50.57 'rm -f ~/.local/bin/picoclaw ~/.picoclaw/.env'
```

---

## 🌐 About

Built for the OpenClaw ecosystem by [Eric Grill](https://ericgrill.com).

- GitHub: [github.com/EricGrill](https://github.com/EricGrill)
- Repo: [EricGrill/agents-skills-plugins](https://github.com/EricGrill/agents-skills-plugins)
