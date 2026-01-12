"""Integration tests for complete workflows.

These tests verify that all components work together correctly:
- Envelope + OP_RETURN primitives roundtrip
- BRC-20 token operations full workflow
- Document storage workflow
- Timestamp creation and verification workflow
"""

import hashlib
import json

import pytest

from mcp_bitcoin_cli.envelope import (
    MAGIC_BYTES,
    VERSION,
    Envelope,
    EnvelopeType,
    decode_envelope,
    encode_envelope,
)
from mcp_bitcoin_cli.primitives import (
    decode_op_return_script,
    encode_op_return_script,
)
from mcp_bitcoin_cli.protocols.brc20 import (
    BRC20Deploy,
    BRC20Mint,
    BRC20Protocol,
    BRC20Transfer,
)


class TestEnvelopePrimitivesRoundtrip:
    """Test envelope + OP_RETURN primitives roundtrip."""

    def test_raw_data_full_roundtrip(self):
        """Raw data: encode -> envelope -> OP_RETURN -> decode -> verify."""
        original_data = b"Hello, Bitcoin blockchain!"

        # Step 1: Wrap in envelope
        envelope_bytes = encode_envelope(original_data, EnvelopeType.RAW)

        # Step 2: Encode to OP_RETURN script
        script = encode_op_return_script(envelope_bytes)

        # Step 3: Decode OP_RETURN script
        decoded_envelope_bytes = decode_op_return_script(script)

        # Step 4: Decode envelope
        envelope = decode_envelope(decoded_envelope_bytes)

        # Verify complete roundtrip
        assert envelope.magic == MAGIC_BYTES
        assert envelope.version == VERSION
        assert envelope.type == EnvelopeType.RAW
        assert envelope.payload == original_data

    def test_text_data_full_roundtrip(self):
        """UTF-8 text: encode -> envelope -> OP_RETURN -> decode -> verify."""
        original_text = "The quick brown fox jumps over the lazy dog"
        original_data = original_text.encode("utf-8")

        envelope_bytes = encode_envelope(original_data, EnvelopeType.TEXT)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.TEXT
        assert envelope.payload.decode("utf-8") == original_text

    def test_json_data_full_roundtrip(self):
        """JSON data: encode -> envelope -> OP_RETURN -> decode -> verify."""
        original_obj = {"message": "test", "value": 42, "nested": {"key": "value"}}
        json_str = json.dumps(original_obj, separators=(",", ":"))
        original_data = json_str.encode("utf-8")

        envelope_bytes = encode_envelope(original_data, EnvelopeType.JSON)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.JSON
        decoded_obj = json.loads(envelope.payload.decode("utf-8"))
        assert decoded_obj == original_obj

    def test_hash_data_full_roundtrip(self):
        """Hash commitment: encode -> envelope -> OP_RETURN -> decode -> verify."""
        original_hash = hashlib.sha256(b"data to timestamp").digest()

        envelope_bytes = encode_envelope(original_hash, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.HASH
        assert envelope.payload == original_hash
        assert len(envelope.payload) == 32  # SHA256 hash length

    def test_large_data_roundtrip(self):
        """Large data (using PUSHDATA2): roundtrip verification."""
        # Data larger than 255 bytes requires PUSHDATA2
        original_data = b"x" * 500

        envelope_bytes = encode_envelope(original_data, EnvelopeType.RAW)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.payload == original_data

    def test_binary_data_roundtrip(self):
        """Binary data with all byte values: roundtrip verification."""
        # Data containing all possible byte values (0x00-0xFF)
        original_data = bytes(range(256))

        envelope_bytes = encode_envelope(original_data, EnvelopeType.RAW)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.payload == original_data

    @pytest.mark.parametrize("env_type", list(EnvelopeType))
    def test_all_envelope_types_roundtrip(self, env_type):
        """All envelope types complete roundtrip successfully."""
        original_data = b"test payload for " + env_type.name.encode()

        envelope_bytes = encode_envelope(original_data, env_type)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == env_type
        assert envelope.payload == original_data


class TestBRC20FullWorkflow:
    """Test BRC-20 token operations full workflow."""

    def test_deploy_full_workflow(self):
        """Deploy: create -> envelope -> OP_RETURN -> decode -> parse -> verify."""
        # Step 1: Create deploy operation
        deploy = BRC20Deploy(
            tick="TEST",
            max_supply=21000000,
            mint_limit=1000,
            decimals=8,
        )

        # Step 2: Convert to envelope
        envelope_bytes = deploy.to_envelope()

        # Step 3: Encode to OP_RETURN script
        script = encode_op_return_script(envelope_bytes)

        # Step 4: Decode OP_RETURN script
        decoded_envelope_bytes = decode_op_return_script(script)

        # Step 5: Decode envelope
        envelope = decode_envelope(decoded_envelope_bytes)

        # Step 6: Verify envelope type
        assert envelope.type == EnvelopeType.TOKEN

        # Step 7: Parse BRC-20 JSON from payload
        json_str = envelope.payload.decode("utf-8")
        parsed_op = BRC20Protocol.parse(json_str)

        # Verify complete roundtrip
        assert isinstance(parsed_op, BRC20Deploy)
        assert parsed_op.tick == "TEST"
        assert parsed_op.max_supply == 21000000
        assert parsed_op.mint_limit == 1000
        assert parsed_op.decimals == 8

    def test_mint_full_workflow(self):
        """Mint: create -> envelope -> OP_RETURN -> decode -> parse -> verify."""
        mint = BRC20Mint(tick="TEST", amount=1000)

        envelope_bytes = mint.to_envelope()
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.TOKEN

        json_str = envelope.payload.decode("utf-8")
        parsed_op = BRC20Protocol.parse(json_str)

        assert isinstance(parsed_op, BRC20Mint)
        assert parsed_op.tick == "TEST"
        assert parsed_op.amount == 1000

    def test_transfer_full_workflow(self):
        """Transfer: create -> envelope -> OP_RETURN -> decode -> parse -> verify."""
        transfer = BRC20Transfer(tick="TEST", amount=500)

        envelope_bytes = transfer.to_envelope()
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.TOKEN

        json_str = envelope.payload.decode("utf-8")
        parsed_op = BRC20Protocol.parse(json_str)

        assert isinstance(parsed_op, BRC20Transfer)
        assert parsed_op.tick == "TEST"
        assert parsed_op.amount == 500

    def test_complete_token_lifecycle(self):
        """Test a complete token lifecycle: deploy -> mint -> transfer."""
        # Deploy token
        deploy = BRC20Deploy(tick="LIFE", max_supply=1000000, mint_limit=100)
        deploy_json = json.loads(deploy.to_json())
        assert deploy_json["op"] == "deploy"
        assert deploy_json["tick"] == "LIFE"

        # Mint tokens
        mint = BRC20Mint(tick="LIFE", amount=100)
        mint_json = json.loads(mint.to_json())
        assert mint_json["op"] == "mint"
        assert mint_json["amt"] == "100"

        # Transfer tokens
        transfer = BRC20Transfer(tick="LIFE", amount=50)
        transfer_json = json.loads(transfer.to_json())
        assert transfer_json["op"] == "transfer"
        assert transfer_json["amt"] == "50"

        # Verify all operations encode to valid scripts
        for op in [deploy, mint, transfer]:
            envelope_bytes = op.to_envelope()
            script = encode_op_return_script(envelope_bytes)
            decoded = decode_op_return_script(script)
            envelope = decode_envelope(decoded)
            assert envelope.type == EnvelopeType.TOKEN

    def test_json_format_consistency(self):
        """Verify JSON format is consistent between encode and decode."""
        deploy = BRC20Deploy(tick="JSON", max_supply=100, mint_limit=10, decimals=6)

        # Get the JSON string
        json_str = deploy.to_json()

        # Parse it back
        parsed = BRC20Protocol.parse(json_str)

        # Re-encode and verify consistency
        re_encoded_json = parsed.to_json()
        assert json.loads(json_str) == json.loads(re_encoded_json)


class TestDocumentStorageWorkflow:
    """Test document storage workflow."""

    def test_plain_text_document_workflow(self):
        """Plain text document: embed -> OP_RETURN -> decode -> verify."""
        content = "This is a plain text document for blockchain storage."
        content_bytes = content.encode("utf-8")

        # Embed as TEXT envelope type
        envelope_bytes = encode_envelope(content_bytes, EnvelopeType.TEXT)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.TEXT
        assert envelope.payload.decode("utf-8") == content

    def test_json_document_workflow(self):
        """JSON document: embed -> OP_RETURN -> decode -> verify."""
        document = {
            "title": "Test Document",
            "author": "Integration Test",
            "content": "Document body content",
            "tags": ["test", "integration"],
        }
        json_str = json.dumps(document, separators=(",", ":"))
        content_bytes = json_str.encode("utf-8")

        envelope_bytes = encode_envelope(content_bytes, EnvelopeType.JSON)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.JSON
        decoded_document = json.loads(envelope.payload.decode("utf-8"))
        assert decoded_document == document

    def test_file_with_content_type_workflow(self):
        """File with content-type header: embed -> OP_RETURN -> decode -> verify."""
        content_type = "application/json"
        content = '{"key": "value"}'
        content_bytes = content.encode("utf-8")

        # File envelope includes content-type header
        header = f"{content_type}\n".encode("utf-8")
        payload = header + content_bytes

        envelope_bytes = encode_envelope(payload, EnvelopeType.FILE)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.FILE

        # Parse content-type header
        decoded_payload = envelope.payload
        if b"\n" in decoded_payload:
            decoded_header, decoded_content = decoded_payload.split(b"\n", 1)
            decoded_content_type = decoded_header.decode("utf-8")
        else:
            decoded_content_type = "application/octet-stream"
            decoded_content = decoded_payload

        assert decoded_content_type == content_type
        assert decoded_content.decode("utf-8") == content

    def test_binary_document_workflow(self):
        """Binary document: embed -> OP_RETURN -> decode -> verify."""
        # Simulate binary content (e.g., small image data)
        binary_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])  # PNG header

        envelope_bytes = encode_envelope(binary_content, EnvelopeType.RAW)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.RAW
        assert envelope.payload == binary_content

    def test_multiple_documents_consistency(self):
        """Multiple documents encoded and decoded maintain consistency."""
        documents = [
            ("text/plain", "Simple text"),
            ("application/json", '{"key": "value"}'),
            ("text/html", "<h1>Hello</h1>"),
        ]

        for content_type, content in documents:
            content_bytes = content.encode("utf-8")
            header = f"{content_type}\n".encode("utf-8")
            payload = header + content_bytes

            envelope_bytes = encode_envelope(payload, EnvelopeType.FILE)
            script = encode_op_return_script(envelope_bytes)
            decoded_envelope_bytes = decode_op_return_script(script)
            envelope = decode_envelope(decoded_envelope_bytes)

            decoded_header, decoded_content = envelope.payload.split(b"\n", 1)
            assert decoded_header.decode("utf-8") == content_type
            assert decoded_content.decode("utf-8") == content


class TestTimestampWorkflow:
    """Test timestamp creation and verification workflow."""

    def test_timestamp_creation_and_verification_sha256(self):
        """Create timestamp with SHA256 and verify it matches."""
        original_data = b"Data to be timestamped on the blockchain"

        # Create timestamp (hash)
        hash_bytes = hashlib.sha256(original_data).digest()

        # Embed in envelope
        envelope_bytes = encode_envelope(hash_bytes, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)

        # Decode and extract hash
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.HASH
        stored_hash = envelope.payload

        # Verify: compute hash of original data and compare
        verification_hash = hashlib.sha256(original_data).digest()
        assert stored_hash == verification_hash

    def test_timestamp_creation_and_verification_sha3(self):
        """Create timestamp with SHA3-256 and verify it matches."""
        original_data = b"SHA3 timestamped data"

        hash_bytes = hashlib.sha3_256(original_data).digest()

        envelope_bytes = encode_envelope(hash_bytes, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.HASH
        stored_hash = envelope.payload

        verification_hash = hashlib.sha3_256(original_data).digest()
        assert stored_hash == verification_hash

    def test_timestamp_verification_fails_with_modified_data(self):
        """Verify timestamp fails when data is modified."""
        original_data = b"Original data"

        # Create timestamp
        hash_bytes = hashlib.sha256(original_data).digest()
        envelope_bytes = encode_envelope(hash_bytes, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        stored_hash = envelope.payload

        # Try to verify with modified data
        modified_data = b"Modified data"
        verification_hash = hashlib.sha256(modified_data).digest()

        # Should NOT match
        assert stored_hash != verification_hash

    def test_timestamp_hash_length(self):
        """Verify timestamp hash has correct length."""
        data = b"Test data"

        # SHA256 should be 32 bytes
        sha256_hash = hashlib.sha256(data).digest()
        envelope_bytes = encode_envelope(sha256_hash, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert len(envelope.payload) == 32

        # SHA3-256 should also be 32 bytes
        sha3_hash = hashlib.sha3_256(data).digest()
        envelope_bytes = encode_envelope(sha3_hash, EnvelopeType.HASH)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert len(envelope.payload) == 32

    def test_multiple_timestamps_independence(self):
        """Multiple timestamps are independent and verifiable."""
        data_items = [
            b"First document to timestamp",
            b"Second document to timestamp",
            b"Third document to timestamp",
        ]

        stored_hashes = []

        # Create timestamps for all documents
        for data in data_items:
            hash_bytes = hashlib.sha256(data).digest()
            envelope_bytes = encode_envelope(hash_bytes, EnvelopeType.HASH)
            script = encode_op_return_script(envelope_bytes)
            decoded_envelope_bytes = decode_op_return_script(script)
            envelope = decode_envelope(decoded_envelope_bytes)
            stored_hashes.append(envelope.payload)

        # Verify each timestamp independently
        for i, data in enumerate(data_items):
            verification_hash = hashlib.sha256(data).digest()
            assert stored_hashes[i] == verification_hash

        # Verify all hashes are unique
        assert len(set(stored_hashes)) == len(stored_hashes)


class TestCrossModuleIntegration:
    """Test that all modules use consistent data formats."""

    def test_envelope_type_consistency_with_brc20(self):
        """BRC-20 operations use correct envelope type."""
        operations = [
            BRC20Deploy(tick="TEST", max_supply=1000),
            BRC20Mint(tick="TEST", amount=100),
            BRC20Transfer(tick="TEST", amount=50),
        ]

        for op in operations:
            envelope_bytes = op.to_envelope()
            envelope = decode_envelope(envelope_bytes)
            assert envelope.type == EnvelopeType.TOKEN

    def test_data_format_consistency_across_modules(self):
        """Data encoded by one module is correctly decoded by another."""
        # Create BRC-20 mint operation
        mint = BRC20Mint(tick="MINT", amount=500)

        # Encode using BRC-20 module
        envelope_bytes = mint.to_envelope()

        # Encode to script using primitives module
        script = encode_op_return_script(envelope_bytes)

        # Decode using primitives module
        decoded_data = decode_op_return_script(script)

        # Decode using envelope module
        envelope = decode_envelope(decoded_data)

        # Parse using BRC-20 module
        parsed = BRC20Protocol.parse(envelope.payload.decode("utf-8"))

        # Full circle verification
        assert isinstance(parsed, BRC20Mint)
        assert parsed.tick == "MINT"
        assert parsed.amount == 500

    def test_hex_encoding_consistency(self):
        """Hex encoding/decoding is consistent across workflows."""
        original_hex = "deadbeef"
        original_bytes = bytes.fromhex(original_hex)

        envelope_bytes = encode_envelope(original_bytes, EnvelopeType.RAW)
        script = encode_op_return_script(envelope_bytes)

        # Convert to hex (as would be stored/transmitted)
        script_hex = script.hex()

        # Convert back from hex
        script_from_hex = bytes.fromhex(script_hex)

        decoded_envelope_bytes = decode_op_return_script(script_from_hex)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.payload.hex() == original_hex

    def test_envelope_header_preservation(self):
        """Envelope header fields are preserved through full workflow."""
        data = b"test data"

        for env_type in EnvelopeType:
            envelope_bytes = encode_envelope(data, env_type)
            script = encode_op_return_script(envelope_bytes)
            decoded_envelope_bytes = decode_op_return_script(script)
            envelope = decode_envelope(decoded_envelope_bytes)

            assert envelope.magic == MAGIC_BYTES
            assert envelope.version == VERSION
            assert envelope.type == env_type
            assert envelope.payload == data

    def test_empty_payload_handling(self):
        """Empty payload is handled correctly across modules."""
        empty_data = b""

        envelope_bytes = encode_envelope(empty_data, EnvelopeType.RAW)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.payload == empty_data
        assert len(envelope.payload) == 0

    def test_max_envelope_type_value(self):
        """Maximum standard envelope type value is handled correctly."""
        # FILE (0x05) is the highest defined type
        data = b"file content"

        envelope_bytes = encode_envelope(data, EnvelopeType.FILE)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.type == EnvelopeType.FILE
        assert envelope.payload == data


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_boundary_sizes_for_push_opcodes(self):
        """Test data at opcode size boundaries."""
        # Test sizes at opcode boundaries: 75, 76, 255, 256
        boundary_sizes = [75, 76, 255, 256]

        for size in boundary_sizes:
            data = b"x" * size
            envelope_bytes = encode_envelope(data, EnvelopeType.RAW)
            script = encode_op_return_script(envelope_bytes)
            decoded_envelope_bytes = decode_op_return_script(script)
            envelope = decode_envelope(decoded_envelope_bytes)

            assert envelope.payload == data
            assert len(envelope.payload) == size

    def test_unicode_text_roundtrip(self):
        """Unicode text with various scripts roundtrips correctly."""
        unicode_texts = [
            "Hello",  # ASCII
            "Bonjour",  # Latin-1
            "Привет",  # Cyrillic
            "你好",  # Chinese
            "مرحبا",  # Arabic
            "שלום",  # Hebrew
        ]

        for text in unicode_texts:
            data = text.encode("utf-8")
            envelope_bytes = encode_envelope(data, EnvelopeType.TEXT)
            script = encode_op_return_script(envelope_bytes)
            decoded_envelope_bytes = decode_op_return_script(script)
            envelope = decode_envelope(decoded_envelope_bytes)

            assert envelope.payload.decode("utf-8") == text

    def test_brc20_tick_case_sensitivity(self):
        """BRC-20 tick is case-sensitive."""
        deploy_upper = BRC20Deploy(tick="TEST", max_supply=1000)
        deploy_lower = BRC20Deploy(tick="test", max_supply=1000)

        json_upper = json.loads(deploy_upper.to_json())
        json_lower = json.loads(deploy_lower.to_json())

        assert json_upper["tick"] == "TEST"
        assert json_lower["tick"] == "test"
        assert json_upper["tick"] != json_lower["tick"]

    def test_special_characters_in_content(self):
        """Special characters in content are preserved."""
        special_content = 'Line1\nLine2\tTabbed\r\nWindows line\x00Null byte'
        data = special_content.encode("utf-8")

        envelope_bytes = encode_envelope(data, EnvelopeType.RAW)
        script = encode_op_return_script(envelope_bytes)
        decoded_envelope_bytes = decode_op_return_script(script)
        envelope = decode_envelope(decoded_envelope_bytes)

        assert envelope.payload.decode("utf-8") == special_content
