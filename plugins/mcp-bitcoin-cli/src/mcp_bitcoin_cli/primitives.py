"""Bitcoin OP_RETURN script encoding and decoding.

Supports Bitcoin Core v30+ with up to ~100KB OP_RETURN data.
"""

# Bitcoin script opcodes
OP_RETURN = 0x6A
OP_PUSHDATA1 = 0x4C
OP_PUSHDATA2 = 0x4D
OP_PUSHDATA4 = 0x4E


def encode_op_return_script(data: bytes) -> bytes:
    """Encode data into an OP_RETURN script.

    Uses appropriate push opcode based on data size:
    - < 76 bytes: direct push (1 byte length)
    - 76-255 bytes: OP_PUSHDATA1 (1 byte length)
    - 256-65535 bytes: OP_PUSHDATA2 (2 byte length, little-endian)
    - > 65535 bytes: OP_PUSHDATA4 (4 byte length, little-endian)

    Args:
        data: Raw data to embed in OP_RETURN

    Returns:
        Complete OP_RETURN script as bytes
    """
    length = len(data)

    if length < 76:
        # Direct push
        return bytes([OP_RETURN, length]) + data
    elif length <= 255:
        # OP_PUSHDATA1
        return bytes([OP_RETURN, OP_PUSHDATA1, length]) + data
    elif length <= 65535:
        # OP_PUSHDATA2 (little-endian)
        return bytes([OP_RETURN, OP_PUSHDATA2]) + length.to_bytes(2, 'little') + data
    else:
        # OP_PUSHDATA4 (little-endian)
        return bytes([OP_RETURN, OP_PUSHDATA4]) + length.to_bytes(4, 'little') + data


def decode_op_return_script(script: bytes) -> bytes:
    """Decode data from an OP_RETURN script.

    Args:
        script: OP_RETURN script bytes

    Returns:
        Extracted data payload

    Raises:
        ValueError: If script is not a valid OP_RETURN
    """
    if len(script) < 2:
        raise ValueError("Script too short")

    if script[0] != OP_RETURN:
        raise ValueError(f"Script is not an OP_RETURN (opcode: {script[0]:#x})")

    pos = 1
    push_byte = script[pos]
    pos += 1

    if push_byte < 76:
        # Direct push
        length = push_byte
    elif push_byte == OP_PUSHDATA1:
        if pos >= len(script):
            raise ValueError("Truncated PUSHDATA1 script")
        length = script[pos]
        pos += 1
    elif push_byte == OP_PUSHDATA2:
        if pos + 2 > len(script):
            raise ValueError("Truncated PUSHDATA2 script")
        length = int.from_bytes(script[pos:pos+2], 'little')
        pos += 2
    elif push_byte == OP_PUSHDATA4:
        if pos + 4 > len(script):
            raise ValueError("Truncated PUSHDATA4 script")
        length = int.from_bytes(script[pos:pos+4], 'little')
        pos += 4
    else:
        raise ValueError(f"Invalid push opcode: {push_byte:#x}")

    if pos + length > len(script):
        raise ValueError(f"Script truncated: expected {length} bytes, got {len(script) - pos}")
    return script[pos:pos+length]
