"""Polymarket platform adapter."""
from datetime import datetime, timezone

import httpx

from mcp_predictive_market.schema import Market, Outcome


class PolymarketAdapter:
    """Adapter for Polymarket API."""

    platform = "polymarket"
    BASE_URL = "https://gamma-api.polymarket.com"

    CATEGORY_MAP = {
        "politics": "politics",
        "crypto": "crypto",
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "sports": "sports",
        "entertainment": "entertainment",
        "science": "science",
        "technology": "technology",
        "ai": "ai",
        "business": "economics",
        "finance": "finance",
    }

    def __init__(self) -> None:
        """Initialize the adapter with an HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by ID."""
        response = await self._client.get(f"{self.BASE_URL}/markets/{native_id}")
        response.raise_for_status()
        data = response.json()
        return self._parse_market(data)

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query."""
        params = {
            "active": "true",
            "closed": "false",
            "limit": 20,
            "title_like": query,
        }
        response = await self._client.get(f"{self.BASE_URL}/markets", params=params)
        response.raise_for_status()
        data = response.json()
        return [self._parse_market(m) for m in data]

    async def list_categories(self) -> list[str]:
        """List available categories (normalized)."""
        return sorted(set(self.CATEGORY_MAP.values()))

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a category."""
        tags = [k for k, v in self.CATEGORY_MAP.items() if v == category]
        if not tags:
            return []

        params = {"active": "true", "closed": "false", "limit": limit}
        response = await self._client.get(f"{self.BASE_URL}/markets", params=params)
        response.raise_for_status()
        data = response.json()

        markets = []
        for m in data:
            market = self._parse_market(m)
            if market.category == category:
                markets.append(market)
                if len(markets) >= limit:
                    break
        return markets

    def _parse_market(self, data: dict) -> Market:
        """Parse Polymarket API response into Market schema."""
        # Determine category from tags
        category = "other"
        for tag in data.get("tags", []):
            tag_lower = tag.lower()
            if tag_lower in self.CATEGORY_MAP:
                category = self.CATEGORY_MAP[tag_lower]
                break

        # Parse timestamps
        created_at = datetime.now(timezone.utc)
        if data.get("startDate"):
            created_at = datetime.fromisoformat(
                data["startDate"].replace("Z", "+00:00")
            )

        closes_at = None
        if data.get("endDate"):
            closes_at = datetime.fromisoformat(data["endDate"].replace("Z", "+00:00"))

        # Parse probability from outcomePrices (first outcome = Yes)
        probability = 0.5
        outcome_prices = data.get("outcomePrices", [])
        if outcome_prices and len(outcome_prices) >= 1:
            probability = float(outcome_prices[0])

        # Build outcomes
        outcomes = []
        outcome_names = data.get("outcomes", ["Yes", "No"])
        for i, name in enumerate(outcome_names):
            prob = float(outcome_prices[i]) if i < len(outcome_prices) else 0.5
            outcomes.append(Outcome(name=name, probability=prob))

        return Market(
            platform=self.platform,
            native_id=data["id"],
            url=f"https://polymarket.com/market/{data.get('slug', data['id'])}",
            title=data["question"],
            description=data.get("description", ""),
            category=category,
            probability=probability,
            outcomes=outcomes,
            volume=float(data.get("volume", 0) or 0),
            liquidity=float(data.get("liquidity", 0) or 0),
            created_at=created_at,
            closes_at=closes_at,
            resolved=data.get("closed", False) and not data.get("active", True),
            resolution=None,
            last_fetched=datetime.now(timezone.utc),
            price_history=[],
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
