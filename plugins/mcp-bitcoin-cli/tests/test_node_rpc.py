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
        mock_response.json.return_value = {
            "result": {"blocks": 100},
            "error": None,
            "id": 1,
        }

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
        mock_response.json.return_value = {
            "result": None,
            "error": {"code": -1, "message": "Test error"},
            "id": 1,
        }

        with patch.object(rpc, '_client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)

            with pytest.raises(RuntimeError, match="Test error"):
                await rpc._call("badmethod")
