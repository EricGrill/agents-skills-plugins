"""Bitcoin Core node communication interfaces."""

from mcp_bitcoin_cli.node.interface import (
    NodeInterface,
    NodeInfo,
    UTXO,
    TransactionInfo,
)
from mcp_bitcoin_cli.node.cli import BitcoinCLI
from mcp_bitcoin_cli.node.rpc import BitcoinRPC

__all__ = [
    "NodeInterface",
    "NodeInfo",
    "UTXO",
    "TransactionInfo",
    "BitcoinCLI",
    "BitcoinRPC",
]
