"""BTCD envelope encoding and decoding.

The envelope format:
- Magic (4 bytes): "BTCD"
- Version (1 byte): Protocol version
- Type (1 byte): Data type identifier
- Payload (variable): Type-specific data
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Union


MAGIC_BYTES = b"BTCD"
VERSION = 0x01


class EnvelopeType(IntEnum):
    """Envelope data types."""

    RAW = 0x00      # Raw bytes, no structure
    TEXT = 0x01     # UTF-8 text
    JSON = 0x02     # JSON document
    HASH = 0x03     # Hash commitment (timestamp/attestation)
    TOKEN = 0x04    # Token operation (BRC-20 compatible)
    FILE = 0x05     # File with content-type header
    # 0x80-0xFF reserved for custom protocols


@dataclass
class Envelope:
    """Decoded envelope structure.

    The type field can be an EnvelopeType for known types, or an int
    for custom types (0x80-0xFF).
    """

    magic: bytes
    version: int
    type: Union[EnvelopeType, int]
    payload: bytes


def encode_envelope(data: bytes, envelope_type: EnvelopeType) -> bytes:
    """Encode data into BTCD envelope format.

    Args:
        data: Raw bytes to encode
        envelope_type: Type identifier for the data

    Returns:
        Encoded envelope as bytes
    """
    return MAGIC_BYTES + bytes([VERSION, envelope_type.value]) + data


def decode_envelope(data: bytes) -> Envelope:
    """Decode BTCD envelope format.

    Args:
        data: Raw envelope bytes

    Returns:
        Decoded Envelope object

    Raises:
        ValueError: If envelope is invalid
    """
    if len(data) < 6:
        raise ValueError("Envelope data too short (minimum 6 bytes)")

    magic = data[:4]
    if magic != MAGIC_BYTES:
        raise ValueError(f"Invalid magic bytes: expected {MAGIC_BYTES!r}, got {magic!r}")

    version = data[4]
    type_byte = data[5]
    payload = data[6:]

    try:
        envelope_type: Union[EnvelopeType, int] = EnvelopeType(type_byte)
    except ValueError:
        # Allow custom types (0x80+) - store as raw int
        if type_byte >= 0x80:
            envelope_type = type_byte
        else:
            raise ValueError(f"Unknown envelope type: {type_byte:#x}")

    return Envelope(
        magic=magic,
        version=version,
        type=envelope_type,
        payload=payload,
    )
