"""Tests for MCP server."""

import json
import pytest
from mcp_bitcoin_cli.server import create_server


class TestServerCreation:
    """Test server initialization."""

    def test_create_server_returns_server(self):
        """create_server returns configured server."""
        server = create_server()
        assert server is not None

    def test_server_registers_tools(self):
        """Server registers expected tools."""
        server = create_server()

        # Check that tools are registered by checking the server has a tool manager
        assert hasattr(server, '_tool_manager')

    @pytest.mark.asyncio
    async def test_server_has_expected_tools(self):
        """Server registers all expected tools."""
        server = create_server()

        # Get list of registered tools
        tools = await server.list_tools()
        tool_names = {tool.name for tool in tools}

        # Low-level primitives
        assert "encode_op_return" in tool_names
        assert "decode_op_return" in tool_names
        assert "build_op_return_transaction" in tool_names
        assert "parse_envelope" in tool_names

        # Bitcoin Core interface
        assert "get_node_info" in tool_names
        assert "list_utxos" in tool_names
        assert "broadcast_transaction" in tool_names
        assert "get_transaction" in tool_names
        assert "search_op_returns" in tool_names

        # Token operations
        assert "create_token_deploy" in tool_names
        assert "create_token_mint" in tool_names
        assert "create_token_transfer" in tool_names

        # Document storage
        assert "embed_document" in tool_names
        assert "read_document" in tool_names

        # Timestamping
        assert "create_timestamp" in tool_names
        assert "verify_timestamp" in tool_names

    @pytest.mark.asyncio
    async def test_server_tool_count(self):
        """Server has expected number of tools."""
        server = create_server()

        tools = await server.list_tools()
        # 16 tools total:
        # 4 low-level primitives + 5 bitcoin core + 3 token + 2 document + 2 timestamp
        assert len(tools) == 16


class TestOpReturnTools:
    """Test encode_op_return and decode_op_return tools."""

    @pytest.fixture
    def server(self):
        """Create a fresh server for each test."""
        return create_server()

    @pytest.mark.asyncio
    async def test_encode_decode_roundtrip_utf8(self, server):
        """encode_op_return and decode_op_return roundtrip works for UTF-8 data."""
        # Access the tool functions directly from server
        encode_fn = server._tool_manager._tools["encode_op_return"].fn
        decode_fn = server._tool_manager._tools["decode_op_return"].fn

        # Encode some text
        test_data = "Hello, Bitcoin!"
        encoded = encode_fn(test_data, "utf-8")

        assert "script_hex" in encoded
        assert "error" not in encoded

        # Decode it back
        decoded = decode_fn(encoded["script_hex"])

        assert "data_hex" in decoded
        assert "data_utf8" in decoded
        assert decoded["data_utf8"] == test_data

    @pytest.mark.asyncio
    async def test_encode_decode_roundtrip_hex(self, server):
        """encode_op_return and decode_op_return roundtrip works for hex data."""
        encode_fn = server._tool_manager._tools["encode_op_return"].fn
        decode_fn = server._tool_manager._tools["decode_op_return"].fn

        # Encode some hex data
        test_data = "deadbeef"
        encoded = encode_fn(test_data, "hex")

        assert "script_hex" in encoded
        assert "error" not in encoded

        # Decode it back
        decoded = decode_fn(encoded["script_hex"])

        assert decoded["data_hex"] == test_data

    @pytest.mark.asyncio
    async def test_encode_op_return_invalid_hex(self, server):
        """encode_op_return returns error for invalid hex input."""
        encode_fn = server._tool_manager._tools["encode_op_return"].fn

        result = encode_fn("not_valid_hex", "hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]

    @pytest.mark.asyncio
    async def test_decode_op_return_invalid_hex(self, server):
        """decode_op_return returns error for invalid hex input."""
        decode_fn = server._tool_manager._tools["decode_op_return"].fn

        result = decode_fn("not_valid_hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]


class TestBuildOpReturnTransaction:
    """Test build_op_return_transaction tool."""

    @pytest.fixture
    def server(self):
        """Create a fresh server for each test."""
        return create_server()

    @pytest.mark.asyncio
    async def test_build_with_envelope(self, server):
        """build_op_return_transaction wraps data in envelope format."""
        build_fn = server._tool_manager._tools["build_op_return_transaction"].fn

        result = build_fn("Hello", "utf-8", use_envelope=True, envelope_type="text")

        assert "script_hex" in result
        assert "data_size" in result
        assert result["uses_envelope"] is True
        # BTCD magic bytes should be in the script
        assert "42544344" in result["script_hex"]  # "BTCD" in hex

    @pytest.mark.asyncio
    async def test_build_without_envelope(self, server):
        """build_op_return_transaction works without envelope."""
        build_fn = server._tool_manager._tools["build_op_return_transaction"].fn

        result = build_fn("Hello", "utf-8", use_envelope=False)

        assert "script_hex" in result
        assert result["uses_envelope"] is False
        # Raw "Hello" should be in the script
        assert "48656c6c6f" in result["script_hex"]  # "Hello" in hex

    @pytest.mark.asyncio
    async def test_build_op_return_invalid_hex(self, server):
        """build_op_return_transaction returns error for invalid hex input."""
        build_fn = server._tool_manager._tools["build_op_return_transaction"].fn

        result = build_fn("invalid_hex", "hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]


class TestParseEnvelope:
    """Test parse_envelope tool."""

    @pytest.fixture
    def server(self):
        """Create a fresh server for each test."""
        return create_server()

    @pytest.mark.asyncio
    async def test_parse_valid_envelope(self, server):
        """parse_envelope correctly parses a valid envelope."""
        build_fn = server._tool_manager._tools["build_op_return_transaction"].fn
        parse_fn = server._tool_manager._tools["parse_envelope"].fn
        decode_fn = server._tool_manager._tools["decode_op_return"].fn

        # First build an envelope
        built = build_fn("TestPayload", "utf-8", use_envelope=True, envelope_type="text")

        # Get the envelope data (strip OP_RETURN prefix)
        script_hex = built["script_hex"]
        decoded = decode_fn(script_hex)
        envelope_hex = decoded["data_hex"]

        # Parse the envelope
        parsed = parse_fn(envelope_hex)

        assert parsed["magic"] == "BTCD"
        assert parsed["version"] == 1
        assert parsed["type"] == "TEXT"
        assert parsed["type_value"] == 1
        assert parsed["payload_utf8"] == "TestPayload"

    @pytest.mark.asyncio
    async def test_parse_envelope_invalid_hex(self, server):
        """parse_envelope returns error for invalid hex input."""
        parse_fn = server._tool_manager._tools["parse_envelope"].fn

        result = parse_fn("not_valid_hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]


class TestTokenOperations:
    """Test BRC-20 token operation tools."""

    @pytest.fixture
    def server(self):
        """Create a fresh server for each test."""
        return create_server()

    @pytest.mark.asyncio
    async def test_create_token_deploy(self, server):
        """create_token_deploy produces valid deployment data."""
        deploy_fn = server._tool_manager._tools["create_token_deploy"].fn

        result = deploy_fn(tick="TEST", max_supply=21000000, mint_limit=1000, decimals=8)

        assert result["operation"] == "deploy"
        assert result["tick"] == "TEST"
        assert result["max_supply"] == 21000000
        assert result["mint_limit"] == 1000
        assert result["decimals"] == 8
        assert "json" in result
        assert "envelope_hex" in result
        assert "script_hex" in result

        # Verify JSON structure
        json_data = json.loads(result["json"])
        assert json_data["p"] == "brc-20"
        assert json_data["op"] == "deploy"
        assert json_data["tick"] == "TEST"

    @pytest.mark.asyncio
    async def test_create_token_mint(self, server):
        """create_token_mint produces valid mint data."""
        mint_fn = server._tool_manager._tools["create_token_mint"].fn

        result = mint_fn(tick="TEST", amount=500)

        assert result["operation"] == "mint"
        assert result["tick"] == "TEST"
        assert result["amount"] == 500
        assert "json" in result
        assert "envelope_hex" in result
        assert "script_hex" in result

        # Verify JSON structure
        json_data = json.loads(result["json"])
        assert json_data["p"] == "brc-20"
        assert json_data["op"] == "mint"

    @pytest.mark.asyncio
    async def test_create_token_transfer(self, server):
        """create_token_transfer produces valid transfer data."""
        transfer_fn = server._tool_manager._tools["create_token_transfer"].fn

        result = transfer_fn(tick="TEST", amount=100)

        assert result["operation"] == "transfer"
        assert result["tick"] == "TEST"
        assert result["amount"] == 100
        assert "json" in result
        assert "envelope_hex" in result
        assert "script_hex" in result

        # Verify JSON structure
        json_data = json.loads(result["json"])
        assert json_data["p"] == "brc-20"
        assert json_data["op"] == "transfer"


class TestTimestampOperations:
    """Test timestamp creation and verification tools."""

    @pytest.fixture
    def server(self):
        """Create a fresh server for each test."""
        return create_server()

    @pytest.mark.asyncio
    async def test_create_verify_timestamp_roundtrip(self, server):
        """create_timestamp and verify_timestamp work together correctly."""
        create_fn = server._tool_manager._tools["create_timestamp"].fn
        verify_fn = server._tool_manager._tools["verify_timestamp"].fn

        test_data = "Important document content"

        # Create a timestamp
        created = create_fn(test_data, "utf-8", "sha256")

        assert "hash_hex" in created
        assert "envelope_hex" in created
        assert "script_hex" in created
        assert created["hash_algorithm"] == "sha256"

        # Verify the timestamp
        verified = verify_fn(test_data, created["hash_hex"], "utf-8", "sha256")

        assert verified["verified"] is True
        assert verified["computed_hash"] == created["hash_hex"]

    @pytest.mark.asyncio
    async def test_verify_timestamp_fails_for_modified_data(self, server):
        """verify_timestamp returns false for modified data."""
        create_fn = server._tool_manager._tools["create_timestamp"].fn
        verify_fn = server._tool_manager._tools["verify_timestamp"].fn

        original_data = "Original content"
        modified_data = "Modified content"

        # Create timestamp for original
        created = create_fn(original_data, "utf-8", "sha256")

        # Try to verify with modified data
        verified = verify_fn(modified_data, created["hash_hex"], "utf-8", "sha256")

        assert verified["verified"] is False

    @pytest.mark.asyncio
    async def test_create_timestamp_sha3(self, server):
        """create_timestamp works with SHA3-256."""
        create_fn = server._tool_manager._tools["create_timestamp"].fn

        result = create_fn("Test data", "utf-8", "sha3_256")

        assert result["hash_algorithm"] == "sha3_256"
        assert len(result["hash_hex"]) == 64  # 32 bytes = 64 hex chars

    @pytest.mark.asyncio
    async def test_create_timestamp_invalid_hex(self, server):
        """create_timestamp returns error for invalid hex input."""
        create_fn = server._tool_manager._tools["create_timestamp"].fn

        result = create_fn("not_valid_hex", "hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]

    @pytest.mark.asyncio
    async def test_verify_timestamp_invalid_hex_data(self, server):
        """verify_timestamp returns error for invalid hex data input."""
        verify_fn = server._tool_manager._tools["verify_timestamp"].fn

        result = verify_fn("not_valid_hex", "abcd1234" * 8, "hex")

        assert "error" in result
        assert "Invalid hex string for data" in result["error"]

    @pytest.mark.asyncio
    async def test_verify_timestamp_invalid_hex_hash(self, server):
        """verify_timestamp returns error for invalid hex expected_hash."""
        verify_fn = server._tool_manager._tools["verify_timestamp"].fn

        result = verify_fn("valid data", "not_valid_hex", "utf-8")

        assert "error" in result
        assert "Invalid hex string for expected_hash" in result["error"]


class TestDocumentOperations:
    """Test embed_document and read_document tools."""

    @pytest.fixture
    def server(self):
        """Create a fresh server for each test."""
        return create_server()

    @pytest.mark.asyncio
    async def test_embed_read_document_roundtrip(self, server):
        """embed_document and read_document roundtrip works correctly."""
        embed_fn = server._tool_manager._tools["embed_document"].fn
        read_fn = server._tool_manager._tools["read_document"].fn

        test_content = "This is my document content."

        # Embed the document
        embedded = embed_fn(test_content, "text/plain", "utf-8")

        assert "envelope_hex" in embedded
        assert embedded["content_type"] == "text/plain"

        # Read it back
        read_result = read_fn(embedded["envelope_hex"])

        assert read_result["is_envelope"] is True
        assert read_result["envelope_type"] == "TEXT"
        assert read_result["content_utf8"] == test_content

    @pytest.mark.asyncio
    async def test_embed_document_with_custom_content_type(self, server):
        """embed_document handles custom content types."""
        embed_fn = server._tool_manager._tools["embed_document"].fn
        read_fn = server._tool_manager._tools["read_document"].fn

        test_content = '{"key": "value"}'

        # Embed with JSON content type
        embedded = embed_fn(test_content, "application/json", "utf-8")

        # The envelope should be FILE type for non-text/plain
        read_result = read_fn(embedded["envelope_hex"])

        assert read_result["is_envelope"] is True
        assert read_result["envelope_type"] == "FILE"
        assert read_result["content_type"] == "application/json"
        assert read_result["content_utf8"] == test_content

    @pytest.mark.asyncio
    async def test_embed_document_invalid_hex(self, server):
        """embed_document returns error for invalid hex input."""
        embed_fn = server._tool_manager._tools["embed_document"].fn

        result = embed_fn("not_valid_hex", "text/plain", "hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]

    @pytest.mark.asyncio
    async def test_read_document_invalid_hex(self, server):
        """read_document returns error for invalid hex input."""
        read_fn = server._tool_manager._tools["read_document"].fn

        result = read_fn("not_valid_hex")

        assert "error" in result
        assert "Invalid hex string" in result["error"]

    @pytest.mark.asyncio
    async def test_read_document_non_envelope(self, server):
        """read_document handles non-envelope data gracefully."""
        read_fn = server._tool_manager._tools["read_document"].fn

        # Send raw data that's not an envelope
        raw_data = "Hello World".encode().hex()
        result = read_fn(raw_data)

        assert result["is_envelope"] is False
        assert result["content_utf8"] == "Hello World"
