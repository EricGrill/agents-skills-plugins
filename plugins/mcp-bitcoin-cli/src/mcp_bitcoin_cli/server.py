"""MCP server for Bitcoin OP_RETURN data operations.

This server exposes tools for working with Bitcoin OP_RETURN data,
including low-level primitives, Bitcoin Core interface, token operations,
document storage, and timestamping.
"""

import hashlib
from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_bitcoin_cli.config import Config, ConnectionMethod, load_config
from mcp_bitcoin_cli.envelope import (
    EnvelopeType,
    decode_envelope,
    encode_envelope,
)
from mcp_bitcoin_cli.node.cli import BitcoinCLI
from mcp_bitcoin_cli.node.interface import NodeInterface
from mcp_bitcoin_cli.node.rpc import BitcoinRPC
from mcp_bitcoin_cli.primitives import decode_op_return_script, encode_op_return_script
from mcp_bitcoin_cli.protocols.brc20 import BRC20Deploy, BRC20Mint, BRC20Transfer


def create_server(config: Optional[Config] = None) -> FastMCP:
    """Create and configure the MCP server with all tools.

    Args:
        config: Optional configuration. If not provided, uses defaults.

    Returns:
        Configured FastMCP server instance.
    """
    if config is None:
        config = Config()

    mcp = FastMCP("mcp-bitcoin-cli")

    # Store config on server for access by tools
    mcp._config = config
    mcp._node: Optional[NodeInterface] = None

    def get_node() -> NodeInterface:
        """Get or create the node interface."""
        if mcp._node is None:
            if config.connection_method == ConnectionMethod.CLI:
                mcp._node = BitcoinCLI(config)
            else:
                mcp._node = BitcoinRPC(config)
        return mcp._node

    # =========================================================================
    # Low-Level Primitives (offline-capable)
    # =========================================================================

    @mcp.tool()
    def encode_op_return(data: str, encoding: str = "utf-8") -> dict:
        """Encode arbitrary data into OP_RETURN script format.

        Args:
            data: Data to encode (string)
            encoding: Encoding for the data ('utf-8', 'hex'). Default: 'utf-8'

        Returns:
            Dictionary with 'script_hex' containing the OP_RETURN script.
        """
        if encoding == "hex":
            try:
                data_bytes = bytes.fromhex(data)
            except ValueError as e:
                return {"error": f"Invalid hex string: {e}"}
        else:
            data_bytes = data.encode(encoding)

        script = encode_op_return_script(data_bytes)
        return {"script_hex": script.hex()}

    @mcp.tool()
    def decode_op_return(script_hex: str) -> dict:
        """Parse OP_RETURN data from script hex.

        Args:
            script_hex: OP_RETURN script as hex string

        Returns:
            Dictionary with 'data_hex' and 'data_utf8' (if decodable).
        """
        try:
            script = bytes.fromhex(script_hex)
        except ValueError as e:
            return {"error": f"Invalid hex string: {e}"}

        data = decode_op_return_script(script)

        result = {"data_hex": data.hex()}

        try:
            result["data_utf8"] = data.decode("utf-8")
        except UnicodeDecodeError:
            result["data_utf8"] = None

        return result

    @mcp.tool()
    def build_op_return_transaction(
        data: str,
        encoding: str = "utf-8",
        use_envelope: bool = True,
        envelope_type: str = "raw",
    ) -> dict:
        """Construct OP_RETURN output data for a transaction.

        This prepares the data for inclusion in a transaction but does not
        create or broadcast the transaction itself.

        Args:
            data: Data to embed
            encoding: Data encoding ('utf-8' or 'hex')
            use_envelope: Whether to wrap in BTCD envelope format
            envelope_type: Envelope type if use_envelope is True
                ('raw', 'text', 'json', 'hash', 'token', 'file')

        Returns:
            Dictionary with 'script_hex' for the OP_RETURN output.
        """
        if encoding == "hex":
            try:
                data_bytes = bytes.fromhex(data)
            except ValueError as e:
                return {"error": f"Invalid hex string: {e}"}
        else:
            data_bytes = data.encode(encoding)

        if use_envelope:
            type_map = {
                "raw": EnvelopeType.RAW,
                "text": EnvelopeType.TEXT,
                "json": EnvelopeType.JSON,
                "hash": EnvelopeType.HASH,
                "token": EnvelopeType.TOKEN,
                "file": EnvelopeType.FILE,
            }
            env_type = type_map.get(envelope_type.lower(), EnvelopeType.RAW)
            data_bytes = encode_envelope(data_bytes, env_type)

        script = encode_op_return_script(data_bytes)
        return {
            "script_hex": script.hex(),
            "data_size": len(data_bytes),
            "uses_envelope": use_envelope,
        }

    @mcp.tool()
    def parse_envelope(data_hex: str) -> dict:
        """Parse BTCD envelope structure from raw bytes.

        Args:
            data_hex: Hex-encoded envelope data

        Returns:
            Dictionary with envelope fields: magic, version, type, payload_hex.
        """
        try:
            data = bytes.fromhex(data_hex)
        except ValueError as e:
            return {"error": f"Invalid hex string: {e}"}

        envelope = decode_envelope(data)

        # Handle both EnvelopeType enum and raw int for custom types
        if isinstance(envelope.type, EnvelopeType):
            type_name = envelope.type.name
            type_value = envelope.type.value
        else:
            # Custom type stored as raw int
            type_name = f"CUSTOM_{envelope.type:#x}"
            type_value = envelope.type

        result = {
            "magic": envelope.magic.decode("ascii"),
            "version": envelope.version,
            "type": type_name,
            "type_value": type_value,
            "payload_hex": envelope.payload.hex(),
        }

        try:
            result["payload_utf8"] = envelope.payload.decode("utf-8")
        except UnicodeDecodeError:
            result["payload_utf8"] = None

        return result

    # =========================================================================
    # Bitcoin Core Interface
    # =========================================================================

    @mcp.tool()
    async def get_node_info() -> dict:
        """Check connection and network status.

        Returns:
            Dictionary with node information including connection status,
            network, block height, and version.
        """
        node = get_node()
        info = await node.get_info()
        return {
            "connected": info.connected,
            "network": info.network,
            "block_height": info.block_height,
            "version": info.version,
            "errors": info.errors if info.errors else None,
        }

    @mcp.tool()
    async def list_utxos(
        min_confirmations: int = 1,
        min_amount: float = 0.0,
    ) -> dict:
        """List available UTXOs for funding transactions.

        Args:
            min_confirmations: Minimum confirmations required (default: 1)
            min_amount: Minimum UTXO amount in BTC (default: 0.0)

        Returns:
            Dictionary with list of UTXOs.
        """
        node = get_node()
        utxos = await node.list_utxos(min_confirmations, min_amount)

        return {
            "count": len(utxos),
            "utxos": [
                {
                    "txid": u.txid,
                    "vout": u.vout,
                    "amount": u.amount,
                    "confirmations": u.confirmations,
                }
                for u in utxos
            ],
        }

    @mcp.tool()
    async def broadcast_transaction(
        tx_hex: str,
        dry_run: bool = True,
        max_fee_rate: Optional[float] = None,
    ) -> dict:
        """Send signed transaction to the network.

        Args:
            tx_hex: Signed transaction as hex string
            dry_run: If True, only test without broadcasting (default: True)
            max_fee_rate: Maximum fee rate in BTC/kB (optional)

        Returns:
            Dictionary with result. For dry_run, includes 'allowed' status.
            For actual broadcast, includes 'txid'.
        """
        node = get_node()

        if dry_run:
            result = await node.test_mempool_accept(tx_hex)
            return {
                "dry_run": True,
                "allowed": result.get("allowed", False),
                "reject_reason": result.get("reject-reason"),
            }
        else:
            txid = await node.send_raw_transaction(tx_hex, max_fee_rate)
            return {
                "dry_run": False,
                "txid": txid,
                "broadcast": True,
            }

    @mcp.tool()
    async def get_transaction(txid: str) -> dict:
        """Fetch transaction details.

        Args:
            txid: Transaction ID (hash)

        Returns:
            Dictionary with transaction details.
        """
        node = get_node()
        tx = await node.get_transaction(txid)

        return {
            "txid": tx.txid,
            "blockhash": tx.blockhash,
            "confirmations": tx.confirmations,
            "time": tx.time,
            "hex": tx.hex,
        }

    @mcp.tool()
    async def search_op_returns(
        start_height: int,
        end_height: Optional[int] = None,
        limit: int = 100,
    ) -> dict:
        """Scan blocks for OP_RETURN transactions.

        Note: This is a placeholder that will require additional implementation
        for block scanning. Currently returns an error indicating the feature
        requires direct block access.

        Args:
            start_height: Starting block height
            end_height: Ending block height (optional, defaults to start_height)
            limit: Maximum number of results (default: 100)

        Returns:
            Dictionary with found OP_RETURN transactions.
        """
        # This would require block iteration which is expensive
        # For now, return a placeholder indicating this needs more work
        return {
            "error": "Block scanning not yet implemented",
            "start_height": start_height,
            "end_height": end_height or start_height,
            "limit": limit,
            "results": [],
        }

    # =========================================================================
    # Token Operations (BRC-20 Template)
    # =========================================================================

    @mcp.tool()
    def create_token_deploy(
        tick: str,
        max_supply: int,
        mint_limit: Optional[int] = None,
        decimals: int = 18,
    ) -> dict:
        """Create a BRC-20 token deployment inscription.

        Args:
            tick: Token ticker (exactly 4 characters)
            max_supply: Maximum token supply
            mint_limit: Maximum amount per mint (optional)
            decimals: Token decimals (default: 18)

        Returns:
            Dictionary with inscription data in various formats.
        """
        deploy = BRC20Deploy(
            tick=tick,
            max_supply=max_supply,
            mint_limit=mint_limit,
            decimals=decimals,
        )

        envelope_bytes = deploy.to_envelope()
        script = encode_op_return_script(envelope_bytes)

        return {
            "operation": "deploy",
            "tick": tick,
            "max_supply": max_supply,
            "mint_limit": mint_limit,
            "decimals": decimals,
            "json": deploy.to_json(),
            "envelope_hex": envelope_bytes.hex(),
            "script_hex": script.hex(),
        }

    @mcp.tool()
    def create_token_mint(tick: str, amount: int) -> dict:
        """Create a BRC-20 token mint inscription.

        Args:
            tick: Token ticker (exactly 4 characters)
            amount: Amount to mint

        Returns:
            Dictionary with inscription data in various formats.
        """
        mint = BRC20Mint(tick=tick, amount=amount)

        envelope_bytes = mint.to_envelope()
        script = encode_op_return_script(envelope_bytes)

        return {
            "operation": "mint",
            "tick": tick,
            "amount": amount,
            "json": mint.to_json(),
            "envelope_hex": envelope_bytes.hex(),
            "script_hex": script.hex(),
        }

    @mcp.tool()
    def create_token_transfer(tick: str, amount: int) -> dict:
        """Create a BRC-20 token transfer inscription.

        Args:
            tick: Token ticker (exactly 4 characters)
            amount: Amount to transfer

        Returns:
            Dictionary with inscription data in various formats.
        """
        transfer = BRC20Transfer(tick=tick, amount=amount)

        envelope_bytes = transfer.to_envelope()
        script = encode_op_return_script(envelope_bytes)

        return {
            "operation": "transfer",
            "tick": tick,
            "amount": amount,
            "json": transfer.to_json(),
            "envelope_hex": envelope_bytes.hex(),
            "script_hex": script.hex(),
        }

    # =========================================================================
    # Document Storage
    # =========================================================================

    @mcp.tool()
    def embed_document(
        content: str,
        content_type: str = "text/plain",
        encoding: str = "utf-8",
    ) -> dict:
        """Prepare a document for on-chain storage.

        Args:
            content: Document content
            content_type: MIME type of the content (default: 'text/plain')
            encoding: Content encoding ('utf-8' or 'hex')

        Returns:
            Dictionary with prepared document data for embedding.
        """
        if encoding == "hex":
            try:
                content_bytes = bytes.fromhex(content)
            except ValueError as e:
                return {"error": f"Invalid hex string: {e}"}
        else:
            content_bytes = content.encode(encoding)

        # For file type, prepend content-type header
        if content_type != "text/plain":
            header = f"{content_type}\n".encode("utf-8")
            payload = header + content_bytes
            envelope_type = EnvelopeType.FILE
        else:
            payload = content_bytes
            envelope_type = EnvelopeType.TEXT

        envelope_bytes = encode_envelope(payload, envelope_type)
        script = encode_op_return_script(envelope_bytes)

        return {
            "content_type": content_type,
            "content_size": len(content_bytes),
            "envelope_size": len(envelope_bytes),
            "envelope_hex": envelope_bytes.hex(),
            "script_hex": script.hex(),
        }

    @mcp.tool()
    def read_document(data_hex: str) -> dict:
        """Retrieve and parse document from transaction data.

        Args:
            data_hex: Hex-encoded document data (from OP_RETURN)

        Returns:
            Dictionary with parsed document content.
        """
        try:
            data = bytes.fromhex(data_hex)
        except ValueError as e:
            return {"error": f"Invalid hex string: {e}"}

        # Try to decode as envelope first
        try:
            envelope = decode_envelope(data)
            payload = envelope.payload

            if envelope.type == EnvelopeType.FILE:
                # Parse content-type header
                if b"\n" in payload:
                    header, content = payload.split(b"\n", 1)
                    content_type = header.decode("utf-8")
                else:
                    content_type = "application/octet-stream"
                    content = payload
            elif envelope.type == EnvelopeType.TEXT:
                content_type = "text/plain"
                content = payload
            elif envelope.type == EnvelopeType.JSON:
                content_type = "application/json"
                content = payload
            else:
                content_type = "application/octet-stream"
                content = payload

            # Handle both EnvelopeType enum and raw int for custom types
            if isinstance(envelope.type, EnvelopeType):
                envelope_type_name = envelope.type.name
            else:
                # Custom type stored as raw int
                envelope_type_name = f"CUSTOM_{envelope.type:#x}"

            result = {
                "is_envelope": True,
                "envelope_type": envelope_type_name,
                "content_type": content_type,
                "content_hex": content.hex(),
            }

            try:
                result["content_utf8"] = content.decode("utf-8")
            except UnicodeDecodeError:
                result["content_utf8"] = None

            return result

        except ValueError:
            # Not an envelope, return raw data
            result = {
                "is_envelope": False,
                "content_hex": data.hex(),
            }

            try:
                result["content_utf8"] = data.decode("utf-8")
            except UnicodeDecodeError:
                result["content_utf8"] = None

            return result

    # =========================================================================
    # Timestamping & Attestation
    # =========================================================================

    @mcp.tool()
    def create_timestamp(
        data: str,
        encoding: str = "utf-8",
        hash_algorithm: str = "sha256",
    ) -> dict:
        """Create a hash commitment for timestamping.

        Args:
            data: Data to timestamp
            encoding: Data encoding ('utf-8' or 'hex')
            hash_algorithm: Hash algorithm to use ('sha256', 'sha3_256')

        Returns:
            Dictionary with hash and prepared script for embedding.
        """
        if encoding == "hex":
            try:
                data_bytes = bytes.fromhex(data)
            except ValueError as e:
                return {"error": f"Invalid hex string: {e}"}
        else:
            data_bytes = data.encode(encoding)

        if hash_algorithm == "sha3_256":
            hash_bytes = hashlib.sha3_256(data_bytes).digest()
        else:
            hash_bytes = hashlib.sha256(data_bytes).digest()

        envelope_bytes = encode_envelope(hash_bytes, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)

        return {
            "hash_algorithm": hash_algorithm,
            "hash_hex": hash_bytes.hex(),
            "data_size": len(data_bytes),
            "envelope_hex": envelope_bytes.hex(),
            "script_hex": script.hex(),
        }

    @mcp.tool()
    def verify_timestamp(
        data: str,
        expected_hash: str,
        encoding: str = "utf-8",
        hash_algorithm: str = "sha256",
    ) -> dict:
        """Verify data against an on-chain timestamp hash.

        Args:
            data: Original data to verify
            expected_hash: Expected hash value (hex)
            encoding: Data encoding ('utf-8' or 'hex')
            hash_algorithm: Hash algorithm used ('sha256', 'sha3_256')

        Returns:
            Dictionary with verification result.
        """
        if encoding == "hex":
            try:
                data_bytes = bytes.fromhex(data)
            except ValueError as e:
                return {"error": f"Invalid hex string for data: {e}"}
        else:
            data_bytes = data.encode(encoding)

        if hash_algorithm == "sha3_256":
            computed_hash = hashlib.sha3_256(data_bytes).digest()
        else:
            computed_hash = hashlib.sha256(data_bytes).digest()

        try:
            expected_bytes = bytes.fromhex(expected_hash)
        except ValueError as e:
            return {"error": f"Invalid hex string for expected_hash: {e}"}

        match = computed_hash == expected_bytes

        return {
            "verified": match,
            "hash_algorithm": hash_algorithm,
            "computed_hash": computed_hash.hex(),
            "expected_hash": expected_hash,
        }

    return mcp


def main():
    """Entry point for the MCP server."""
    from pathlib import Path

    # Try to load config from standard locations
    config_paths = [
        Path("mcp-bitcoin-cli.toml"),
        Path.home() / ".config" / "mcp-bitcoin-cli" / "config.toml",
    ]

    config = None
    for path in config_paths:
        if path.exists():
            config = load_config(path)
            break

    if config is None:
        config = Config()

    server = create_server(config)
    server.run()


if __name__ == "__main__":
    main()
