"""Custom exceptions for the MCP prediction market server."""


class PlatformError(Exception):
    """Exception raised when a platform operation fails.

    Attributes:
        platform: The name of the platform that failed.
        message: A description of what went wrong.
    """

    def __init__(self, platform: str, message: str) -> None:
        """Initialize PlatformError.

        Args:
            platform: The name of the platform that failed.
            message: A description of what went wrong.
        """
        self.platform = platform
        self.message = message
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """Return a formatted error message."""
        return f"[{self.platform}] {self.message}"
