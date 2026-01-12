"""Base protocol for platform adapters."""
from typing import Protocol, runtime_checkable

from mcp_predictive_market.schema import Market


@runtime_checkable
class PlatformAdapter(Protocol):
    """Protocol that all platform adapters must implement."""

    platform: str

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query."""
        ...

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by its native ID."""
        ...

    async def list_categories(self) -> list[str]:
        """List available market categories."""
        ...

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a specific category."""
        ...
