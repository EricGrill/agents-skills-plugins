"""Base protocol class for custom protocols."""

from abc import ABC, abstractmethod


class Protocol(ABC):
    """Base class for OP_RETURN protocols."""

    @abstractmethod
    def to_bytes(self) -> bytes:
        """Convert to raw bytes for embedding."""
        pass

    @abstractmethod
    def to_envelope(self) -> bytes:
        """Convert to BTCD envelope format."""
        pass
