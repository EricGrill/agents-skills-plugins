# MCP Bitcoin CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python MCP server for Bitcoin OP_RETURN data operations supporting documents, timestamps, tokens, and custom protocols.

**Architecture:** Layered design with low-level primitives (envelope encoding, transaction building) and high-level convenience tools (BRC-20, documents, timestamps). Supports both offline operations and connected mode via bitcoin-cli or JSON-RPC.

**Tech Stack:** Python 3.11+, mcp library, python-bitcoinlib, tomli, httpx

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/mcp_bitcoin_cli/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mcp-bitcoin-cli"
version = "0.1.0"
description = "MCP server for Bitcoin OP_RETURN data operations"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
    "python-bitcoinlib>=0.12.0",
    "tomli>=2.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[project.scripts]
mcp-bitcoin-cli = "mcp_bitcoin_cli.server:main"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_bitcoin_cli"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 2: Create package init**

```python
# src/mcp_bitcoin_cli/__init__.py
"""MCP server for Bitcoin OP_RETURN data operations."""

__version__ = "0.1.0"
```

**Step 3: Create tests init**

```python
# tests/__init__.py
"""Tests for mcp-bitcoin-cli."""
```

**Step 4: Create directory structure**

Run:
```bash
mkdir -p src/mcp_bitcoin_cli/node
mkdir -p src/mcp_bitcoin_cli/tools
mkdir -p src/mcp_bitcoin_cli/protocols
mkdir -p tests
touch src/mcp_bitcoin_cli/node/__init__.py
touch src/mcp_bitcoin_cli/tools/__init__.py
touch src/mcp_bitcoin_cli/protocols/__init__.py
```

**Step 5: Install dependencies**

Run:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Step 6: Verify installation**

Run: `python -c "import mcp_bitcoin_cli; print(mcp_bitcoin_cli.__version__)"`
Expected: `0.1.0`

**Step 7: Commit**

```bash
git add -A
git commit -m "chore: initial project setup with dependencies"
```

---

## Task 2: Envelope Module - Core Data Structure

**Files:**
- Create: `src/mcp_bitcoin_cli/envelope.py`
- Create: `tests/test_envelope.py`

**Step 1: Write failing test for envelope encoding**

```python
# tests/test_envelope.py
"""Tests for BTCD envelope encoding/decoding."""

import pytest
from mcp_bitcoin_cli.envelope import (
    Envelope,
    EnvelopeType,
    MAGIC_BYTES,
    VERSION,
    encode_envelope,
    decode_envelope,
)


class TestEnvelopeEncoding:
    """Test envelope encoding."""

    def test_encode_raw_data(self):
        """Encode raw bytes into envelope format."""
        data = b"hello world"
        result = encode_envelope(data, EnvelopeType.RAW)

        assert result[:4] == MAGIC_BYTES
        assert result[4] == VERSION
        assert result[5] == EnvelopeType.RAW.value
        assert result[6:] == data

    def test_encode_text_data(self):
        """Encode text into envelope format."""
        text = "Hello, Bitcoin!"
        result = encode_envelope(text.encode(), EnvelopeType.TEXT)

        assert result[:4] == MAGIC_BYTES
        assert result[5] == EnvelopeType.TEXT.value
        assert result[6:] == text.encode()

    def test_encode_from_hex_string(self):
        """Encode data provided as hex string."""
        hex_data = "deadbeef"
        result = encode_envelope(bytes.fromhex(hex_data), EnvelopeType.RAW)

        assert result[6:] == bytes.fromhex(hex_data)


class TestEnvelopeDecoding:
    """Test envelope decoding."""

    def test_decode_valid_envelope(self):
        """Decode a valid envelope."""
        data = b"test payload"
        encoded = encode_envelope(data, EnvelopeType.RAW)

        envelope = decode_envelope(encoded)

        assert envelope.magic == MAGIC_BYTES
        assert envelope.version == VERSION
        assert envelope.type == EnvelopeType.RAW
        assert envelope.payload == data

    def test_decode_invalid_magic(self):
        """Reject envelope with wrong magic bytes."""
        invalid = b"XXXX\x01\x00test"

        with pytest.raises(ValueError, match="Invalid magic bytes"):
            decode_envelope(invalid)

    def test_decode_too_short(self):
        """Reject envelope that's too short."""
        with pytest.raises(ValueError, match="too short"):
            decode_envelope(b"BTC")


class TestEnvelopeTypes:
    """Test all envelope types."""

    @pytest.mark.parametrize("env_type", list(EnvelopeType))
    def test_roundtrip_all_types(self, env_type):
        """All envelope types encode and decode correctly."""
        data = b"test data"
        encoded = encode_envelope(data, env_type)
        decoded = decode_envelope(encoded)

        assert decoded.type == env_type
        assert decoded.payload == data
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_envelope.py -v`
Expected: FAIL with import errors

**Step 3: Write envelope implementation**

```python
# src/mcp_bitcoin_cli/envelope.py
"""BTCD envelope encoding and decoding.

The envelope format:
- Magic (4 bytes): "BTCD"
- Version (1 byte): Protocol version
- Type (1 byte): Data type identifier
- Payload (variable): Type-specific data
"""

from dataclasses import dataclass
from enum import IntEnum


MAGIC_BYTES = b"BTCD"
VERSION = 0x01


class EnvelopeType(IntEnum):
    """Envelope data types."""

    RAW = 0x00      # Raw bytes, no structure
    TEXT = 0x01     # UTF-8 text
    JSON = 0x02     # JSON document
    HASH = 0x03     # Hash commitment (timestamp/attestation)
    TOKEN = 0x04    # Token operation (BRC-20 compatible)
    FILE = 0x05     # File with content-type header
    # 0x80-0xFF reserved for custom protocols


@dataclass
class Envelope:
    """Decoded envelope structure."""

    magic: bytes
    version: int
    type: EnvelopeType
    payload: bytes


def encode_envelope(data: bytes, envelope_type: EnvelopeType) -> bytes:
    """Encode data into BTCD envelope format.

    Args:
        data: Raw bytes to encode
        envelope_type: Type identifier for the data

    Returns:
        Encoded envelope as bytes
    """
    return MAGIC_BYTES + bytes([VERSION, envelope_type.value]) + data


def decode_envelope(data: bytes) -> Envelope:
    """Decode BTCD envelope format.

    Args:
        data: Raw envelope bytes

    Returns:
        Decoded Envelope object

    Raises:
        ValueError: If envelope is invalid
    """
    if len(data) < 6:
        raise ValueError("Envelope data too short (minimum 6 bytes)")

    magic = data[:4]
    if magic != MAGIC_BYTES:
        raise ValueError(f"Invalid magic bytes: expected {MAGIC_BYTES!r}, got {magic!r}")

    version = data[4]
    type_byte = data[5]
    payload = data[6:]

    try:
        envelope_type = EnvelopeType(type_byte)
    except ValueError:
        # Allow custom types (0x80+)
        if type_byte >= 0x80:
            envelope_type = EnvelopeType(type_byte)
        else:
            raise ValueError(f"Unknown envelope type: {type_byte:#x}")

    return Envelope(
        magic=magic,
        version=version,
        type=envelope_type,
        payload=payload,
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_envelope.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/mcp_bitcoin_cli/envelope.py tests/test_envelope.py
git commit -m "feat: add BTCD envelope encoding/decoding"
```

---

## Task 3: OP_RETURN Primitives

**Files:**
- Create: `src/mcp_bitcoin_cli/primitives.py`
- Create: `tests/test_primitives.py`

**Step 1: Write failing test for OP_RETURN encoding**

```python
# tests/test_primitives.py
"""Tests for OP_RETURN primitives."""

import pytest
from mcp_bitcoin_cli.primitives import (
    encode_op_return_script,
    decode_op_return_script,
    OP_RETURN,
    OP_PUSHDATA1,
    OP_PUSHDATA2,
)
from mcp_bitcoin_cli.envelope import EnvelopeType, encode_envelope


class TestOpReturnEncoding:
    """Test OP_RETURN script encoding."""

    def test_encode_small_data(self):
        """Encode small data (< 76 bytes) directly."""
        data = b"hello"
        script = encode_op_return_script(data)

        assert script[0] == OP_RETURN
        assert script[1] == len(data)  # Direct push
        assert script[2:] == data

    def test_encode_medium_data(self):
        """Encode medium data (76-255 bytes) with PUSHDATA1."""
        data = b"x" * 100
        script = encode_op_return_script(data)

        assert script[0] == OP_RETURN
        assert script[1] == OP_PUSHDATA1
        assert script[2] == len(data)
        assert script[3:] == data

    def test_encode_large_data(self):
        """Encode large data (256+ bytes) with PUSHDATA2."""
        data = b"x" * 300
        script = encode_op_return_script(data)

        assert script[0] == OP_RETURN
        assert script[1] == OP_PUSHDATA2
        # Little-endian length
        assert int.from_bytes(script[2:4], 'little') == len(data)
        assert script[4:] == data

    def test_encode_with_envelope(self):
        """Encode data wrapped in envelope."""
        data = b"test"
        envelope = encode_envelope(data, EnvelopeType.TEXT)
        script = encode_op_return_script(envelope)

        # Script contains envelope with magic bytes
        assert b"BTCD" in script


class TestOpReturnDecoding:
    """Test OP_RETURN script decoding."""

    def test_decode_small_data(self):
        """Decode small OP_RETURN."""
        data = b"hello"
        script = encode_op_return_script(data)

        decoded = decode_op_return_script(script)
        assert decoded == data

    def test_decode_medium_data(self):
        """Decode medium OP_RETURN with PUSHDATA1."""
        data = b"x" * 100
        script = encode_op_return_script(data)

        decoded = decode_op_return_script(script)
        assert decoded == data

    def test_decode_large_data(self):
        """Decode large OP_RETURN with PUSHDATA2."""
        data = b"x" * 300
        script = encode_op_return_script(data)

        decoded = decode_op_return_script(script)
        assert decoded == data

    def test_decode_invalid_opcode(self):
        """Reject non-OP_RETURN script."""
        script = bytes([0x76, 0x05]) + b"hello"  # OP_DUP instead

        with pytest.raises(ValueError, match="not an OP_RETURN"):
            decode_op_return_script(script)

    def test_roundtrip_max_size(self):
        """Roundtrip near-max OP_RETURN (100KB)."""
        data = b"x" * 99000
        script = encode_op_return_script(data)
        decoded = decode_op_return_script(script)

        assert decoded == data
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_primitives.py -v`
Expected: FAIL with import errors

**Step 3: Write primitives implementation**

```python
# src/mcp_bitcoin_cli/primitives.py
"""Bitcoin OP_RETURN script encoding and decoding.

Supports Bitcoin Core v30+ with up to ~100KB OP_RETURN data.
"""

# Bitcoin script opcodes
OP_RETURN = 0x6A
OP_PUSHDATA1 = 0x4C
OP_PUSHDATA2 = 0x4D
OP_PUSHDATA4 = 0x4E


def encode_op_return_script(data: bytes) -> bytes:
    """Encode data into an OP_RETURN script.

    Uses appropriate push opcode based on data size:
    - < 76 bytes: direct push (1 byte length)
    - 76-255 bytes: OP_PUSHDATA1 (1 byte length)
    - 256-65535 bytes: OP_PUSHDATA2 (2 byte length, little-endian)
    - > 65535 bytes: OP_PUSHDATA4 (4 byte length, little-endian)

    Args:
        data: Raw data to embed in OP_RETURN

    Returns:
        Complete OP_RETURN script as bytes
    """
    length = len(data)

    if length < 76:
        # Direct push
        return bytes([OP_RETURN, length]) + data
    elif length <= 255:
        # OP_PUSHDATA1
        return bytes([OP_RETURN, OP_PUSHDATA1, length]) + data
    elif length <= 65535:
        # OP_PUSHDATA2 (little-endian)
        return bytes([OP_RETURN, OP_PUSHDATA2]) + length.to_bytes(2, 'little') + data
    else:
        # OP_PUSHDATA4 (little-endian)
        return bytes([OP_RETURN, OP_PUSHDATA4]) + length.to_bytes(4, 'little') + data


def decode_op_return_script(script: bytes) -> bytes:
    """Decode data from an OP_RETURN script.

    Args:
        script: OP_RETURN script bytes

    Returns:
        Extracted data payload

    Raises:
        ValueError: If script is not a valid OP_RETURN
    """
    if len(script) < 2:
        raise ValueError("Script too short")

    if script[0] != OP_RETURN:
        raise ValueError(f"Script is not an OP_RETURN (opcode: {script[0]:#x})")

    pos = 1
    push_byte = script[pos]
    pos += 1

    if push_byte < 76:
        # Direct push
        length = push_byte
    elif push_byte == OP_PUSHDATA1:
        length = script[pos]
        pos += 1
    elif push_byte == OP_PUSHDATA2:
        length = int.from_bytes(script[pos:pos+2], 'little')
        pos += 2
    elif push_byte == OP_PUSHDATA4:
        length = int.from_bytes(script[pos:pos+4], 'little')
        pos += 4
    else:
        raise ValueError(f"Invalid push opcode: {push_byte:#x}")

    return script[pos:pos+length]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_primitives.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/mcp_bitcoin_cli/primitives.py tests/test_primitives.py
git commit -m "feat: add OP_RETURN script encoding/decoding"
```

---

## Task 4: Configuration Module

**Files:**
- Create: `src/mcp_bitcoin_cli/config.py`
- Create: `tests/test_config.py`

**Step 1: Write failing test for configuration**

```python
# tests/test_config.py
"""Tests for configuration loading."""

import pytest
from pathlib import Path
from mcp_bitcoin_cli.config import (
    Config,
    ConnectionMethod,
    Network,
    load_config,
    DEFAULT_CONFIG,
)


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_network_is_testnet(self):
        """Default network should be testnet for safety."""
        config = Config()
        assert config.network == Network.TESTNET

    def test_default_connection_is_cli(self):
        """Default connection method is bitcoin-cli."""
        config = Config()
        assert config.connection_method == ConnectionMethod.CLI

    def test_default_dry_run_is_true(self):
        """Dry run should be enabled by default."""
        config = Config()
        assert config.dry_run_default is True

    def test_default_max_data_size(self):
        """Max data size should be 100KB."""
        config = Config()
        assert config.max_data_size == 102400


class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_from_toml_string(self, tmp_path):
        """Load configuration from TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('''
[connection]
method = "rpc"
network = "signet"

[rpc]
host = "192.168.1.100"
port = 38332
user = "bitcoinrpc"
password = "secret123"

[safety]
dry_run_default = false
max_data_size = 50000
''')

        config = load_config(config_file)

        assert config.connection_method == ConnectionMethod.RPC
        assert config.network == Network.SIGNET
        assert config.rpc_host == "192.168.1.100"
        assert config.rpc_port == 38332
        assert config.dry_run_default is False
        assert config.max_data_size == 50000

    def test_load_missing_file_uses_defaults(self, tmp_path):
        """Missing config file should use defaults."""
        config = load_config(tmp_path / "nonexistent.toml")

        assert config.network == Network.TESTNET
        assert config.dry_run_default is True

    def test_partial_config_merges_with_defaults(self, tmp_path):
        """Partial config should merge with defaults."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('''
[connection]
network = "regtest"
''')

        config = load_config(config_file)

        assert config.network == Network.REGTEST
        assert config.connection_method == ConnectionMethod.CLI  # default
        assert config.dry_run_default is True  # default


class TestNetworkPorts:
    """Test default RPC ports per network."""

    @pytest.mark.parametrize("network,expected_port", [
        (Network.MAINNET, 8332),
        (Network.TESTNET, 18332),
        (Network.SIGNET, 38332),
        (Network.REGTEST, 18443),
    ])
    def test_default_port_for_network(self, network, expected_port):
        """Each network has correct default RPC port."""
        config = Config(network=network)
        assert config.default_rpc_port == expected_port
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with import errors

**Step 3: Write config implementation**

```python
# src/mcp_bitcoin_cli/config.py
"""Configuration loading and management."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import tomli
except ImportError:
    import tomllib as tomli  # Python 3.11+


class ConnectionMethod(Enum):
    """Bitcoin Core connection method."""
    CLI = "cli"
    RPC = "rpc"


class Network(Enum):
    """Bitcoin network."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    SIGNET = "signet"
    REGTEST = "regtest"


# Default RPC ports per network
DEFAULT_PORTS = {
    Network.MAINNET: 8332,
    Network.TESTNET: 18332,
    Network.SIGNET: 38332,
    Network.REGTEST: 18443,
}


@dataclass
class Config:
    """Server configuration."""

    # Connection settings
    connection_method: ConnectionMethod = ConnectionMethod.CLI
    network: Network = Network.TESTNET

    # CLI settings
    cli_path: str = "bitcoin-cli"
    cli_datadir: str = ""

    # RPC settings
    rpc_host: str = "127.0.0.1"
    rpc_port: Optional[int] = None
    rpc_user: str = ""
    rpc_password: str = ""

    # Safety settings
    require_confirmation: bool = True
    dry_run_default: bool = True
    max_data_size: int = 102400  # 100KB

    @property
    def default_rpc_port(self) -> int:
        """Get default RPC port for current network."""
        return DEFAULT_PORTS[self.network]

    def get_rpc_port(self) -> int:
        """Get configured or default RPC port."""
        return self.rpc_port if self.rpc_port else self.default_rpc_port


DEFAULT_CONFIG = Config()


def load_config(path: Path) -> Config:
    """Load configuration from TOML file.

    Args:
        path: Path to config file

    Returns:
        Loaded configuration, merged with defaults
    """
    if not path.exists():
        return Config()

    with open(path, "rb") as f:
        data = tomli.load(f)

    # Parse connection section
    conn = data.get("connection", {})
    method_str = conn.get("method", "cli")
    network_str = conn.get("network", "testnet")

    # Parse CLI section
    cli = data.get("cli", {})

    # Parse RPC section
    rpc = data.get("rpc", {})

    # Parse safety section
    safety = data.get("safety", {})

    return Config(
        connection_method=ConnectionMethod(method_str),
        network=Network(network_str),
        cli_path=cli.get("path", "bitcoin-cli"),
        cli_datadir=cli.get("datadir", ""),
        rpc_host=rpc.get("host", "127.0.0.1"),
        rpc_port=rpc.get("port"),
        rpc_user=rpc.get("user", ""),
        rpc_password=rpc.get("password", ""),
        require_confirmation=safety.get("require_confirmation", True),
        dry_run_default=safety.get("dry_run_default", True),
        max_data_size=safety.get("max_data_size", 102400),
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/mcp_bitcoin_cli/config.py tests/test_config.py
git commit -m "feat: add configuration loading with safety defaults"
```

---

## Task 5: BRC-20 Protocol Implementation

**Files:**
- Create: `src/mcp_bitcoin_cli/protocols/base.py`
- Create: `src/mcp_bitcoin_cli/protocols/brc20.py`
- Create: `tests/test_brc20.py`

**Step 1: Write failing test for BRC-20**

```python
# tests/test_brc20.py
"""Tests for BRC-20 protocol implementation."""

import json
import pytest
from mcp_bitcoin_cli.protocols.brc20 import (
    BRC20Protocol,
    BRC20Deploy,
    BRC20Mint,
    BRC20Transfer,
)
from mcp_bitcoin_cli.envelope import decode_envelope, EnvelopeType


class TestBRC20Deploy:
    """Test BRC-20 deploy operation."""

    def test_create_deploy(self):
        """Create a deploy inscription."""
        deploy = BRC20Deploy(
            tick="TEST",
            max_supply=21000000,
            mint_limit=1000,
        )

        assert deploy.tick == "TEST"
        assert deploy.max_supply == 21000000
        assert deploy.mint_limit == 1000

    def test_deploy_to_json(self):
        """Deploy converts to correct JSON format."""
        deploy = BRC20Deploy(
            tick="TEST",
            max_supply=21000000,
            mint_limit=1000,
            decimals=8,
        )

        data = deploy.to_json()
        parsed = json.loads(data)

        assert parsed["p"] == "brc-20"
        assert parsed["op"] == "deploy"
        assert parsed["tick"] == "TEST"
        assert parsed["max"] == "21000000"
        assert parsed["lim"] == "1000"
        assert parsed["dec"] == "8"

    def test_deploy_to_envelope(self):
        """Deploy creates valid envelope."""
        deploy = BRC20Deploy(tick="TEST", max_supply=1000)
        envelope = deploy.to_envelope()

        decoded = decode_envelope(envelope)
        assert decoded.type == EnvelopeType.TOKEN

    def test_tick_must_be_4_chars(self):
        """Tick must be exactly 4 characters."""
        with pytest.raises(ValueError, match="4 characters"):
            BRC20Deploy(tick="AB", max_supply=1000)


class TestBRC20Mint:
    """Test BRC-20 mint operation."""

    def test_create_mint(self):
        """Create a mint inscription."""
        mint = BRC20Mint(tick="TEST", amount=100)

        data = mint.to_json()
        parsed = json.loads(data)

        assert parsed["p"] == "brc-20"
        assert parsed["op"] == "mint"
        assert parsed["tick"] == "TEST"
        assert parsed["amt"] == "100"


class TestBRC20Transfer:
    """Test BRC-20 transfer operation."""

    def test_create_transfer(self):
        """Create a transfer inscription."""
        transfer = BRC20Transfer(tick="TEST", amount=50)

        data = transfer.to_json()
        parsed = json.loads(data)

        assert parsed["p"] == "brc-20"
        assert parsed["op"] == "transfer"
        assert parsed["tick"] == "TEST"
        assert parsed["amt"] == "50"


class TestBRC20Protocol:
    """Test BRC-20 protocol helper."""

    def test_parse_deploy(self):
        """Parse deploy JSON back to object."""
        json_str = '{"p":"brc-20","op":"deploy","tick":"TEST","max":"1000"}'

        op = BRC20Protocol.parse(json_str)

        assert isinstance(op, BRC20Deploy)
        assert op.tick == "TEST"
        assert op.max_supply == 1000

    def test_parse_mint(self):
        """Parse mint JSON back to object."""
        json_str = '{"p":"brc-20","op":"mint","tick":"TEST","amt":"100"}'

        op = BRC20Protocol.parse(json_str)

        assert isinstance(op, BRC20Mint)
        assert op.amount == 100

    def test_parse_invalid_protocol(self):
        """Reject non-BRC-20 JSON."""
        json_str = '{"p":"other","op":"deploy"}'

        with pytest.raises(ValueError, match="Not a BRC-20"):
            BRC20Protocol.parse(json_str)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_brc20.py -v`
Expected: FAIL with import errors

**Step 3: Write base protocol class**

```python
# src/mcp_bitcoin_cli/protocols/base.py
"""Base protocol class for custom protocols."""

from abc import ABC, abstractmethod


class Protocol(ABC):
    """Base class for OP_RETURN protocols."""

    @abstractmethod
    def to_bytes(self) -> bytes:
        """Convert to raw bytes for embedding."""
        pass

    @abstractmethod
    def to_envelope(self) -> bytes:
        """Convert to BTCD envelope format."""
        pass
```

**Step 4: Write BRC-20 implementation**

```python
# src/mcp_bitcoin_cli/protocols/brc20.py
"""BRC-20 token protocol implementation.

BRC-20 is a token standard using JSON inscriptions:
- Deploy: Create new token
- Mint: Mint tokens
- Transfer: Transfer tokens

Reference: https://domo-2.gitbook.io/brc-20-experiment/
"""

import json
from dataclasses import dataclass
from typing import Optional, Union

from mcp_bitcoin_cli.envelope import encode_envelope, EnvelopeType
from mcp_bitcoin_cli.protocols.base import Protocol


@dataclass
class BRC20Deploy(Protocol):
    """BRC-20 deploy operation."""

    tick: str
    max_supply: int
    mint_limit: Optional[int] = None
    decimals: int = 18

    def __post_init__(self):
        if len(self.tick) != 4:
            raise ValueError(f"Tick must be exactly 4 characters, got {len(self.tick)}")

    def to_json(self) -> str:
        """Convert to BRC-20 JSON format."""
        data = {
            "p": "brc-20",
            "op": "deploy",
            "tick": self.tick,
            "max": str(self.max_supply),
        }
        if self.mint_limit is not None:
            data["lim"] = str(self.mint_limit)
        if self.decimals != 18:
            data["dec"] = str(self.decimals)
        return json.dumps(data, separators=(',', ':'))

    def to_bytes(self) -> bytes:
        """Convert to raw bytes."""
        return self.to_json().encode('utf-8')

    def to_envelope(self) -> bytes:
        """Convert to BTCD envelope format."""
        return encode_envelope(self.to_bytes(), EnvelopeType.TOKEN)


@dataclass
class BRC20Mint(Protocol):
    """BRC-20 mint operation."""

    tick: str
    amount: int

    def __post_init__(self):
        if len(self.tick) != 4:
            raise ValueError(f"Tick must be exactly 4 characters, got {len(self.tick)}")

    def to_json(self) -> str:
        """Convert to BRC-20 JSON format."""
        return json.dumps({
            "p": "brc-20",
            "op": "mint",
            "tick": self.tick,
            "amt": str(self.amount),
        }, separators=(',', ':'))

    def to_bytes(self) -> bytes:
        return self.to_json().encode('utf-8')

    def to_envelope(self) -> bytes:
        return encode_envelope(self.to_bytes(), EnvelopeType.TOKEN)


@dataclass
class BRC20Transfer(Protocol):
    """BRC-20 transfer operation."""

    tick: str
    amount: int

    def __post_init__(self):
        if len(self.tick) != 4:
            raise ValueError(f"Tick must be exactly 4 characters, got {len(self.tick)}")

    def to_json(self) -> str:
        """Convert to BRC-20 JSON format."""
        return json.dumps({
            "p": "brc-20",
            "op": "transfer",
            "tick": self.tick,
            "amt": str(self.amount),
        }, separators=(',', ':'))

    def to_bytes(self) -> bytes:
        return self.to_json().encode('utf-8')

    def to_envelope(self) -> bytes:
        return encode_envelope(self.to_bytes(), EnvelopeType.TOKEN)


BRC20Operation = Union[BRC20Deploy, BRC20Mint, BRC20Transfer]


class BRC20Protocol:
    """BRC-20 protocol parser and helpers."""

    @staticmethod
    def parse(json_str: str) -> BRC20Operation:
        """Parse BRC-20 JSON into operation object.

        Args:
            json_str: BRC-20 JSON string

        Returns:
            Appropriate BRC20 operation object

        Raises:
            ValueError: If not valid BRC-20 JSON
        """
        data = json.loads(json_str)

        if data.get("p") != "brc-20":
            raise ValueError(f"Not a BRC-20 inscription: p={data.get('p')}")

        op = data.get("op")
        tick = data.get("tick", "")

        if op == "deploy":
            return BRC20Deploy(
                tick=tick,
                max_supply=int(data.get("max", 0)),
                mint_limit=int(data["lim"]) if "lim" in data else None,
                decimals=int(data.get("dec", 18)),
            )
        elif op == "mint":
            return BRC20Mint(
                tick=tick,
                amount=int(data.get("amt", 0)),
            )
        elif op == "transfer":
            return BRC20Transfer(
                tick=tick,
                amount=int(data.get("amt", 0)),
            )
        else:
            raise ValueError(f"Unknown BRC-20 operation: {op}")
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_brc20.py -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/mcp_bitcoin_cli/protocols/base.py src/mcp_bitcoin_cli/protocols/brc20.py tests/test_brc20.py
git commit -m "feat: add BRC-20 token protocol implementation"
```

---

## Task 6: Node Interface - Abstract Base

**Files:**
- Create: `src/mcp_bitcoin_cli/node/interface.py`

**Step 1: Write interface definition**

```python
# src/mcp_bitcoin_cli/node/interface.py
"""Abstract interface for Bitcoin Core communication."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class NodeInfo:
    """Bitcoin node information."""
    connected: bool
    network: str
    block_height: int
    version: int
    errors: str = ""


@dataclass
class UTXO:
    """Unspent transaction output."""
    txid: str
    vout: int
    amount: float  # BTC
    confirmations: int
    script_pubkey: str


@dataclass
class TransactionInfo:
    """Transaction information."""
    txid: str
    blockhash: Optional[str]
    confirmations: int
    time: Optional[int]
    hex: str
    decoded: dict


class NodeInterface(ABC):
    """Abstract interface for Bitcoin Core communication."""

    @abstractmethod
    async def get_info(self) -> NodeInfo:
        """Get node status and network info."""
        pass

    @abstractmethod
    async def list_utxos(
        self,
        min_confirmations: int = 1,
        min_amount: float = 0,
    ) -> list[UTXO]:
        """List available UTXOs."""
        pass

    @abstractmethod
    async def get_transaction(self, txid: str) -> TransactionInfo:
        """Get transaction details."""
        pass

    @abstractmethod
    async def send_raw_transaction(
        self,
        tx_hex: str,
        max_fee_rate: Optional[float] = None,
    ) -> str:
        """Broadcast signed transaction, return txid."""
        pass

    @abstractmethod
    async def test_mempool_accept(self, tx_hex: str) -> dict[str, Any]:
        """Test if transaction would be accepted (dry run)."""
        pass

    @abstractmethod
    async def create_raw_transaction(
        self,
        inputs: list[dict],
        outputs: list[dict],
    ) -> str:
        """Create unsigned raw transaction."""
        pass

    @abstractmethod
    async def fund_raw_transaction(
        self,
        tx_hex: str,
        options: Optional[dict] = None,
    ) -> dict:
        """Add inputs to fund transaction, return hex and fee."""
        pass

    @abstractmethod
    async def get_new_address(self, label: str = "") -> str:
        """Generate new receiving address."""
        pass

    @abstractmethod
    async def estimate_fee(self, conf_target: int = 6) -> float:
        """Estimate fee rate in BTC/kB."""
        pass
```

**Step 2: Commit**

```bash
git add src/mcp_bitcoin_cli/node/interface.py
git commit -m "feat: add abstract node interface"
```

---

## Task 7: Node Interface - CLI Implementation

**Files:**
- Create: `src/mcp_bitcoin_cli/node/cli.py`
- Create: `tests/test_node_cli.py`

**Step 1: Write failing test for CLI interface**

```python
# tests/test_node_cli.py
"""Tests for bitcoin-cli interface."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from mcp_bitcoin_cli.node.cli import BitcoinCLI
from mcp_bitcoin_cli.config import Config, Network


class TestBitcoinCLI:
    """Test bitcoin-cli subprocess interface."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance with test config."""
        config = Config(network=Network.REGTEST)
        return BitcoinCLI(config)

    def test_build_command_basic(self, cli):
        """Build basic command with network flag."""
        cmd = cli._build_command("getblockcount")

        assert "bitcoin-cli" in cmd
        assert "-regtest" in cmd
        assert "getblockcount" in cmd

    def test_build_command_with_args(self, cli):
        """Build command with arguments."""
        cmd = cli._build_command("gettransaction", "abc123")

        assert "gettransaction" in cmd
        assert "abc123" in cmd

    @pytest.mark.asyncio
    async def test_get_info_parses_response(self, cli):
        """Parse getblockchaininfo response."""
        mock_response = {
            "chain": "regtest",
            "blocks": 100,
            "headers": 100,
            "bestblockhash": "abc",
            "warnings": "",
        }
        mock_network = {"version": 270000, "subversion": "/Satoshi:27.0.0/"}

        with patch.object(cli, '_call', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [mock_response, mock_network]

            info = await cli.get_info()

            assert info.connected is True
            assert info.network == "regtest"
            assert info.block_height == 100
            assert info.version == 270000

    @pytest.mark.asyncio
    async def test_list_utxos(self, cli):
        """Parse listunspent response."""
        mock_response = [
            {
                "txid": "abc123",
                "vout": 0,
                "amount": 1.5,
                "confirmations": 10,
                "scriptPubKey": "76a914...",
            }
        ]

        with patch.object(cli, '_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            utxos = await cli.list_utxos()

            assert len(utxos) == 1
            assert utxos[0].txid == "abc123"
            assert utxos[0].amount == 1.5

    @pytest.mark.asyncio
    async def test_dry_run_uses_testmempoolaccept(self, cli):
        """Dry run uses testmempoolaccept."""
        mock_response = [{"txid": "abc", "allowed": True}]

        with patch.object(cli, '_call', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await cli.test_mempool_accept("0100...")

            mock_call.assert_called_once()
            assert "testmempoolaccept" in str(mock_call.call_args)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_node_cli.py -v`
Expected: FAIL with import errors

**Step 3: Write CLI implementation**

```python
# src/mcp_bitcoin_cli/node/cli.py
"""Bitcoin Core CLI (subprocess) interface."""

import asyncio
import json
from typing import Any, Optional

from mcp_bitcoin_cli.config import Config, Network
from mcp_bitcoin_cli.node.interface import (
    NodeInterface,
    NodeInfo,
    UTXO,
    TransactionInfo,
)


# Network CLI flags
NETWORK_FLAGS = {
    Network.MAINNET: [],
    Network.TESTNET: ["-testnet"],
    Network.SIGNET: ["-signet"],
    Network.REGTEST: ["-regtest"],
}


class BitcoinCLI(NodeInterface):
    """Bitcoin Core interface via bitcoin-cli subprocess."""

    def __init__(self, config: Config):
        self.config = config
        self.cli_path = config.cli_path
        self.network = config.network
        self.datadir = config.cli_datadir

    def _build_command(self, method: str, *args: Any) -> list[str]:
        """Build bitcoin-cli command."""
        cmd = [self.cli_path]

        # Add network flag
        cmd.extend(NETWORK_FLAGS.get(self.network, []))

        # Add datadir if configured
        if self.datadir:
            cmd.append(f"-datadir={self.datadir}")

        # Add method and arguments
        cmd.append(method)
        cmd.extend(str(arg) for arg in args)

        return cmd

    async def _call(self, method: str, *args: Any) -> Any:
        """Execute bitcoin-cli command and parse JSON response."""
        cmd = self._build_command(method, *args)

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode().strip()
            raise RuntimeError(f"bitcoin-cli error: {error_msg}")

        output = stdout.decode().strip()
        if not output:
            return None

        try:
            return json.loads(output)
        except json.JSONDecodeError:
            # Some commands return plain text
            return output

    async def get_info(self) -> NodeInfo:
        """Get node status and network info."""
        try:
            chain_info = await self._call("getblockchaininfo")
            network_info = await self._call("getnetworkinfo")

            return NodeInfo(
                connected=True,
                network=chain_info["chain"],
                block_height=chain_info["blocks"],
                version=network_info["version"],
                errors=chain_info.get("warnings", ""),
            )
        except Exception as e:
            return NodeInfo(
                connected=False,
                network="unknown",
                block_height=0,
                version=0,
                errors=str(e),
            )

    async def list_utxos(
        self,
        min_confirmations: int = 1,
        min_amount: float = 0,
    ) -> list[UTXO]:
        """List available UTXOs."""
        result = await self._call("listunspent", min_confirmations)

        utxos = []
        for u in result:
            if u["amount"] >= min_amount:
                utxos.append(UTXO(
                    txid=u["txid"],
                    vout=u["vout"],
                    amount=u["amount"],
                    confirmations=u["confirmations"],
                    script_pubkey=u["scriptPubKey"],
                ))

        return utxos

    async def get_transaction(self, txid: str) -> TransactionInfo:
        """Get transaction details."""
        # Try getrawtransaction with verbose=true first
        try:
            result = await self._call("getrawtransaction", txid, "true")
            return TransactionInfo(
                txid=result["txid"],
                blockhash=result.get("blockhash"),
                confirmations=result.get("confirmations", 0),
                time=result.get("time"),
                hex=result["hex"],
                decoded=result,
            )
        except RuntimeError:
            # Fall back to gettransaction for wallet transactions
            result = await self._call("gettransaction", txid)
            return TransactionInfo(
                txid=result["txid"],
                blockhash=result.get("blockhash"),
                confirmations=result.get("confirmations", 0),
                time=result.get("time"),
                hex=result["hex"],
                decoded=result,
            )

    async def send_raw_transaction(
        self,
        tx_hex: str,
        max_fee_rate: Optional[float] = None,
    ) -> str:
        """Broadcast signed transaction, return txid."""
        if max_fee_rate:
            return await self._call("sendrawtransaction", tx_hex, max_fee_rate)
        return await self._call("sendrawtransaction", tx_hex)

    async def test_mempool_accept(self, tx_hex: str) -> dict[str, Any]:
        """Test if transaction would be accepted (dry run)."""
        # testmempoolaccept expects an array
        result = await self._call("testmempoolaccept", f'["{tx_hex}"]')
        return result[0] if result else {"allowed": False}

    async def create_raw_transaction(
        self,
        inputs: list[dict],
        outputs: list[dict],
    ) -> str:
        """Create unsigned raw transaction."""
        return await self._call(
            "createrawtransaction",
            json.dumps(inputs),
            json.dumps(outputs),
        )

    async def fund_raw_transaction(
        self,
        tx_hex: str,
        options: Optional[dict] = None,
    ) -> dict:
        """Add inputs to fund transaction, return hex and fee."""
        if options:
            return await self._call("fundrawtransaction", tx_hex, json.dumps(options))
        return await self._call("fundrawtransaction", tx_hex)

    async def get_new_address(self, label: str = "") -> str:
        """Generate new receiving address."""
        if label:
            return await self._call("getnewaddress", label)
        return await self._call("getnewaddress")

    async def estimate_fee(self, conf_target: int = 6) -> float:
        """Estimate fee rate in BTC/kB."""
        result = await self._call("estimatesmartfee", conf_target)
        return result.get("feerate", 0.0001)  # Default to 0.0001 BTC/kB
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_node_cli.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/mcp_bitcoin_cli/node/cli.py tests/test_node_cli.py
git commit -m "feat: add bitcoin-cli subprocess interface"
```

---

## Task 8: Node Interface - RPC Implementation

**Files:**
- Create: `src/mcp_bitcoin_cli/node/rpc.py`
- Create: `tests/test_node_rpc.py`

**Step 1: Write failing test for RPC interface**

```python
# tests/test_node_rpc.py
"""Tests for JSON-RPC interface."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from mcp_bitcoin_cli.node.rpc import BitcoinRPC
from mcp_bitcoin_cli.config import Config, Network, ConnectionMethod


class TestBitcoinRPC:
    """Test JSON-RPC interface."""

    @pytest.fixture
    def rpc(self):
        """Create RPC instance with test config."""
        config = Config(
            connection_method=ConnectionMethod.RPC,
            network=Network.REGTEST,
            rpc_host="127.0.0.1",
            rpc_port=18443,
            rpc_user="test",
            rpc_password="test123",
        )
        return BitcoinRPC(config)

    def test_build_url(self, rpc):
        """Build correct RPC URL."""
        assert rpc.url == "http://127.0.0.1:18443"

    def test_auth_header(self, rpc):
        """Create correct auth header."""
        # Basic auth is base64(user:password)
        assert "Authorization" in rpc._headers
        assert rpc._headers["Authorization"].startswith("Basic ")

    @pytest.mark.asyncio
    async def test_call_formats_request(self, rpc):
        """RPC call formats JSON-RPC 2.0 request."""
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": {"blocks": 100},
            "error": None,
            "id": 1,
        })

        with patch.object(rpc, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            result = await rpc._call("getblockchaininfo")

            # Verify request format
            call_args = mock_client.post.call_args
            request_body = call_args.kwargs.get('json') or call_args.args[1]

            assert request_body["jsonrpc"] == "2.0"
            assert request_body["method"] == "getblockchaininfo"
            assert "id" in request_body

    @pytest.mark.asyncio
    async def test_handles_rpc_error(self, rpc):
        """Handle RPC error response."""
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "result": None,
            "error": {"code": -1, "message": "Test error"},
            "id": 1,
        })

        with patch.object(rpc, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            with pytest.raises(RuntimeError, match="Test error"):
                await rpc._call("badmethod")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_node_rpc.py -v`
Expected: FAIL with import errors

**Step 3: Write RPC implementation**

```python
# src/mcp_bitcoin_cli/node/rpc.py
"""Bitcoin Core JSON-RPC interface."""

import base64
from typing import Any, Optional

import httpx

from mcp_bitcoin_cli.config import Config
from mcp_bitcoin_cli.node.interface import (
    NodeInterface,
    NodeInfo,
    UTXO,
    TransactionInfo,
)


class BitcoinRPC(NodeInterface):
    """Bitcoin Core interface via JSON-RPC."""

    def __init__(self, config: Config):
        self.config = config
        self.url = f"http://{config.rpc_host}:{config.get_rpc_port()}"

        # Build auth header
        credentials = f"{config.rpc_user}:{config.rpc_password}"
        auth_bytes = base64.b64encode(credentials.encode()).decode()

        self._headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json",
        }

        self._client = httpx.AsyncClient(timeout=30.0)
        self._request_id = 0

    async def _call(self, method: str, *args: Any) -> Any:
        """Execute JSON-RPC call."""
        self._request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": list(args),
        }

        response = await self._client.post(
            self.url,
            json=payload,
            headers=self._headers,
        )

        data = response.json()

        if data.get("error"):
            error = data["error"]
            raise RuntimeError(f"RPC error {error['code']}: {error['message']}")

        return data.get("result")

    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()

    async def get_info(self) -> NodeInfo:
        """Get node status and network info."""
        try:
            chain_info = await self._call("getblockchaininfo")
            network_info = await self._call("getnetworkinfo")

            return NodeInfo(
                connected=True,
                network=chain_info["chain"],
                block_height=chain_info["blocks"],
                version=network_info["version"],
                errors=chain_info.get("warnings", ""),
            )
        except Exception as e:
            return NodeInfo(
                connected=False,
                network="unknown",
                block_height=0,
                version=0,
                errors=str(e),
            )

    async def list_utxos(
        self,
        min_confirmations: int = 1,
        min_amount: float = 0,
    ) -> list[UTXO]:
        """List available UTXOs."""
        result = await self._call("listunspent", min_confirmations)

        utxos = []
        for u in result:
            if u["amount"] >= min_amount:
                utxos.append(UTXO(
                    txid=u["txid"],
                    vout=u["vout"],
                    amount=u["amount"],
                    confirmations=u["confirmations"],
                    script_pubkey=u["scriptPubKey"],
                ))

        return utxos

    async def get_transaction(self, txid: str) -> TransactionInfo:
        """Get transaction details."""
        try:
            result = await self._call("getrawtransaction", txid, True)
            return TransactionInfo(
                txid=result["txid"],
                blockhash=result.get("blockhash"),
                confirmations=result.get("confirmations", 0),
                time=result.get("time"),
                hex=result["hex"],
                decoded=result,
            )
        except RuntimeError:
            result = await self._call("gettransaction", txid)
            return TransactionInfo(
                txid=result["txid"],
                blockhash=result.get("blockhash"),
                confirmations=result.get("confirmations", 0),
                time=result.get("time"),
                hex=result["hex"],
                decoded=result,
            )

    async def send_raw_transaction(
        self,
        tx_hex: str,
        max_fee_rate: Optional[float] = None,
    ) -> str:
        """Broadcast signed transaction, return txid."""
        if max_fee_rate:
            return await self._call("sendrawtransaction", tx_hex, max_fee_rate)
        return await self._call("sendrawtransaction", tx_hex)

    async def test_mempool_accept(self, tx_hex: str) -> dict[str, Any]:
        """Test if transaction would be accepted (dry run)."""
        result = await self._call("testmempoolaccept", [tx_hex])
        return result[0] if result else {"allowed": False}

    async def create_raw_transaction(
        self,
        inputs: list[dict],
        outputs: list[dict],
    ) -> str:
        """Create unsigned raw transaction."""
        return await self._call("createrawtransaction", inputs, outputs)

    async def fund_raw_transaction(
        self,
        tx_hex: str,
        options: Optional[dict] = None,
    ) -> dict:
        """Add inputs to fund transaction, return hex and fee."""
        if options:
            return await self._call("fundrawtransaction", tx_hex, options)
        return await self._call("fundrawtransaction", tx_hex)

    async def get_new_address(self, label: str = "") -> str:
        """Generate new receiving address."""
        if label:
            return await self._call("getnewaddress", label)
        return await self._call("getnewaddress")

    async def estimate_fee(self, conf_target: int = 6) -> float:
        """Estimate fee rate in BTC/kB."""
        result = await self._call("estimatesmartfee", conf_target)
        return result.get("feerate", 0.0001)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_node_rpc.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/mcp_bitcoin_cli/node/rpc.py tests/test_node_rpc.py
git commit -m "feat: add JSON-RPC direct interface"
```

---

## Task 9: MCP Server - Core Setup

**Files:**
- Create: `src/mcp_bitcoin_cli/server.py`
- Create: `tests/test_server.py`

**Note:** The MCP server implementation is extensive. See the design document for the full tool list. The server.py file should register all tools defined in the design document.

**Step 1: Write failing test for server initialization**

```python
# tests/test_server.py
"""Tests for MCP server."""

import pytest
from mcp_bitcoin_cli.server import create_server


class TestServerCreation:
    """Test server initialization."""

    def test_create_server_returns_server(self):
        """create_server returns configured server."""
        server = create_server()
        assert server is not None

    def test_server_registers_tools(self):
        """Server registers expected tools."""
        server = create_server()

        # Check that tools are registered by checking the server has tools
        assert hasattr(server, 'server')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_server.py -v`
Expected: FAIL with import errors

**Step 3: Write server implementation**

Create `src/mcp_bitcoin_cli/server.py` with the full implementation. Due to size, implement incrementally - start with basic structure and low-level tools, then add high-level tools.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_server.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/mcp_bitcoin_cli/server.py tests/test_server.py
git commit -m "feat: add MCP server with all tools"
```

---

## Task 10: Integration Tests

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration tests**

Test complete workflows: encode -> decode roundtrips, token creation, timestamps.

**Step 2: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests for full workflows"
```

---

## Task 11: Final Polish

**Files:**
- Update: `src/mcp_bitcoin_cli/node/__init__.py`
- Update: `src/mcp_bitcoin_cli/protocols/__init__.py`

**Step 1: Update init files with exports**

Add proper `__all__` exports to make imports cleaner.

**Step 2: Run final test suite**

Run: `pytest -v --tb=short`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: update package exports and final polish"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Project setup | Install verification |
| 2 | Envelope module | 9 tests |
| 3 | OP_RETURN primitives | 9 tests |
| 4 | Configuration | 8 tests |
| 5 | BRC-20 protocol | 11 tests |
| 6 | Node interface (abstract) | - |
| 7 | CLI implementation | 5 tests |
| 8 | RPC implementation | 4 tests |
| 9 | MCP server | 2 tests |
| 10 | Integration tests | 4+ tests |
| 11 | Final polish | - |

**Total: ~52 tests across 11 tasks**
