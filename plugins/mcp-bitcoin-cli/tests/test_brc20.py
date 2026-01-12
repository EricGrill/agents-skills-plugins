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
