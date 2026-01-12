"""MCP server for Bitcoin OP_RETURN data operations."""

__version__ = "0.1.0"

# Server entry points
from mcp_bitcoin_cli.server import create_server, main

# Configuration
from mcp_bitcoin_cli.config import Config, Network, ConnectionMethod

# Envelope encoding/decoding
from mcp_bitcoin_cli.envelope import (
    encode_envelope,
    decode_envelope,
    Envelope,
    EnvelopeType,
)

# OP_RETURN primitives
from mcp_bitcoin_cli.primitives import (
    encode_op_return_script,
    decode_op_return_script,
)

__all__ = [
    # Version
    "__version__",
    # Server
    "create_server",
    "main",
    # Config
    "Config",
    "Network",
    "ConnectionMethod",
    # Envelope
    "encode_envelope",
    "decode_envelope",
    "Envelope",
    "EnvelopeType",
    # Primitives
    "encode_op_return_script",
    "decode_op_return_script",
]
