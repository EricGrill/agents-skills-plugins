"""PredictIt platform adapter."""
from datetime import datetime, timezone

import httpx

from mcp_predictive_market.schema import Market, Outcome


class PredictItAdapter:
    """Adapter for PredictIt API."""

    platform = "predictit"
    BASE_URL = "https://www.predictit.org/api/marketdata"

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
        """Search for markets matching a query.

        PredictIt doesn't have a search endpoint, so we fetch all markets
        and filter client-side.
        """
        response = await self._client.get(f"{self.BASE_URL}/all/")
        response.raise_for_status()
        data = response.json()

        markets = data.get("markets", [])
        query_lower = query.lower()

        results = []
        for m in markets:
            name = m.get("name", "").lower()
            short_name = m.get("shortName", "").lower()
            if query_lower in name or query_lower in short_name:
                results.append(self._parse_market(m))
                if len(results) >= 20:
                    break

        return results

    async def list_categories(self) -> list[str]:
        """List available categories.

        PredictIt is politics-focused, so we return just politics.
        """
        return ["politics"]

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a category.

        All PredictIt markets are politics-related.
        """
        if category != "politics":
            return []

        response = await self._client.get(f"{self.BASE_URL}/all/")
        response.raise_for_status()
        data = response.json()

        markets = data.get("markets", [])
        results = []
        for m in markets:
            if m.get("status") == "Open":
                results.append(self._parse_market(m))
                if len(results) >= limit:
                    break

        return results

    def _parse_market(self, data: dict) -> Market:
        """Parse PredictIt API response into Market schema."""
        contracts = data.get("contracts", [])

        # Get probability from first contract's lastTradePrice or bestBuyYesCost
        probability = 0.5
        if contracts:
            first_contract = contracts[0]
            last_trade = first_contract.get("lastTradePrice")
            if last_trade is not None:
                probability = float(last_trade)
            else:
                # Fall back to bestBuyYesCost
                best_buy = first_contract.get("bestBuyYesCost")
                if best_buy is not None:
                    probability = float(best_buy)

        # Build outcomes from contracts
        outcomes = []
        for contract in contracts:
            contract_name = contract.get("name", "Unknown")
            contract_price = contract.get("lastTradePrice")
            if contract_price is None:
                contract_price = contract.get("bestBuyYesCost", 0.5)
            if contract_price is None:
                contract_price = 0.5
            outcomes.append(
                Outcome(name=contract_name, probability=float(contract_price))
            )

        # Check if resolved (status is Closed)
        resolved = data.get("status") == "Closed"

        # All PredictIt markets are politics
        category = "politics"

        return Market(
            platform=self.platform,
            native_id=str(data["id"]),
            url=data.get("url", f"https://www.predictit.org/markets/detail/{data['id']}"),
            title=data["name"],
            description="",  # PredictIt API doesn't include description
            category=category,
            probability=probability,
            outcomes=outcomes,
            volume=None,  # PredictIt doesn't expose volume in API
            liquidity=None,  # PredictIt doesn't expose liquidity
            created_at=datetime.now(timezone.utc),  # Not provided by API
            closes_at=None,  # Not provided by API
            resolved=resolved,
            resolution=None,
            last_fetched=datetime.now(timezone.utc),
            price_history=[],
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
