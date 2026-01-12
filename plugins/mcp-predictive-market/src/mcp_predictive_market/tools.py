"""Tool handler implementations for the MCP server."""
from datetime import datetime, timezone
from typing import Any

from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.analysis.arbitrage import ArbitrageDetector
from mcp_predictive_market.analysis.matching import MarketMatcher
from mcp_predictive_market.errors import PlatformError
from mcp_predictive_market.schema import Market


class ToolHandlers:
    """Handlers for MCP tool calls."""

    def __init__(self, adapters: dict[str, PlatformAdapter]) -> None:
        """Initialize with platform adapters."""
        self._adapters = adapters
        self._tracked_markets: dict[str, dict] = {}  # market_id -> market info
        self._matcher = MarketMatcher()
        self._arbitrage_detector = ArbitrageDetector(self._matcher)

    def _market_to_dict(self, market: Market) -> dict[str, Any]:
        """Convert a Market object to a JSON-serializable dictionary."""
        return {
            "id": market.id,
            "platform": market.platform,
            "native_id": market.native_id,
            "url": market.url,
            "title": market.title,
            "description": market.description,
            "category": market.category,
            "probability": market.probability,
            "volume": market.volume,
            "resolved": market.resolved,
            "resolution": market.resolution,
            "last_fetched": market.last_fetched.isoformat(),
        }

    async def search_markets(
        self,
        query: str,
        platforms: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search for markets across platforms."""
        target_adapters = self._adapters
        if platforms:
            target_adapters = {
                k: v for k, v in self._adapters.items() if k in platforms
            }

        all_markets = []
        errors = []

        for name, adapter in target_adapters.items():
            try:
                markets = await adapter.search_markets(query)
                all_markets.extend(markets)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        return {
            "markets": [self._market_to_dict(m) for m in all_markets],
            "errors": errors,
        }

    async def get_market_odds(
        self,
        platform: str,
        market_id: str,
    ) -> dict[str, Any]:
        """Get current odds for a specific market."""
        if platform not in self._adapters:
            raise ValueError(f"Unknown platform: {platform}")

        adapter = self._adapters[platform]
        market = await adapter.get_market(market_id)
        return self._market_to_dict(market)

    async def list_categories(self) -> dict[str, Any]:
        """List available categories across platforms."""
        all_categories: set[str] = set()
        errors = []

        for name, adapter in self._adapters.items():
            try:
                categories = await adapter.list_categories()
                all_categories.update(categories)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        return {"categories": sorted(all_categories), "errors": errors}

    async def browse_category(
        self,
        category: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Browse markets in a category."""
        all_markets = []
        errors = []

        for name, adapter in self._adapters.items():
            try:
                markets = await adapter.browse_category(category, limit)
                all_markets.extend(markets)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        # Sort by volume (highest first) and limit
        all_markets.sort(key=lambda m: m.volume or 0, reverse=True)
        all_markets = all_markets[:limit]

        return {
            "markets": [self._market_to_dict(m) for m in all_markets],
            "errors": errors,
        }

    async def track_market(
        self,
        platform: str,
        market_id: str,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """Add a market to the tracking watchlist."""
        if platform not in self._adapters:
            raise ValueError(f"Unknown platform: {platform}")

        adapter = self._adapters[platform]
        market = await adapter.get_market(market_id)

        full_id = f"{platform}:{market_id}"
        self._tracked_markets[full_id] = {
            "market": self._market_to_dict(market),
            "alias": alias,
            "tracked_at": datetime.now(timezone.utc).isoformat(),
        }

        return {
            "status": "tracked",
            "market_id": full_id,
            "alias": alias,
            "market": self._market_to_dict(market),
        }

    async def get_tracked_markets(self) -> dict[str, Any]:
        """Get all tracked markets with current data."""
        results = []
        errors = []

        for full_id, info in self._tracked_markets.items():
            platform, native_id = full_id.split(":", 1)
            try:
                adapter = self._adapters[platform]
                market = await adapter.get_market(native_id)
                results.append({
                    "market": self._market_to_dict(market),
                    "alias": info.get("alias"),
                    "tracked_at": info.get("tracked_at"),
                })
            except Exception as e:
                errors.append({"market_id": full_id, "error": str(e)})

        return {"tracked_markets": results, "errors": errors}

    async def find_arbitrage(
        self,
        min_spread: float = 0.05,
    ) -> dict[str, Any]:
        """Find arbitrage opportunities across platforms."""
        # Fetch markets from all platforms
        all_markets = []
        errors = []

        for name, adapter in self._adapters.items():
            try:
                # Get some markets to compare
                markets = await adapter.search_markets("")  # Get recent/popular
                all_markets.extend(markets)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        # Find opportunities
        opportunities = self._arbitrage_detector.find_arbitrage(
            all_markets, min_spread=min_spread
        )

        return {
            "opportunities": [
                {
                    "market_a": self._market_to_dict(o.market_a),
                    "market_b": self._market_to_dict(o.market_b),
                    "spread": o.spread,
                    "match_confidence": o.match_confidence,
                    "direction": o.direction,
                }
                for o in opportunities
            ],
            "errors": errors,
        }

    async def compare_platforms(
        self,
        query: str,
    ) -> dict[str, Any]:
        """Side-by-side comparison of markets matching a query."""
        # Search across all platforms
        all_markets = []
        errors = []

        for name, adapter in self._adapters.items():
            try:
                markets = await adapter.search_markets(query)
                all_markets.extend(markets)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        # Compare
        result = self._arbitrage_detector.compare_platforms(all_markets)
        result["errors"] = errors

        return result
