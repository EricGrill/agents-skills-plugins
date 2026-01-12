"""Kalshi platform adapter."""
from datetime import datetime, timezone

import httpx

from mcp_predictive_market.schema import Market, Outcome


class KalshiAdapter:
    """Adapter for Kalshi API."""

    platform = "kalshi"
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    # Known categories from Kalshi (normalized to lowercase)
    CATEGORIES = [
        "politics",
        "crypto",
        "economics",
        "science",
        "entertainment",
        "sports",
        "technology",
    ]

    def __init__(self) -> None:
        """Initialize the adapter with an HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by ticker."""
        response = await self._client.get(f"{self.BASE_URL}/markets/{native_id}")
        response.raise_for_status()
        data = response.json()
        return self._parse_market(data["market"])

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query.

        Uses ticker parameter to search markets.
        """
        params = {"ticker": query}
        response = await self._client.get(f"{self.BASE_URL}/markets", params=params)
        response.raise_for_status()
        data = response.json()

        markets = data.get("markets", [])
        results = []
        for m in markets:
            market = self._parse_market(m)
            if category is None or market.category == category:
                results.append(market)
                if len(results) >= 20:
                    break

        return results

    async def list_categories(self) -> list[str]:
        """List available categories."""
        return sorted(self.CATEGORIES)

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a category.

        Fetches active markets and filters by category.
        """
        params = {"limit": limit, "status": "active"}
        response = await self._client.get(f"{self.BASE_URL}/markets", params=params)
        response.raise_for_status()
        data = response.json()

        markets = data.get("markets", [])
        results = []
        for m in markets:
            market = self._parse_market(m)
            if market.category == category:
                results.append(market)
                if len(results) >= limit:
                    break

        return results

    def _parse_market(self, data: dict) -> Market:
        """Parse Kalshi API response into Market schema."""
        # Get probability from yes_ask (in cents, 0-100), fall back to last_price
        probability = 0.5
        yes_ask = data.get("yes_ask")
        last_price = data.get("last_price")

        if yes_ask is not None:
            probability = yes_ask / 100.0
        elif last_price is not None:
            probability = last_price / 100.0

        # Ensure probability is in valid range
        probability = max(0.0, min(1.0, probability))

        # Build Yes/No outcomes (Kalshi markets are binary)
        outcomes = [
            Outcome(name="Yes", probability=probability),
            Outcome(name="No", probability=1.0 - probability),
        ]

        # Normalize category to lowercase
        category = (data.get("category") or "other").lower()

        # Parse timestamps
        created_at = datetime.now(timezone.utc)
        closes_at = None
        if data.get("close_time"):
            closes_at = datetime.fromisoformat(
                data["close_time"].replace("Z", "+00:00")
            )

        # Check if resolved (status is finalized or result is set)
        resolved = data.get("status") == "finalized" or data.get("result") is not None
        resolution = data.get("result")

        ticker = data["ticker"]

        return Market(
            platform=self.platform,
            native_id=ticker,
            url=f"https://kalshi.com/markets/{ticker}",
            title=data["title"],
            description=data.get("subtitle", ""),
            category=category,
            probability=probability,
            outcomes=outcomes,
            volume=float(data.get("volume", 0) or 0),
            liquidity=None,  # Kalshi uses open_interest instead
            created_at=created_at,
            closes_at=closes_at,
            resolved=resolved,
            resolution=resolution,
            last_fetched=datetime.now(timezone.utc),
            price_history=[],
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
