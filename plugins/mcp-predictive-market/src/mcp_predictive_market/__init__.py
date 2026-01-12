"""MCP server for querying and aggregating prediction market data."""
from mcp_predictive_market.errors import PlatformError

__all__ = ["PlatformError"]


def hello() -> str:
    """Return a greeting message from the package."""
    return "Hello from mcp-predictive-market!"
