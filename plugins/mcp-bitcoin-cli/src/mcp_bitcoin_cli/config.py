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
