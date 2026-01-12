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
