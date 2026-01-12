"""Bitcoin Core JSON-RPC interface."""

import base64
from typing import Any, Optional

import httpx

from mcp_bitcoin_cli.config import Config
from mcp_bitcoin_cli.node.interface import (
    NodeInterface,
    NodeInfo,
    UTXO,
    TransactionInfo,
)


class BitcoinRPC(NodeInterface):
    """Bitcoin Core interface via JSON-RPC."""

    def __init__(self, config: Config):
        self.config = config
        self.url = f"http://{config.rpc_host}:{config.get_rpc_port()}"

        # Build auth header
        credentials = f"{config.rpc_user}:{config.rpc_password}"
        auth_bytes = base64.b64encode(credentials.encode()).decode()

        self._headers = {
            "Authorization": f"Basic {auth_bytes}",
            "Content-Type": "application/json",
        }

        self._client = httpx.AsyncClient(timeout=30.0)
        self._request_id = 0

    async def _call(self, method: str, *args: Any) -> Any:
        """Execute JSON-RPC call."""
        self._request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": list(args),
        }

        response = await self._client.post(
            self.url,
            json=payload,
            headers=self._headers,
        )

        data = response.json()

        if data.get("error"):
            error = data["error"]
            raise RuntimeError(f"RPC error {error['code']}: {error['message']}")

        return data.get("result")

    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()

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
        try:
            result = await self._call("getrawtransaction", txid, True)
            return TransactionInfo(
                txid=result["txid"],
                blockhash=result.get("blockhash"),
                confirmations=result.get("confirmations", 0),
                time=result.get("time"),
                hex=result["hex"],
                decoded=result,
            )
        except RuntimeError:
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
        result = await self._call("testmempoolaccept", [tx_hex])
        return result[0] if result else {"allowed": False}

    async def create_raw_transaction(
        self,
        inputs: list[dict],
        outputs: list[dict],
    ) -> str:
        """Create unsigned raw transaction."""
        return await self._call("createrawtransaction", inputs, outputs)

    async def fund_raw_transaction(
        self,
        tx_hex: str,
        options: Optional[dict] = None,
    ) -> dict:
        """Add inputs to fund transaction, return hex and fee."""
        if options:
            return await self._call("fundrawtransaction", tx_hex, options)
        return await self._call("fundrawtransaction", tx_hex)

    async def get_new_address(self, label: str = "") -> str:
        """Generate new receiving address."""
        if label:
            return await self._call("getnewaddress", label)
        return await self._call("getnewaddress")

    async def estimate_fee(self, conf_target: int = 6) -> float:
        """Estimate fee rate in BTC/kB."""
        result = await self._call("estimatesmartfee", conf_target)
        return result.get("feerate", 0.0001)
