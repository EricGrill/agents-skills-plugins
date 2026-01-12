"""Manifold Markets platform adapter."""
from datetime import datetime, timezone

import httpx

from mcp_predictive_market.schema import Market, Outcome


class ManifoldAdapter:
    """Adapter for Manifold Markets API."""

    platform = "manifold"
    BASE_URL = "https://api.manifold.markets/v0"

    # Map Manifold group slugs to normalized categories
    CATEGORY_MAP = {
        "politics": "politics",
        "us-politics": "politics",
        "world-politics": "politics",
        "sports": "sports",
        "crypto": "crypto",
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "ai": "ai",
        "technology": "technology",
        "science": "science",
        "economics": "economics",
        "finance": "finance",
        "entertainment": "entertainment",
        "gaming": "gaming",
    }

    def __init__(self) -> None:
        """Initialize the adapter with an HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by ID."""
        response = await self._client.get(f"{self.BASE_URL}/market/{native_id}")
        response.raise_for_status()
        data = response.json()
        return self._parse_market(data)

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query."""
        params = {"term": query, "limit": 20}
        response = await self._client.get(
            f"{self.BASE_URL}/search-markets", params=params
        )
        response.raise_for_status()
        data = response.json()
        return [self._parse_market(m) for m in data]

    async def list_categories(self) -> list[str]:
        """List available categories (normalized)."""
        return sorted(set(self.CATEGORY_MAP.values()))

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a category."""
        # Manifold uses group slugs, find matching ones
        slugs = [k for k, v in self.CATEGORY_MAP.items() if v == category]
        if not slugs:
            return []

        # Search with first matching slug as filter
        params = {"term": "", "filter": "open", "limit": limit}
        response = await self._client.get(
            f"{self.BASE_URL}/search-markets", params=params
        )
        response.raise_for_status()
        data = response.json()

        # Filter to matching categories
        markets = []
        for m in data:
            market = self._parse_market(m)
            if market.category == category:
                markets.append(market)
                if len(markets) >= limit:
                    break
        return markets

    def _parse_market(self, data: dict) -> Market:
        """Parse Manifold API response into Market schema."""
        # Determine category from group slugs
        category = "other"
        for slug in data.get("groupSlugs", []):
            if slug in self.CATEGORY_MAP:
                category = self.CATEGORY_MAP[slug]
                break

        # Parse timestamps (Manifold uses milliseconds)
        created_at = datetime.fromtimestamp(
            data["createdTime"] / 1000, tz=timezone.utc
        )
        closes_at = None
        if data.get("closeTime"):
            closes_at = datetime.fromtimestamp(
                data["closeTime"] / 1000, tz=timezone.utc
            )

        # Build outcomes for binary markets
        outcomes = []
        if data.get("outcomeType") == "BINARY":
            prob = data.get("probability", 0.5)
            outcomes = [
                Outcome(name="Yes", probability=prob),
                Outcome(name="No", probability=1 - prob),
            ]

        return Market(
            platform=self.platform,
            native_id=data["id"],
            url=data.get("url", f"https://manifold.markets/market/{data['id']}"),
            title=data["question"],
            description=data.get("description", ""),
            category=category,
            probability=data.get("probability", 0.5),
            outcomes=outcomes,
            volume=data.get("volume"),
            liquidity=None,  # Manifold doesn't expose this directly
            created_at=created_at,
            closes_at=closes_at,
            resolved=data.get("isResolved", False),
            resolution=data.get("resolution"),
            last_fetched=datetime.now(timezone.utc),
            price_history=[],
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
