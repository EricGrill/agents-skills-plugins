"""MCP server entry point for prediction market aggregation."""
import json

from mcp.server import Server
from mcp.types import Tool, TextContent

from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from mcp_predictive_market.adapters.polymarket import PolymarketAdapter
from mcp_predictive_market.adapters.metaculus import MetaculusAdapter
from mcp_predictive_market.adapters.predictit import PredictItAdapter
from mcp_predictive_market.adapters.kalshi import KalshiAdapter
from mcp_predictive_market.tools import ToolHandlers


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("mcp-predictive-market")

    # Initialize adapters
    adapters = {
        "manifold": ManifoldAdapter(),
        "polymarket": PolymarketAdapter(),
        "metaculus": MetaculusAdapter(),
        "predictit": PredictItAdapter(),
        "kalshi": KalshiAdapter(),
    }

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="search_markets",
                description="Search for prediction markets across platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'Will Trump win 2024?')",
                        },
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: filter to specific platforms",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_market_odds",
                description="Get current odds for a specific market",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Platform name (manifold, polymarket, etc.)",
                        },
                        "market_id": {
                            "type": "string",
                            "description": "The market's native ID",
                        },
                    },
                    "required": ["platform", "market_id"],
                },
            ),
            Tool(
                name="list_categories",
                description="List available market categories",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="browse_category",
                description="Browse markets in a specific category",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to browse",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max markets to return (default 20)",
                            "default": 20,
                        },
                    },
                    "required": ["category"],
                },
            ),
            Tool(
                name="track_market",
                description="Add a market to your tracking watchlist",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Platform name (manifold, polymarket, etc.)",
                        },
                        "market_id": {
                            "type": "string",
                            "description": "The market's native ID",
                        },
                        "alias": {
                            "type": "string",
                            "description": "Optional friendly name for the market",
                        },
                    },
                    "required": ["platform", "market_id"],
                },
            ),
            Tool(
                name="get_tracked_markets",
                description="Get all markets in your watchlist with current prices",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="find_arbitrage",
                description="Find price discrepancies across platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "min_spread": {
                            "type": "number",
                            "description": "Minimum probability difference to report (default 0.05)",
                            "default": 0.05,
                        },
                    },
                },
            ),
            Tool(
                name="compare_platforms",
                description="Side-by-side odds comparison for markets matching a query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to find markets to compare",
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    handlers = ToolHandlers(adapters)

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        if name == "search_markets":
            result = await handlers.search_markets(**arguments)
        elif name == "get_market_odds":
            result = await handlers.get_market_odds(**arguments)
        elif name == "list_categories":
            result = await handlers.list_categories()
        elif name == "browse_category":
            result = await handlers.browse_category(**arguments)
        elif name == "track_market":
            result = await handlers.track_market(**arguments)
        elif name == "get_tracked_markets":
            result = await handlers.get_tracked_markets()
        elif name == "find_arbitrage":
            result = await handlers.find_arbitrage(**arguments)
        elif name == "compare_platforms":
            result = await handlers.compare_platforms(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    return server


def main() -> None:
    """Run the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    server = create_server()

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
