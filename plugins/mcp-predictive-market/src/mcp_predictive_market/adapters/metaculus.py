"""Metaculus platform adapter."""
from datetime import datetime, timezone

import httpx

from mcp_predictive_market.schema import Market, Outcome


class MetaculusAdapter:
    """Adapter for Metaculus API."""

    platform = "metaculus"
    BASE_URL = "https://www.metaculus.com/api2"

    # Map Metaculus category names to normalized categories
    CATEGORY_MAP = {
        "ai": "ai",
        "artificial intelligence": "ai",
        "technology": "technology",
        "tech": "technology",
        "science": "science",
        "biology": "science",
        "physics": "science",
        "space": "science",
        "crypto": "crypto",
        "cryptocurrency": "crypto",
        "bitcoin": "crypto",
        "finance": "finance",
        "economics": "economics",
        "politics": "politics",
        "geopolitics": "politics",
        "sports": "sports",
        "entertainment": "entertainment",
        "health": "health",
        "medicine": "health",
        "climate": "science",
        "environment": "science",
    }

    def __init__(self) -> None:
        """Initialize the adapter with an HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by ID."""
        response = await self._client.get(f"{self.BASE_URL}/questions/{native_id}/")
        response.raise_for_status()
        data = response.json()
        return self._parse_market(data)

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query."""
        params = {
            "search": query,
            "limit": 20,
        }
        response = await self._client.get(f"{self.BASE_URL}/questions/", params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        return [self._parse_market(q) for q in results]

    async def list_categories(self) -> list[str]:
        """List available categories (normalized)."""
        return sorted(set(self.CATEGORY_MAP.values()))

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a category."""
        # Metaculus doesn't have a direct category filter in the API,
        # so we fetch questions and filter by category
        params = {"limit": limit}
        response = await self._client.get(f"{self.BASE_URL}/questions/", params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        markets = []
        for q in results:
            market = self._parse_market(q)
            if market.category == category:
                markets.append(market)
                if len(markets) >= limit:
                    break
        return markets

    def _parse_market(self, data: dict) -> Market:
        """Parse Metaculus API response into Market schema."""
        # Determine category from categories array
        category = "other"
        for cat in data.get("categories", []):
            cat_name = cat.get("name", "").lower()
            if cat_name in self.CATEGORY_MAP:
                category = self.CATEGORY_MAP[cat_name]
                break

        # Parse timestamps (ISO format)
        created_at = datetime.now(timezone.utc)
        if data.get("created_time"):
            created_at = datetime.fromisoformat(
                data["created_time"].replace("Z", "+00:00")
            )

        closes_at = None
        if data.get("close_time"):
            closes_at = datetime.fromisoformat(
                data["close_time"].replace("Z", "+00:00")
            )

        # Get probability from community_prediction.full.q2 (median)
        probability = 0.5
        community_prediction = data.get("community_prediction")
        if community_prediction and community_prediction.get("full"):
            q2 = community_prediction["full"].get("q2")
            if q2 is not None:
                probability = float(q2)

        # Build outcomes for binary questions
        outcomes = [
            Outcome(name="Yes", probability=probability),
            Outcome(name="No", probability=1 - probability),
        ]

        # Check if resolved
        resolved = data.get("active_state") == "RESOLVED"
        resolution = None
        if data.get("resolution") is not None:
            resolution = str(data["resolution"])

        return Market(
            platform=self.platform,
            native_id=str(data["id"]),
            url=data.get("page_url", f"https://www.metaculus.com/questions/{data['id']}/"),
            title=data["title"],
            description=data.get("description", ""),
            category=category,
            probability=probability,
            outcomes=outcomes,
            volume=None,  # Metaculus doesn't expose trading volume
            liquidity=None,  # Metaculus doesn't have liquidity concept
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
