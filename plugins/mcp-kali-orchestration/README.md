# MCP-Kali-Orchestration

**Orchestrate Kali Linux instances on-demand with 50+ security tools exposed via MCP**

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![50+ Tools](https://img.shields.io/badge/Tools-50%2B-blue.svg)](#-tool-catalog)
[![Docker](https://img.shields.io/badge/Backend-Docker-2496ED.svg)](https://www.docker.com/)
[![Proxmox](https://img.shields.io/badge/Backend-Proxmox-E57000.svg)](https://www.proxmox.com/)

[Quick Start](#-quick-start) | [Tool Catalog](#-tool-catalog) | [All Tools](#-all-tools) | [Configuration](#-configuration) | [Contributing](#-contributing)

---

## What is this?

An MCP (Model Context Protocol) server that spins up Kali Linux instances and exposes professional security tools directly to Claude Code or any MCP-compatible client. Run nmap scans, exploit vulnerabilities with Metasploit, crack passwords, and perform full penetration tests—all through natural language.

> Part of the [Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins) ecosystem.

---

## Quick Start

**1. Add the marketplace and install:**

```bash
claude mcp add-json mcp-kali-orchestration '{"command":"node","args":["/path/to/mcp-kali-orchestration/dist/index.js"]}'
```

**2. Build the Kali image and server:**

```bash
git clone https://github.com/EricGrill/mcp-kali-orchestration.git
cd mcp-kali-orchestration
npm install && npm run build
npm run build:image  # Builds Docker image with all tools
```

---

## Why Use MCP-Kali-Orchestration?

| Feature | Description |
|---------|-------------|
| **On-demand instances** | Spin up fresh Kali containers/VMs per engagement, tear down when done |
| **50+ tools exposed** | Reconnaissance, web testing, exploitation, passwords, post-exploitation, network |
| **Dual backend** | Docker (fast, local) or Proxmox (full VM isolation) |
| **Natural language** | "Scan example.com for vulnerabilities" → Claude handles the rest |

---

## Tool Catalog

| Category | Tools | Best For |
|----------|-------|----------|
| **Lifecycle** | 6 | Instance management (`kali_start`, `kali_stop`, `kali_exec`) |
| **Reconnaissance** | 9 | Network discovery, DNS enum, OSINT (`nmap`, `amass`, `theharvester`) |
| **Web Testing** | 12 | Web app security (`sqlmap`, `nikto`, `nuclei`, `gobuster`) |
| **Exploitation** | 4 | Exploits and payloads (`metasploit`, `msfvenom`, `searchsploit`) |
| **Password Attacks** | 7 | Credential attacks (`hydra`, `john`, `hashcat`) |
| **Post-Exploitation** | 7 | Lateral movement (`impacket`, `crackmapexec`, `bloodhound`) |
| **Network** | 7 | Network attacks and analysis (`responder`, `bettercap`, `tcpdump`) |

---

## All Tools

### Lifecycle Management

| Tool | Description |
|------|-------------|
| `kali_start` | Spin up a new Kali instance (Docker or Proxmox) |
| `kali_stop` | Stop and remove an instance |
| `kali_list` | List all running instances with status and IPs |
| `kali_exec` | Execute arbitrary command in instance |
| `kali_upload` | Upload file from host to instance |
| `kali_download` | Download file from instance to host |

### Reconnaissance

| Tool | Description |
|------|-------------|
| `nmap_scan` | Port scanning with customizable flags |
| `nmap_vuln_scan` | Vulnerability scanning with NSE scripts |
| `masscan_scan` | High-speed port scanner for large ranges |
| `whois_lookup` | Domain registration information |
| `dig_lookup` | DNS queries (A, MX, NS, TXT, etc.) |
| `dnsrecon_scan` | DNS enumeration and zone transfers |
| `theharvester_search` | Email, subdomain, and host harvesting |
| `amass_enum` | Subdomain enumeration (passive/active) |
| `sublist3r_scan` | Fast subdomain enumeration |

### Web Application Testing

| Tool | Description |
|------|-------------|
| `nikto_scan` | Web server vulnerability scanner |
| `dirb_scan` | Directory brute-forcing |
| `gobuster_dir` | Directory/file enumeration |
| `gobuster_dns` | DNS subdomain brute-forcing |
| `ffuf_fuzz` | Fast web fuzzer |
| `sqlmap_scan` | SQL injection detection and exploitation |
| `wpscan_scan` | WordPress vulnerability scanner |
| `whatweb_scan` | Web technology fingerprinting |
| `wafw00f_detect` | WAF detection |
| `nuclei_scan` | Template-based vulnerability scanner |
| `xsser_scan` | Cross-site scripting scanner |
| `commix_scan` | Command injection exploitation |

### Exploitation

| Tool | Description |
|------|-------------|
| `metasploit_search` | Search Metasploit modules |
| `metasploit_run` | Execute Metasploit exploits/auxiliary modules |
| `searchsploit_search` | Search Exploit-DB offline database |
| `msfvenom_generate` | Generate encoded payloads |

### Password Attacks

| Tool | Description |
|------|-------------|
| `hydra_attack` | Online password cracking (SSH, FTP, HTTP, SMB, etc.) |
| `medusa_attack` | Parallel modular login brute-forcer |
| `john_crack` | Offline hash cracking (John the Ripper) |
| `hashcat_crack` | GPU-accelerated hash cracking |
| `hash_identifier` | Identify hash types |
| `cewl_generate` | Custom wordlist from website spidering |
| `crunch_generate` | Pattern-based wordlist generator |

### Post-Exploitation

| Tool | Description |
|------|-------------|
| `impacket_secretsdump` | Dump NTLM hashes from Windows targets |
| `impacket_psexec` | Remote execution via SMB |
| `impacket_smbexec` | SMB-based command execution |
| `impacket_wmiexec` | WMI-based command execution |
| `evil_winrm` | WinRM shell access |
| `crackmapexec_run` | Swiss army knife for network attacks |
| `bloodhound_collect` | Active Directory enumeration |

### Network

| Tool | Description |
|------|-------------|
| `netcat_connect` | Network connections and listeners |
| `tcpdump_capture` | Packet capture |
| `wireshark_cli` | tshark packet analysis |
| `responder_run` | LLMNR/NBT-NS/mDNS poisoner |
| `bettercap_run` | Network attack framework |
| `socat_relay` | Advanced network relay/tunnel |
| `aircrack_crack` | WPA/WPA2 handshake cracking |

---

## Usage Example

```
Human: Start a Kali instance and scan 192.168.1.0/24 for open ports

Claude: I'll spin up a Kali instance and run an nmap scan.

[Uses kali_start]
Instance started: kali-1704825600, IP: 172.17.0.2

[Uses nmap_scan with target=192.168.1.0/24, ports=1-1000]
Nmap scan report for 192.168.1.0/24
Host: 192.168.1.1   Ports: 22/open/tcp, 80/open/tcp, 443/open/tcp
Host: 192.168.1.50  Ports: 22/open/tcp, 3389/open/tcp
...

Found 2 hosts with open ports. Would you like me to run vulnerability scans?
```

---

## Configuration

Copy `.env.example` to `.env`:

```bash
# Backend: "docker" or "proxmox"
KALI_BACKEND=docker

# Docker settings
DOCKER_SOCKET=/var/run/docker.sock
KALI_IMAGE=mcp-kali:latest

# Proxmox settings (when KALI_BACKEND=proxmox)
PROXMOX_HOST=192.168.1.100
PROXMOX_PORT=8006
PROXMOX_API_TOKEN_ID=root@pam!mcp-kali
PROXMOX_API_TOKEN_SECRET=xxxx
PROXMOX_SSH_USER=root
PROXMOX_SSH_KEY_PATH=~/.ssh/id_rsa
PROXMOX_KALI_TEMPLATE=local:vztmpl/kali-template
PROXMOX_TARGET_NODE=pve
```

---

## Security Notice

This tool is intended for **authorized use only**:

- Authorized penetration testing engagements
- CTF competitions
- Security research in lab environments
- Educational purposes

**Always ensure you have explicit written authorization before using these tools against any target.**

---

## Related Resources

- [Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins) - Discover more plugins, agents, and skills
- [MCP Proxmox Admin](https://github.com/EricGrill/mcp-proxmox-admin) - Proxmox VM management via MCP

---

## Contributing

1. Fork this repository
2. Add your tool wrapper to `src/tools/`
3. Register it in `src/server.ts`
4. Submit a pull request

---

## License

MIT
