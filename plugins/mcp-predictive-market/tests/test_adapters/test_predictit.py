"""Tests for PredictIt adapter."""
from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.adapters.predictit import PredictItAdapter
from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market
from tests.fixtures.predictit_responses import (
    SAMPLE_MARKET,
    SAMPLE_MARKET_BINARY,
    SAMPLE_MARKET_CLOSED,
    SAMPLE_MARKET_NO_TRADES,
    SAMPLE_ALL_MARKETS,
    SAMPLE_SEARCH_RESULTS,
)


class TestPredictItAdapter:
    def test_implements_protocol(self):
        """PredictItAdapter should implement PlatformAdapter protocol."""
        adapter = PredictItAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        """Platform name should be 'predictit'."""
        adapter = PredictItAdapter()
        assert adapter.platform == "predictit"


class TestPredictItGetMarket:
    @pytest.mark.asyncio
    async def test_get_market_success(self, httpx_mock: HTTPXMock):
        """Should fetch and parse a single market."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/markets/7456",
            json=SAMPLE_MARKET,
        )

        adapter = PredictItAdapter()
        market = await adapter.get_market("7456")

        assert isinstance(market, Market)
        assert market.platform == "predictit"
        assert market.native_id == "7456"
        assert market.title == "Who will win the 2024 presidential election?"
        assert market.probability == 0.55  # First contract's lastTradePrice
        assert market.category == "politics"
        assert market.url == "https://www.predictit.org/markets/detail/7456"

    @pytest.mark.asyncio
    async def test_get_market_binary(self, httpx_mock: HTTPXMock):
        """Should handle binary market with single contract."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/markets/7500",
            json=SAMPLE_MARKET_BINARY,
        )

        adapter = PredictItAdapter()
        market = await adapter.get_market("7500")

        assert isinstance(market, Market)
        assert market.probability == 0.72
        assert len(market.outcomes) == 1
        assert market.outcomes[0].name == "Yes"
        assert market.outcomes[0].probability == 0.72

    @pytest.mark.asyncio
    async def test_get_market_closed(self, httpx_mock: HTTPXMock):
        """Should correctly parse closed/resolved markets."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/markets/7100",
            json=SAMPLE_MARKET_CLOSED,
        )

        adapter = PredictItAdapter()
        market = await adapter.get_market("7100")

        assert isinstance(market, Market)
        assert market.resolved is True

    @pytest.mark.asyncio
    async def test_get_market_no_trades(self, httpx_mock: HTTPXMock):
        """Should handle markets with no lastTradePrice by using bestBuyYesCost."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/markets/7600",
            json=SAMPLE_MARKET_NO_TRADES,
        )

        adapter = PredictItAdapter()
        market = await adapter.get_market("7600")

        assert isinstance(market, Market)
        assert market.probability == 0.50  # Falls back to bestBuyYesCost


class TestPredictItSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_markets(self, httpx_mock: HTTPXMock):
        """Should search markets by query from all markets."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            json=SAMPLE_ALL_MARKETS,
        )

        adapter = PredictItAdapter()
        markets = await adapter.search_markets("president")

        assert len(markets) >= 1
        assert all(isinstance(m, Market) for m in markets)
        # Should find the presidential election market
        assert any("president" in m.title.lower() for m in markets)

    @pytest.mark.asyncio
    async def test_search_markets_empty(self, httpx_mock: HTTPXMock):
        """Should handle empty search results."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            json={"markets": []},
        )

        adapter = PredictItAdapter()
        markets = await adapter.search_markets("nonexistent")

        assert markets == []


class TestPredictItListCategories:
    @pytest.mark.asyncio
    async def test_list_categories(self):
        """Should return list with politics category."""
        adapter = PredictItAdapter()
        categories = await adapter.list_categories()

        assert isinstance(categories, list)
        assert len(categories) >= 1
        assert "politics" in categories


class TestPredictItBrowseCategory:
    @pytest.mark.asyncio
    async def test_browse_category(self, httpx_mock: HTTPXMock):
        """Should browse markets in a category."""
        httpx_mock.add_response(
            url="https://www.predictit.org/api/marketdata/all/",
            json=SAMPLE_ALL_MARKETS,
        )

        adapter = PredictItAdapter()
        markets = await adapter.browse_category("politics", limit=20)

        assert len(markets) >= 1
        assert all(isinstance(m, Market) for m in markets)
        assert all(m.category == "politics" for m in markets)


class TestPredictItParseMarket:
    def test_parse_outcomes_multi_contract(self):
        """Should create outcomes for multi-contract markets."""
        adapter = PredictItAdapter()
        market = adapter._parse_market(SAMPLE_MARKET)

        assert len(market.outcomes) == 2
        assert market.outcomes[0].name == "Donald Trump"
        assert market.outcomes[0].probability == 0.55
        assert market.outcomes[1].name == "Joe Biden"
        assert market.outcomes[1].probability == 0.35

    def test_parse_timestamp(self):
        """Should correctly parse ISO timestamps."""
        adapter = PredictItAdapter()
        market = adapter._parse_market(SAMPLE_MARKET)

        # Should have last_fetched set
        assert market.last_fetched is not None

    def test_all_markets_are_politics(self):
        """All PredictIt markets should be categorized as politics."""
        adapter = PredictItAdapter()
        market = adapter._parse_market(SAMPLE_MARKET)

        assert market.category == "politics"


class TestPredictItClose:
    @pytest.mark.asyncio
    async def test_close(self):
        """Should close the HTTP client."""
        adapter = PredictItAdapter()
        await adapter.close()
        # Should not raise
