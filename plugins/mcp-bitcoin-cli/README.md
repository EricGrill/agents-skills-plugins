<p align="center">
  <h1 align="center">MCP Bitcoin CLI</h1>
  <p align="center">
    <strong>Embed and read data on the Bitcoin blockchain through Claude</strong>
  </p>
  <p align="center">
    <a href="https://github.com/EricGrill/mcp-bitcoin-cli/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/tools-16-green.svg" alt="16 Tools">
    <img src="https://img.shields.io/badge/OP__RETURN-100KB-orange.svg" alt="OP_RETURN 100KB">
    <img src="https://img.shields.io/badge/python-%3E%3D3.11-blue.svg" alt="Python >= 3.11">
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

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that enables Claude to interact with Bitcoin's OP_RETURN functionality. Store documents, create timestamps, deploy tokens, and build custom protocols—all through natural language.

**Works with Claude Desktop, Cursor, and any MCP-compatible client.**

**Supports Bitcoin Core v30+ with up to ~100KB OP_RETURN data.**

---

## Quick Start

```bash
# Install from source
git clone https://github.com/EricGrill/mcp-bitcoin-cli.git
cd mcp-bitcoin-cli
pip install -e .

# Run the server
mcp-bitcoin-cli
```

Add to your Claude Desktop config and start working with Bitcoin:

> "Create a timestamp for this document on Bitcoin testnet"

---

## Why Use This?

| Feature | Description |
|---------|-------------|
| **Document Storage** | Embed documents up to 100KB directly on-chain |
| **Timestamping** | Create immutable SHA-256/SHA3 hash commitments |
| **BRC-20 Tokens** | Deploy, mint, and transfer tokens using the BRC-20 standard |
| **Custom Protocols** | Build your own OP_RETURN protocols with the BTCD envelope format |
| **Offline-Capable** | Encode/decode data without a running Bitcoin node |
| **Safety First** | Testnet default, dry-run mode, fee warnings |

---

## Available Tools

### Low-Level Primitives

Offline-capable tools for data encoding and transaction building.

| Tool | Description |
|------|-------------|
| `encode_op_return` | Encode arbitrary data into OP_RETURN script format |
| `decode_op_return` | Parse and extract data from OP_RETURN scripts |
| `build_op_return_transaction` | Construct transactions with OP_RETURN outputs |
| `parse_envelope` | Parse BTCD envelope structure from raw bytes |

### Bitcoin Core Interface

Tools for interacting with a running Bitcoin node.

| Tool | Description |
|------|-------------|
| `get_node_info` | Check connection status and network info |
| `list_utxos` | List available UTXOs for funding transactions |
| `broadcast_transaction` | Send signed transactions (dry-run by default) |
| `get_transaction` | Fetch and decode transaction details |
| `search_op_returns` | Scan blocks for OP_RETURN transactions |

### Token Operations (BRC-20)

Create and manage tokens using the [BRC-20 standard](https://domo-2.gitbook.io/brc-20-experiment/).

| Tool | Description |
|------|-------------|
| `create_token_deploy` | Deploy a new BRC-20 token |
| `create_token_mint` | Mint tokens from an existing deployment |
| `create_token_transfer` | Create a transfer inscription |

### Document Storage

Store and retrieve documents on the blockchain.

| Tool | Description |
|------|-------------|
| `embed_document` | Prepare documents for on-chain storage |
| `read_document` | Parse and extract documents from transactions |

### Timestamping & Attestation

Create cryptographic proofs of existence.

| Tool | Description |
|------|-------------|
| `create_timestamp` | Create SHA-256/SHA3 hash commitments |
| `verify_timestamp` | Verify data against on-chain timestamps |

---

## Data Envelope Format

All data uses the **BTCD envelope format** for discoverability and proper parsing:

```
┌─────────────────────────────────────────────────────────┐
│ OP_RETURN Envelope (variable size, up to ~100KB)        │
├──────────┬──────────┬──────────┬────────────────────────┤
│ Magic    │ Version  │ Type     │ Payload                │
│ (4 bytes)│ (1 byte) │ (1 byte) │ (variable)             │
├──────────┼──────────┼──────────┼────────────────────────┤
│ "BTCD"   │ 0x01     │ See below│ Type-specific data     │
└──────────┴──────────┴──────────┴────────────────────────┘
```

| Type | Hex | Description |
|------|-----|-------------|
| RAW | `0x00` | Raw bytes, no structure |
| TEXT | `0x01` | UTF-8 text |
| JSON | `0x02` | JSON document |
| HASH | `0x03` | Hash commitment (timestamp) |
| TOKEN | `0x04` | Token operation (BRC-20) |
| FILE | `0x05` | File with content-type |
| CUSTOM | `0x80+` | User-defined protocols |

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
    "bitcoin": {
      "command": "mcp-bitcoin-cli",
      "env": {
        "BITCOIN_NETWORK": "testnet",
        "BITCOIN_CLI_PATH": "/usr/local/bin/bitcoin-cli"
      }
    }
  }
}
```

### Configuration File

Create `~/.mcp-bitcoin-cli/config.toml`:

```toml
[connection]
method = "cli"              # "cli" or "rpc"
network = "testnet"         # "mainnet", "testnet", "signet", "regtest"

[cli]
path = "bitcoin-cli"        # Path to bitcoin-cli binary
datadir = ""                # Optional: custom datadir

[rpc]
host = "127.0.0.1"
port = 18332                # Testnet default
user = ""
password = ""

[safety]
require_confirmation = true # Prompt before broadcast
dry_run_default = true      # Always dry-run first
max_data_size = 102400      # 100KB limit
```

### Network Ports

| Network | Default RPC Port |
|---------|------------------|
| Mainnet | 8332 |
| Testnet | 18332 |
| Signet | 38332 |
| Regtest | 18443 |

---

## Examples

<details>
<summary><b>Timestamping</b></summary>

```
"Create a SHA-256 timestamp for this contract"
"Verify this document against timestamp in transaction abc123..."
"Create a SHA3-256 hash commitment for my research paper"
```

</details>

<details>
<summary><b>Document Storage</b></summary>

```
"Embed this JSON configuration on the blockchain"
"Store this text document with content-type text/plain"
"Read the document from transaction def456..."
```

</details>

<details>
<summary><b>BRC-20 Tokens</b></summary>

```
"Deploy a new token called TEST with max supply 21 million"
"Mint 1000 TEST tokens"
"Create a transfer inscription for 500 TEST"
```

</details>

<details>
<summary><b>Raw Data</b></summary>

```
"Encode this hex data into an OP_RETURN script"
"Decode the OP_RETURN from this transaction"
"Build a transaction with this message embedded"
```

</details>

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server                           │
├─────────────────────────────────────────────────────────┤
│  High-Level Tools                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ BRC-20 Ops  │ │ Document    │ │ Timestamp/      │   │
│  │ deploy/mint │ │ Storage     │ │ Attestation     │   │
│  └──────┬──────┘ └──────┬──────┘ └────────┬────────┘   │
│         │               │                  │            │
│  ───────┴───────────────┴──────────────────┴─────────  │
│                                                         │
│  Low-Level Primitives                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ encode_     │ │ decode_     │ │ build_op_return │   │
│  │ op_return   │ │ op_return   │ │ _transaction    │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Bitcoin Core Interface (configurable)                  │
│  ┌──────────────────┐  ┌────────────────────────────┐  │
│  │ bitcoin-cli      │  │ JSON-RPC (direct)          │  │
│  │ (subprocess)     │  │                            │  │
│  └──────────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Safety Features

| Feature | Description |
|---------|-------------|
| **Testnet Default** | Network locked to testnet unless explicitly configured |
| **Dry-Run Mode** | Transactions validated before broadcast by default |
| **Fee Warnings** | Alerts for unusually high fees |
| **Size Validation** | Rejects data exceeding configured max before building |
| **Network Lock** | Can't switch networks mid-session |

---

## Development

```bash
# Clone
git clone https://github.com/EricGrill/mcp-bitcoin-cli.git
cd mcp-bitcoin-cli

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=mcp_bitcoin_cli
```

### Project Structure

```
src/mcp_bitcoin_cli/
├── __init__.py          # Public exports
├── server.py            # MCP server with 16 tools
├── envelope.py          # BTCD envelope encoding/decoding
├── primitives.py        # OP_RETURN script encoding/decoding
├── config.py            # Configuration loading
├── node/
│   ├── interface.py     # Abstract node interface
│   ├── cli.py           # bitcoin-cli subprocess
│   └── rpc.py           # JSON-RPC direct connection
└── protocols/
    ├── base.py          # Base protocol class
    └── brc20.py         # BRC-20 token protocol
```

---

## Troubleshooting

<details>
<summary><b>Cannot connect to Bitcoin Core</b></summary>

1. Verify Bitcoin Core is running: `bitcoin-cli getblockchaininfo`
2. Check network matches config (testnet vs mainnet)
3. Verify RPC credentials if using JSON-RPC mode

</details>

<details>
<summary><b>Transaction rejected</b></summary>

1. Use `broadcast_transaction` with `dry_run=true` first
2. Check fee rate is sufficient
3. Verify UTXOs have enough confirmations

</details>

<details>
<summary><b>Data too large</b></summary>

- Bitcoin Core v30+ supports up to ~100KB OP_RETURN
- Older versions limited to 80 bytes
- Check `max_data_size` in config

</details>

<details>
<summary><b>Import errors</b></summary>

```bash
# Verify installation
python -c "import mcp_bitcoin_cli; print(mcp_bitcoin_cli.__version__)"

# Reinstall if needed
pip install -e ".[dev]"
```

</details>

---

## Contributing

Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `pytest`
4. Commit: `git commit -m 'Add my feature'`
5. Push: `git push origin feature/my-feature`
6. Open a Pull Request

---

## Related Projects

- [MCP Proxmox Admin](https://github.com/EricGrill/mcp-proxmox-admin) - Manage Proxmox VE through Claude
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
- [BRC-20 Standard](https://domo-2.gitbook.io/brc-20-experiment/) - Bitcoin token standard

---

## License

MIT
