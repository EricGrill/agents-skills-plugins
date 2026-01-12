# MCP Bitcoin CLI Design

## Overview

**mcp-bitcoin-cli** is a Python MCP server providing Bitcoin OP_RETURN data operations. It enables Claude to embed and read data on the Bitcoin blockchain, with support for documents, timestamps, tokens (BRC-20 compatible), and custom protocols.

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

**Key characteristics:**
- **Offline-capable**: Data encoding/decoding works without a node
- **Testnet default**: Mainnet requires explicit configuration
- **Dry-run first**: Prepare transactions before broadcasting

## Data Envelope Format

A general-purpose wrapper for all OP_RETURN data. Higher-level tools (BRC-20, documents, timestamps) use this envelope internally.

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

### Type Registry

| Type   | Hex    | Description                              |
|--------|--------|------------------------------------------|
| RAW    | 0x00   | Raw bytes, no structure                  |
| TEXT   | 0x01   | UTF-8 text with optional metadata        |
| JSON   | 0x02   | JSON document                            |
| HASH   | 0x03   | Hash commitment (timestamp/attestation)  |
| TOKEN  | 0x04   | Token operation (BRC-20 compatible)      |
| FILE   | 0x05   | File with content-type header            |
| CUSTOM | 0x80+  | User-defined protocols (128-255)         |

**Benefits:**
- Magic bytes make data discoverable on-chain
- Version allows protocol upgrades
- Type enables proper parsing without guessing
- CUSTOM range lets users define their own protocols

## MCP Tools

### Low-Level Primitives

These foundational tools work offline and power the high-level operations.

#### `encode_op_return`

Encode arbitrary data into OP_RETURN format.

```python
{
    "data": str | bytes,      # Raw data or hex string
    "envelope": bool = True,  # Wrap in BTCD envelope
    "type": str = "RAW"       # Envelope type if wrapped
}
# Returns: hex-encoded OP_RETURN script
```

#### `decode_op_return`

Parse OP_RETURN data from a transaction.

```python
{
    "script_hex": str,        # OP_RETURN script in hex
    # OR
    "txid": str,              # Transaction ID (requires node)
    "vout": int = 0           # Output index
}
# Returns: { type, version, payload, raw_bytes }
```

#### `build_op_return_transaction`

Construct a transaction with OP_RETURN output.

```python
{
    "data": str | bytes,      # Data to embed
    "envelope": bool = True,
    "type": str = "RAW",
    "funding_utxos": list,    # Optional: specific UTXOs
    "change_address": str,    # Optional: override change
    "fee_rate": float         # sats/vbyte
}
# Returns: { unsigned_tx_hex, estimated_fee, size_bytes }
```

#### `parse_envelope`

Parse BTCD envelope structure from raw bytes.

```python
{
    "data": str | bytes       # Hex or raw envelope data
}
# Returns: { magic, version, type, payload }
```

### Bitcoin Core Interface

Tools for interacting with a running Bitcoin node.

#### `get_node_info`

Check connection and network status.

```python
{}
# Returns: { connected, network, block_height, version }
```

#### `list_utxos`

List available UTXOs for funding transactions.

```python
{
    "min_confirmations": int = 1,
    "min_amount": float = 0    # Minimum BTC
}
# Returns: [{ txid, vout, amount, confirmations }]
```

#### `broadcast_transaction`

Send a signed transaction to the network.

```python
{
    "tx_hex": str,            # Signed transaction
    "dry_run": bool = True    # Default: just validate
}
# Returns: { txid, accepted, fee_paid } or { errors } if dry_run
```

#### `get_transaction`

Fetch transaction details.

```python
{
    "txid": str,
    "decode_op_return": bool = True  # Auto-parse OP_RETURN
}
# Returns: full transaction with decoded OP_RETURN if present
```

#### `search_op_returns`

Scan blocks for OP_RETURN transactions.

```python
{
    "start_block": int,
    "end_block": int,
    "magic": str = "BTCD",    # Filter by magic bytes
    "type": str = None        # Filter by envelope type
}
# Returns: [{ txid, block, type, payload_preview }]
```

### Token Operations (BRC-20 Template)

#### `create_token_deploy`

Deploy a new token (BRC-20 compatible format).

```python
{
    "tick": str,              # 4-char ticker
    "max_supply": int,        # Maximum supply
    "mint_limit": int = None, # Per-mint limit
    "decimals": int = 18,
    "protocol": str = "brc-20" # Or custom protocol name
}
# Returns: { envelope_hex, tx_template, token_info }
```

#### `create_token_mint`

Mint tokens.

```python
{
    "tick": str,
    "amount": int,
    "protocol": str = "brc-20"
}
# Returns: { envelope_hex, tx_template }
```

#### `create_token_transfer`

Transfer tokens.

```python
{
    "tick": str,
    "amount": int,
    "protocol": str = "brc-20"
}
# Returns: { envelope_hex, tx_template }
```

### Document Storage

#### `embed_document`

Store a document on-chain.

```python
{
    "content": str,           # Document content
    "content_type": str,      # "text/plain", "application/json", etc.
    "filename": str = None,   # Optional filename
    "compress": bool = True   # gzip if beneficial
}
# Returns: { envelope_hex, tx_template, size_bytes, compressed }
```

#### `read_document`

Retrieve and parse a document from a transaction.

```python
{
    "txid": str
}
# Returns: { content, content_type, filename, size_bytes }
```

### Timestamping & Attestation

#### `create_timestamp`

Create a hash commitment.

```python
{
    "data": str | bytes,      # Data to hash, or provide hash directly
    "hash": str = None,       # Pre-computed hash (sha256 hex)
    "metadata": dict = None   # Optional: { description, source, etc. }
}
# Returns: { envelope_hex, tx_template, hash, timestamp_utc }
```

#### `verify_timestamp`

Verify data against an on-chain timestamp.

```python
{
    "txid": str,
    "data": str | bytes = None,  # Original data to verify
    "hash": str = None           # Or just the hash
}
# Returns: { verified, block_time, block_height, hash }
```

## Configuration

Configuration file location: `~/.mcp-bitcoin-cli/config.toml`

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

### Safety Features

- **Network locked at startup**: Can't switch from testnet to mainnet mid-session
- **Dry-run by default**: `broadcast_transaction` validates first, requires `dry_run=False` to actually send
- **Fee estimation warnings**: Alert if fee seems unusually high
- **Size validation**: Reject data exceeding configured max before building transaction

## Project Structure

```
mcp-bitcoin-cli/
├── pyproject.toml
├── README.md
├── src/
│   └── mcp_bitcoin_cli/
│       ├── __init__.py
│       ├── server.py           # MCP server entry point
│       ├── config.py           # Configuration loading
│       ├── envelope.py         # BTCD envelope encode/decode
│       ├── primitives.py       # Low-level OP_RETURN tools
│       ├── node/
│       │   ├── __init__.py
│       │   ├── interface.py    # Abstract node interface
│       │   ├── cli.py          # bitcoin-cli subprocess
│       │   └── rpc.py          # JSON-RPC direct connection
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── primitives.py   # Low-level MCP tools
│       │   ├── node.py         # Node interaction tools
│       │   ├── tokens.py       # BRC-20 and custom tokens
│       │   ├── documents.py    # Document storage
│       │   └── timestamps.py   # Timestamping/attestation
│       └── protocols/
│           ├── __init__.py
│           ├── brc20.py        # BRC-20 format implementation
│           └── base.py         # Base protocol class for custom protocols
├── tests/
│   ├── test_envelope.py
│   ├── test_primitives.py
│   ├── test_tokens.py
│   └── test_node_mock.py
└── examples/
    ├── deploy_token.py
    ├── store_document.py
    └── timestamp_file.py
```

### Dependencies

- `mcp` - MCP server framework
- `python-bitcoinlib` - Bitcoin primitives
- `tomli` - Config parsing
- `httpx` - Async HTTP for RPC

## Design Decisions Summary

| Aspect             | Decision                                                    |
|--------------------|-------------------------------------------------------------|
| **Language**       | Python                                                      |
| **Connection**     | bitcoin-cli subprocess OR JSON-RPC (configurable)           |
| **Network default**| Testnet/Signet (mainnet requires explicit config)           |
| **Data format**    | BTCD envelope (magic + version + type + payload)            |
| **Max size**       | ~100KB (Bitcoin Core v30+)                                  |
| **Tool layers**    | Low-level primitives + high-level convenience tools         |
| **Safety**         | Dry-run default, confirmation before broadcast              |
| **Token support**  | BRC-20 as template, extensible for custom protocols         |
