"""Tests for OP_RETURN primitives."""

import pytest
from mcp_bitcoin_cli.primitives import (
    encode_op_return_script,
    decode_op_return_script,
    OP_RETURN,
    OP_PUSHDATA1,
    OP_PUSHDATA2,
    OP_PUSHDATA4,
)
from mcp_bitcoin_cli.envelope import EnvelopeType, encode_envelope


class TestOpReturnEncoding:
    """Test OP_RETURN script encoding."""

    def test_encode_small_data(self):
        """Encode small data (< 76 bytes) directly."""
        data = b"hello"
        script = encode_op_return_script(data)

        assert script[0] == OP_RETURN
        assert script[1] == len(data)  # Direct push
        assert script[2:] == data

    def test_encode_medium_data(self):
        """Encode medium data (76-255 bytes) with PUSHDATA1."""
        data = b"x" * 100
        script = encode_op_return_script(data)

        assert script[0] == OP_RETURN
        assert script[1] == OP_PUSHDATA1
        assert script[2] == len(data)
        assert script[3:] == data

    def test_encode_large_data(self):
        """Encode large data (256+ bytes) with PUSHDATA2."""
        data = b"x" * 300
        script = encode_op_return_script(data)

        assert script[0] == OP_RETURN
        assert script[1] == OP_PUSHDATA2
        # Little-endian length
        assert int.from_bytes(script[2:4], 'little') == len(data)
        assert script[4:] == data

    def test_encode_with_envelope(self):
        """Encode data wrapped in envelope."""
        data = b"test"
        envelope = encode_envelope(data, EnvelopeType.TEXT)
        script = encode_op_return_script(envelope)

        # Script contains envelope with magic bytes
        assert b"BTCD" in script


class TestOpReturnDecoding:
    """Test OP_RETURN script decoding."""

    def test_decode_small_data(self):
        """Decode small OP_RETURN."""
        data = b"hello"
        script = encode_op_return_script(data)

        decoded = decode_op_return_script(script)
        assert decoded == data

    def test_decode_medium_data(self):
        """Decode medium OP_RETURN with PUSHDATA1."""
        data = b"x" * 100
        script = encode_op_return_script(data)

        decoded = decode_op_return_script(script)
        assert decoded == data

    def test_decode_large_data(self):
        """Decode large OP_RETURN with PUSHDATA2."""
        data = b"x" * 300
        script = encode_op_return_script(data)

        decoded = decode_op_return_script(script)
        assert decoded == data

    def test_decode_invalid_opcode(self):
        """Reject non-OP_RETURN script."""
        script = bytes([0x76, 0x05]) + b"hello"  # OP_DUP instead

        with pytest.raises(ValueError, match="not an OP_RETURN"):
            decode_op_return_script(script)

    def test_roundtrip_max_size(self):
        """Roundtrip near-max OP_RETURN (100KB)."""
        data = b"x" * 99000
        script = encode_op_return_script(data)
        decoded = decode_op_return_script(script)

        assert decoded == data


class TestMalformedScripts:
    """Test handling of malformed OP_RETURN scripts."""

    def test_truncated_pushdata1_no_length(self):
        """PUSHDATA1 with no length byte should raise ValueError."""
        script = bytes([OP_RETURN, OP_PUSHDATA1])  # Missing length byte

        with pytest.raises(ValueError, match="Truncated PUSHDATA1"):
            decode_op_return_script(script)

    def test_truncated_pushdata2_partial_length(self):
        """PUSHDATA2 with only 1 length byte should raise ValueError."""
        script = bytes([OP_RETURN, OP_PUSHDATA2, 0x00])  # Only 1 of 2 length bytes

        with pytest.raises(ValueError, match="Truncated PUSHDATA2"):
            decode_op_return_script(script)

    def test_truncated_pushdata2_no_length(self):
        """PUSHDATA2 with no length bytes should raise ValueError."""
        script = bytes([OP_RETURN, OP_PUSHDATA2])

        with pytest.raises(ValueError, match="Truncated PUSHDATA2"):
            decode_op_return_script(script)

    def test_truncated_pushdata4_partial_length(self):
        """PUSHDATA4 with only 2 length bytes should raise ValueError."""
        script = bytes([OP_RETURN, OP_PUSHDATA4, 0x00, 0x00])  # Only 2 of 4 length bytes

        with pytest.raises(ValueError, match="Truncated PUSHDATA4"):
            decode_op_return_script(script)

    def test_truncated_pushdata4_no_length(self):
        """PUSHDATA4 with no length bytes should raise ValueError."""
        script = bytes([OP_RETURN, OP_PUSHDATA4])

        with pytest.raises(ValueError, match="Truncated PUSHDATA4"):
            decode_op_return_script(script)

    def test_truncated_data_direct_push(self):
        """Direct push with declared length > actual data should raise ValueError."""
        # Declares 10 bytes but only has 3
        script = bytes([OP_RETURN, 10]) + b"abc"

        with pytest.raises(ValueError, match="Script truncated.*expected 10 bytes.*got 3"):
            decode_op_return_script(script)

    def test_truncated_data_pushdata1(self):
        """PUSHDATA1 with declared length > actual data should raise ValueError."""
        # Declares 100 bytes but only has 5
        script = bytes([OP_RETURN, OP_PUSHDATA1, 100]) + b"hello"

        with pytest.raises(ValueError, match="Script truncated.*expected 100 bytes.*got 5"):
            decode_op_return_script(script)

    def test_truncated_data_pushdata2(self):
        """PUSHDATA2 with declared length > actual data should raise ValueError."""
        # Declares 1000 bytes (little-endian) but only has 10
        length_bytes = (1000).to_bytes(2, 'little')
        script = bytes([OP_RETURN, OP_PUSHDATA2]) + length_bytes + b"0123456789"

        with pytest.raises(ValueError, match="Script truncated.*expected 1000 bytes.*got 10"):
            decode_op_return_script(script)

    def test_script_too_short(self):
        """Script with less than 2 bytes should raise ValueError."""
        with pytest.raises(ValueError, match="Script too short"):
            decode_op_return_script(bytes([OP_RETURN]))

        with pytest.raises(ValueError, match="Script too short"):
            decode_op_return_script(bytes([]))
