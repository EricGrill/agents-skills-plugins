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
