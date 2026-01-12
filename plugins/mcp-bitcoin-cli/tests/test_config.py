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
