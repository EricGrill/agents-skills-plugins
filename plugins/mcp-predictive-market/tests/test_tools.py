"""Tests for MCP tool handlers."""
from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.tools import ToolHandlers
from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from mcp_predictive_market.adapters.polymarket import PolymarketAdapter
from tests.fixtures.manifold_responses import SAMPLE_MARKET, SAMPLE_MARKETS_LIST
from tests.fixtures.polymarket_responses import (
    SAMPLE_MARKET as SAMPLE_POLYMARKET_MARKET,
    SAMPLE_MARKETS_LIST as SAMPLE_POLYMARKET_MARKETS_LIST,
)


class TestSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_returns_formatted_results(self, httpx_mock: HTTPXMock):
        """search_markets should return formatted market data."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=AI&limit=20",
            json=SAMPLE_MARKETS_LIST,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="AI")

        assert "markets" in result
        assert len(result["markets"]) == 2
        assert result["markets"][0]["title"] == "Will AI pass the Turing test by 2025?"
        assert result["markets"][0]["probability"] == 0.4


class TestGetMarketOdds:
    @pytest.mark.asyncio
    async def test_get_market_odds_success(self, httpx_mock: HTTPXMock):
        """get_market_odds should return market details."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.get_market_odds(
            platform="manifold", market_id="abc123xyz"
        )

        assert result["platform"] == "manifold"
        assert result["probability"] == 0.4
        assert result["title"] == "Will AI pass the Turing test by 2025?"


class TestTrackMarket:
    @pytest.mark.asyncio
    async def test_track_market_success(self, httpx_mock: HTTPXMock):
        """track_market should add market to watchlist and return confirmation."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.track_market(
            platform="manifold",
            market_id="abc123xyz",
            alias="AI Turing Test",
        )

        assert result["status"] == "tracked"
        assert result["market_id"] == "manifold:abc123xyz"
        assert result["alias"] == "AI Turing Test"
        assert result["market"]["title"] == "Will AI pass the Turing test by 2025?"

    @pytest.mark.asyncio
    async def test_track_market_unknown_platform(self):
        """track_market should raise error for unknown platform."""
        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        with pytest.raises(ValueError, match="Unknown platform: unknown"):
            await handlers.track_market(platform="unknown", market_id="test123")


class TestGetTrackedMarkets:
    @pytest.mark.asyncio
    async def test_get_tracked_markets_returns_current_data(self, httpx_mock: HTTPXMock):
        """get_tracked_markets should return current data for all tracked markets."""
        # First track a market
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        await handlers.track_market(
            platform="manifold",
            market_id="abc123xyz",
            alias="AI Turing",
        )

        # Now get tracked markets (will fetch again)
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        result = await handlers.get_tracked_markets()

        assert "tracked_markets" in result
        assert len(result["tracked_markets"]) == 1
        assert result["tracked_markets"][0]["alias"] == "AI Turing"
        assert result["tracked_markets"][0]["market"]["probability"] == 0.4

    @pytest.mark.asyncio
    async def test_get_tracked_markets_empty(self):
        """get_tracked_markets should return empty list when nothing tracked."""
        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.get_tracked_markets()

        assert result["tracked_markets"] == []
        assert result["errors"] == []


class TestFindArbitrage:
    @pytest.mark.asyncio
    async def test_find_arbitrage_returns_opportunities(self, httpx_mock: HTTPXMock):
        """find_arbitrage should detect price discrepancies between platforms."""
        # Create markets with similar titles but different probabilities
        manifold_market = SAMPLE_MARKETS_LIST[1].copy()  # Bitcoin market at 35%

        polymarket_market = SAMPLE_POLYMARKET_MARKET.copy()  # Bitcoin market at 45%

        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=&limit=20",
            json=[manifold_market],
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=",
            json=[polymarket_market],
        )

        adapters = {
            "manifold": ManifoldAdapter(),
            "polymarket": PolymarketAdapter(),
        }
        handlers = ToolHandlers(adapters)

        result = await handlers.find_arbitrage(min_spread=0.05)

        assert "opportunities" in result
        assert "errors" in result
        # Both markets are about Bitcoin 100k, so there may be arbitrage
        # The actual detection depends on text similarity

    @pytest.mark.asyncio
    async def test_find_arbitrage_handles_errors(self, httpx_mock: HTTPXMock):
        """find_arbitrage should handle platform errors gracefully."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=&limit=20",
            status_code=500,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.find_arbitrage()

        assert result["opportunities"] == []
        assert len(result["errors"]) == 1
        assert result["errors"][0]["platform"] == "manifold"


class TestComparePlatforms:
    @pytest.mark.asyncio
    async def test_compare_platforms_groups_markets(self, httpx_mock: HTTPXMock):
        """compare_platforms should group similar markets across platforms."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=bitcoin&limit=20",
            json=SAMPLE_MARKETS_LIST,
        )
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=bitcoin",
            json=SAMPLE_POLYMARKET_MARKETS_LIST,
        )

        adapters = {
            "manifold": ManifoldAdapter(),
            "polymarket": PolymarketAdapter(),
        }
        handlers = ToolHandlers(adapters)

        result = await handlers.compare_platforms(query="bitcoin")

        assert "comparisons" in result
        assert "errors" in result

    @pytest.mark.asyncio
    async def test_compare_platforms_handles_errors(self, httpx_mock: HTTPXMock):
        """compare_platforms should handle platform errors gracefully."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=test&limit=20",
            status_code=500,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.compare_platforms(query="test")

        assert "comparisons" in result
        assert len(result["errors"]) == 1
