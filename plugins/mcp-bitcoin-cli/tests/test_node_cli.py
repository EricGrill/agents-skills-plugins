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
