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
        result = await self._call("testmempoolaccept", json.dumps([tx_hex]))
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
