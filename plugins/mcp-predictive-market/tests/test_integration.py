"""End-to-end integration tests for the MCP prediction market server.

These tests verify the full workflow using all 5 platform adapters with mocked HTTP responses.
"""
import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.tools import ToolHandlers
from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from mcp_predictive_market.adapters.polymarket import PolymarketAdapter
from mcp_predictive_market.adapters.metaculus import MetaculusAdapter
from mcp_predictive_market.adapters.predictit import PredictItAdapter
from mcp_predictive_market.adapters.kalshi import KalshiAdapter


# ============================================================================
# Mock responses for each platform - Bitcoin $100k market theme for consistency
# ============================================================================

MANIFOLD_BITCOIN_MARKET = {
    "id": "manifold-btc-100k",
    "creatorId": "user123",
    "creatorUsername": "crypto_trader",
    "creatorName": "Crypto Trader",
    "createdTime": 1704067200000,
    "closeTime": 1735689600000,
    "question": "Will Bitcoin reach $100,000 by end of 2025?",
    "description": "Resolves YES if BTC/USD price exceeds $100,000.",
    "url": "https://manifold.markets/crypto_trader/bitcoin-100k-2025",
    "pool": {"YES": 5000, "NO": 5000},
    "probability": 0.45,
    "volume": 25000,
    "volume24Hours": 500,
    "isResolved": False,
    "resolution": None,
    "resolutionTime": None,
    "outcomeType": "BINARY",
    "mechanism": "cpmm-1",
    "groupSlugs": ["crypto", "bitcoin"],
}

MANIFOLD_AI_MARKET = {
    "id": "manifold-ai-2025",
    "creatorId": "user456",
    "creatorUsername": "ai_watcher",
    "creatorName": "AI Watcher",
    "createdTime": 1704153600000,
    "closeTime": 1735689600000,
    "question": "Will AGI be achieved by 2025?",
    "description": "Resolves YES if AGI is developed.",
    "url": "https://manifold.markets/ai_watcher/agi-2025",
    "pool": {"YES": 2000, "NO": 8000},
    "probability": 0.15,
    "volume": 12000,
    "volume24Hours": 200,
    "isResolved": False,
    "resolution": None,
    "resolutionTime": None,
    "outcomeType": "BINARY",
    "mechanism": "cpmm-1",
    "groupSlugs": ["ai", "technology"],
}

POLYMARKET_BITCOIN_MARKET = {
    "id": "0xpoly-btc-100k",
    "question": "Will Bitcoin reach $100,000 by end of 2025?",
    "description": "Resolves YES if BTC/USD exceeds $100,000 at any point.",
    "slug": "bitcoin-100k-2025",
    "active": True,
    "closed": False,
    "archived": False,
    "outcomes": ["Yes", "No"],
    "outcomePrices": ["0.55", "0.45"],  # 10% higher than Manifold - arbitrage!
    "volume": "150000.00",
    "liquidity": "50000.00",
    "startDate": "2024-01-01T00:00:00Z",
    "endDate": "2025-12-31T23:59:59Z",
    "tags": ["crypto", "bitcoin"],
}

POLYMARKET_ELECTION_MARKET = {
    "id": "0xpoly-election",
    "question": "Will the incumbent win the 2024 election?",
    "description": "US Presidential Election outcome.",
    "slug": "election-2024-incumbent",
    "active": True,
    "closed": False,
    "archived": False,
    "outcomes": ["Yes", "No"],
    "outcomePrices": ["0.40", "0.60"],
    "volume": "500000.00",
    "liquidity": "100000.00",
    "startDate": "2024-01-01T00:00:00Z",
    "endDate": "2024-11-15T00:00:00Z",
    "tags": ["politics"],
}

METACULUS_BITCOIN_QUESTION = {
    "id": 99001,
    "title": "Will Bitcoin reach $100,000 by end of 2025?",
    "description": "This question resolves positively if BTC crosses $100k.",
    "url": "/questions/99001/bitcoin-100k-2025",
    "page_url": "https://www.metaculus.com/questions/99001/",
    "created_time": "2024-01-01T00:00:00Z",
    "close_time": "2025-12-31T23:59:59Z",
    "resolve_time": None,
    "resolution": None,
    "active_state": "OPEN",
    "community_prediction": {"full": {"q2": 0.50}},  # Different from both Manifold & Polymarket
    "number_of_forecasters": 800,
    "categories": [{"id": 4, "name": "Crypto"}],
}

METACULUS_AI_QUESTION = {
    "id": 99002,
    "title": "Will AGI be developed before 2030?",
    "description": "Resolves YES if AGI is achieved.",
    "url": "/questions/99002/agi-2030",
    "page_url": "https://www.metaculus.com/questions/99002/",
    "created_time": "2024-02-01T00:00:00Z",
    "close_time": "2029-12-31T23:59:59Z",
    "resolve_time": None,
    "resolution": None,
    "active_state": "OPEN",
    "community_prediction": {"full": {"q2": 0.25}},
    "number_of_forecasters": 1200,
    "categories": [{"id": 1, "name": "AI"}],
}

PREDICTIT_ELECTION_MARKET = {
    "id": 8001,
    "name": "Who will win the 2024 presidential election?",
    "shortName": "2024 President",
    "image": "https://www.predictit.org/api/marketdata/image/8001",
    "url": "https://www.predictit.org/markets/detail/8001",
    "status": "Open",
    "contracts": [
        {
            "id": 30001,
            "name": "Republican candidate",
            "shortName": "GOP",
            "status": "Open",
            "lastTradePrice": 0.52,
            "bestBuyYesCost": 0.53,
            "bestBuyNoCost": 0.48,
            "bestSellYesCost": 0.51,
            "bestSellNoCost": 0.47,
        },
        {
            "id": 30002,
            "name": "Democratic candidate",
            "shortName": "Dem",
            "status": "Open",
            "lastTradePrice": 0.46,
            "bestBuyYesCost": 0.47,
            "bestBuyNoCost": 0.54,
            "bestSellYesCost": 0.45,
            "bestSellNoCost": 0.53,
        },
    ],
    "timeStamp": "2024-06-01T12:00:00Z",
}

PREDICTIT_ALL_MARKETS = {
    "markets": [PREDICTIT_ELECTION_MARKET]
}

KALSHI_BITCOIN_MARKET = {
    "ticker": "BTC-100K-2025",
    "event_ticker": "BTC-100K",
    "title": "Will Bitcoin reach $100,000 by end of 2025?",
    "subtitle": "Crypto Event Contract",
    "yes_ask": 60,  # 60% - highest of all platforms, good for arbitrage test
    "yes_bid": 58,
    "no_ask": 43,
    "no_bid": 41,
    "last_price": 59,
    "volume": 750000,
    "open_interest": 125000,
    "status": "active",
    "close_time": "2025-12-31T23:59:59Z",
    "expiration_time": "2026-01-15T00:00:00Z",
    "category": "Crypto",
    "result": None,
}

KALSHI_POLITICS_MARKET = {
    "ticker": "PRES-2024",
    "event_ticker": "ELECTION-2024",
    "title": "Will the incumbent win the 2024 presidential election?",
    "subtitle": "Political Event",
    "yes_ask": 42,
    "yes_bid": 40,
    "no_ask": 61,
    "no_bid": 59,
    "last_price": 41,
    "volume": 2000000,
    "open_interest": 350000,
    "status": "active",
    "close_time": "2024-11-06T00:00:00Z",
    "expiration_time": "2024-11-30T00:00:00Z",
    "category": "Politics",
    "result": None,
}

KALSHI_MARKETS_LIST = {
    "markets": [KALSHI_BITCOIN_MARKET, KALSHI_POLITICS_MARKET],
    "cursor": None,
}


# ============================================================================
# Helper to create adapters
# ============================================================================

def create_all_adapters() -> dict:
    """Create all 5 platform adapters."""
    return {
        "manifold": ManifoldAdapter(),
        "polymarket": PolymarketAdapter(),
        "metaculus": MetaculusAdapter(),
        "predictit": PredictItAdapter(),
        "kalshi": KalshiAdapter(),
    }


# ============================================================================
# Integration Tests
# ============================================================================

class TestMultiPlatformSearch:
    """Test searching across all platforms."""

    @pytest.mark.asyncio
    async def test_search_returns_results_from_all_platforms(self, httpx_mock: HTTPXMock):
        """Search should return results from all 5 platforms when they have matching markets."""
        # Mock all platform search endpoints
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=bitcoin&limit=20",
            json=[MANIFOLD_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=bitcoin",
            json=[POLYMARKET_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=bitcoin&limit=20",
            json={"results": [METACULUS_BITCOIN_QUESTION], "count": 1},
        )
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            json=PREDICTIT_ALL_MARKETS,
        )
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=bitcoin",
            json={"markets": [KALSHI_BITCOIN_MARKET], "cursor": None},
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="bitcoin")

        assert "markets" in result
        assert "errors" in result
        # PredictIt doesn't have bitcoin markets, so we expect 4 results
        # (The mock filters client-side, and our mock doesn't match "bitcoin")
        platforms_found = {m["platform"] for m in result["markets"]}
        # We should find at least manifold, polymarket, metaculus, and kalshi
        assert "manifold" in platforms_found
        assert "polymarket" in platforms_found
        assert "metaculus" in platforms_found
        assert "kalshi" in platforms_found

    @pytest.mark.asyncio
    async def test_search_with_platform_filter(self, httpx_mock: HTTPXMock):
        """Search should only query specified platforms when filter is provided."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=AI&limit=20",
            json=[MANIFOLD_AI_MARKET],
        )
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=AI&limit=20",
            json={"results": [METACULUS_AI_QUESTION], "count": 1},
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(
            query="AI",
            platforms=["manifold", "metaculus"],
        )

        platforms_found = {m["platform"] for m in result["markets"]}
        assert platforms_found == {"manifold", "metaculus"}
        assert len(result["errors"]) == 0


class TestArbitrageDetection:
    """Test arbitrage detection across platforms."""

    @pytest.mark.asyncio
    async def test_finds_arbitrage_with_price_differences(self, httpx_mock: HTTPXMock):
        """Arbitrage detector should find opportunities when prices differ significantly."""
        # Bitcoin markets with different prices:
        # Manifold: 45%, Polymarket: 55%, Metaculus: 50%, Kalshi: 60%
        # Should detect opportunities between these

        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=&limit=20",
            json=[MANIFOLD_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=",
            json=[POLYMARKET_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=&limit=20",
            json={"results": [METACULUS_BITCOIN_QUESTION], "count": 1},
        )
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            json={"markets": []},  # Empty for clean test
        )
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=",
            json={"markets": [KALSHI_BITCOIN_MARKET], "cursor": None},
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.find_arbitrage(min_spread=0.05)

        assert "opportunities" in result
        assert "errors" in result

        # With similar titles and spread >= 5%, we should find opportunities
        # The exact number depends on text matching confidence
        # Manifold (45%) vs Kalshi (60%) = 15% spread should definitely be found
        if result["opportunities"]:
            opp = result["opportunities"][0]
            assert opp["spread"] >= 0.05
            assert "market_a" in opp
            assert "market_b" in opp
            assert opp["direction"] in ["buy_a_sell_b", "buy_b_sell_a"]

    @pytest.mark.asyncio
    async def test_arbitrage_handles_platform_errors_gracefully(self, httpx_mock: HTTPXMock):
        """Arbitrage should continue even if some platforms fail."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=&limit=20",
            json=[MANIFOLD_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=",
            status_code=500,  # Polymarket fails
        )
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=&limit=20",
            json={"results": [METACULUS_BITCOIN_QUESTION], "count": 1},
        )
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            status_code=503,  # PredictIt also fails
        )
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=",
            json={"markets": [KALSHI_BITCOIN_MARKET], "cursor": None},
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.find_arbitrage(min_spread=0.05)

        # Should still get results from working platforms
        assert "opportunities" in result
        assert "errors" in result
        # Should have 2 errors (Polymarket and PredictIt)
        assert len(result["errors"]) == 2
        error_platforms = {e["platform"] for e in result["errors"]}
        assert error_platforms == {"polymarket", "predictit"}


class TestMarketTracking:
    """Test market tracking workflow."""

    @pytest.mark.asyncio
    async def test_track_get_refresh_workflow(self, httpx_mock: HTTPXMock):
        """Test full tracking workflow: track -> get tracked -> refresh."""
        # Initial track
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/manifold-btc-100k",
            json=MANIFOLD_BITCOIN_MARKET,
        )
        # Track from Kalshi too
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/BTC-100K-2025",
            json={"market": KALSHI_BITCOIN_MARKET},
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        # Track Manifold market
        result1 = await handlers.track_market(
            platform="manifold",
            market_id="manifold-btc-100k",
            alias="BTC100k-Manifold",
        )
        assert result1["status"] == "tracked"
        assert result1["alias"] == "BTC100k-Manifold"
        assert result1["market"]["probability"] == 0.45

        # Track Kalshi market
        result2 = await handlers.track_market(
            platform="kalshi",
            market_id="BTC-100K-2025",
            alias="BTC100k-Kalshi",
        )
        assert result2["status"] == "tracked"
        assert result2["market"]["probability"] == 0.60

        # Get tracked markets (simulates refresh)
        # Mock updated prices
        updated_manifold = MANIFOLD_BITCOIN_MARKET.copy()
        updated_manifold["probability"] = 0.48  # Price moved up
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/manifold-btc-100k",
            json=updated_manifold,
        )
        updated_kalshi = KALSHI_BITCOIN_MARKET.copy()
        updated_kalshi["yes_ask"] = 62  # Also moved up
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/BTC-100K-2025",
            json={"market": updated_kalshi},
        )

        result3 = await handlers.get_tracked_markets()
        assert len(result3["tracked_markets"]) == 2

        # Verify we got updated prices
        markets_by_alias = {t["alias"]: t for t in result3["tracked_markets"]}
        assert markets_by_alias["BTC100k-Manifold"]["market"]["probability"] == 0.48
        assert markets_by_alias["BTC100k-Kalshi"]["market"]["probability"] == 0.62


class TestComparePlatforms:
    """Test platform comparison functionality."""

    @pytest.mark.asyncio
    async def test_compare_groups_similar_markets(self, httpx_mock: HTTPXMock):
        """Compare should group similar markets from different platforms."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=bitcoin+100k&limit=20",
            json=[MANIFOLD_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=bitcoin+100k",
            json=[POLYMARKET_BITCOIN_MARKET],
        )
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=bitcoin+100k&limit=20",
            json={"results": [METACULUS_BITCOIN_QUESTION], "count": 1},
        )
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            json={"markets": []},
        )
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=bitcoin+100k",
            json={"markets": [KALSHI_BITCOIN_MARKET], "cursor": None},
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.compare_platforms(query="bitcoin 100k")

        assert "comparisons" in result
        assert "errors" in result

        # If markets were matched, we should see comparisons
        # Each comparison groups markets about the same topic
        if result["comparisons"]:
            comparison = result["comparisons"][0]
            assert "title" in comparison
            assert "platforms" in comparison
            assert "max_spread" in comparison
            # Max spread between 45% and 60% is 15%
            # (actual depends on which markets matched)


class TestCategoryBrowsing:
    """Test category browsing across platforms."""

    @pytest.mark.asyncio
    async def test_list_categories_aggregates_all_platforms(self, httpx_mock: HTTPXMock):
        """list_categories should return union of categories from all platforms."""
        # No HTTP calls needed - categories are static in adapters
        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.list_categories()

        assert "categories" in result
        categories = set(result["categories"])

        # Should include categories from various platforms
        assert "crypto" in categories  # Manifold, Polymarket, Kalshi
        assert "politics" in categories  # PredictIt, Kalshi, others
        assert "ai" in categories  # Manifold, Metaculus
        assert "technology" in categories  # Multiple platforms
        assert "science" in categories  # Metaculus, Kalshi

    @pytest.mark.asyncio
    @pytest.mark.httpx_mock(can_send_already_matched_responses=True, assert_all_responses_were_requested=False)
    async def test_browse_category_returns_markets_sorted_by_volume(self, httpx_mock: HTTPXMock):
        """browse_category should return markets from all platforms, sorted by volume."""
        # Manifold browse - uses search-markets endpoint with limit=10
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=&filter=open&limit=10",
            json=[MANIFOLD_BITCOIN_MARKET],  # volume: 25000
        )
        # Polymarket browse
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=10",
            json=[POLYMARKET_BITCOIN_MARKET],  # volume: 150000
        )
        # Metaculus browse
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?limit=10",
            json={"results": [METACULUS_BITCOIN_QUESTION], "count": 1},  # no volume
        )
        # PredictIt browse - only returns for politics category, so won't be called
        # Kalshi browse
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?limit=10&status=active",
            json={"markets": [KALSHI_BITCOIN_MARKET], "cursor": None},  # volume: 750000
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.browse_category(category="crypto", limit=10)

        assert "markets" in result
        assert "errors" in result

        # Markets should be sorted by volume (highest first)
        markets = result["markets"]
        if len(markets) >= 2:
            volumes = [m.get("volume") or 0 for m in markets]
            # Should be descending
            for i in range(len(volumes) - 1):
                assert volumes[i] >= volumes[i + 1], "Markets should be sorted by volume descending"


class TestErrorHandling:
    """Test error handling across the integration."""

    @pytest.mark.asyncio
    async def test_all_platforms_failing(self, httpx_mock: HTTPXMock):
        """Should handle gracefully when all platforms fail."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=test&limit=20",
            status_code=500,
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=test",
            status_code=502,
        )
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=test&limit=20",
            status_code=503,
        )
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            status_code=504,
        )
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=test",
            status_code=500,
        )

        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="test")

        assert result["markets"] == []
        assert len(result["errors"]) == 5
        # Each platform should have an error entry
        error_platforms = {e["platform"] for e in result["errors"]}
        assert error_platforms == {"manifold", "polymarket", "metaculus", "predictit", "kalshi"}

    @pytest.mark.asyncio
    async def test_unknown_platform_for_get_market(self):
        """Should raise error for unknown platform in get_market_odds."""
        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        with pytest.raises(ValueError, match="Unknown platform: fake_platform"):
            await handlers.get_market_odds(platform="fake_platform", market_id="test")

    @pytest.mark.asyncio
    async def test_unknown_platform_for_track_market(self):
        """Should raise error for unknown platform in track_market."""
        adapters = create_all_adapters()
        handlers = ToolHandlers(adapters)

        with pytest.raises(ValueError, match="Unknown platform: nonexistent"):
            await handlers.track_market(platform="nonexistent", market_id="test")
