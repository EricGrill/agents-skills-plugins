"""Tests for Kalshi adapter."""
from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.adapters.kalshi import KalshiAdapter
from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market
from tests.fixtures.kalshi_responses import (
    SAMPLE_MARKET,
    SAMPLE_MARKET_CRYPTO,
    SAMPLE_MARKET_RESOLVED,
    SAMPLE_MARKET_NO_YES_ASK,
    SAMPLE_MARKET_NO_LAST_PRICE,
    SAMPLE_MARKETS_LIST,
    SAMPLE_MARKETS_SEARCH_TRUMP,
    SAMPLE_MARKETS_EMPTY,
    SAMPLE_MARKETS_POLITICS_CATEGORY,
)


class TestKalshiAdapter:
    def test_implements_protocol(self):
        """KalshiAdapter should implement PlatformAdapter protocol."""
        adapter = KalshiAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        """Platform name should be 'kalshi'."""
        adapter = KalshiAdapter()
        assert adapter.platform == "kalshi"


class TestKalshiGetMarket:
    @pytest.mark.asyncio
    async def test_get_market_success(self, httpx_mock: HTTPXMock):
        """Should fetch and parse a single market."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/PRES-2024-DT",
            json=SAMPLE_MARKET,
        )

        adapter = KalshiAdapter()
        market = await adapter.get_market("PRES-2024-DT")

        assert isinstance(market, Market)
        assert market.platform == "kalshi"
        assert market.native_id == "PRES-2024-DT"
        assert market.title == "Will Donald Trump win the 2024 presidential election?"
        assert market.probability == 0.55  # yes_ask / 100
        assert market.category == "politics"  # Normalized from "Politics"
        assert market.url == "https://kalshi.com/markets/PRES-2024-DT"

    @pytest.mark.asyncio
    async def test_get_market_crypto(self, httpx_mock: HTTPXMock):
        """Should handle crypto category market."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/BTC-100K-JAN",
            json=SAMPLE_MARKET_CRYPTO,
        )

        adapter = KalshiAdapter()
        market = await adapter.get_market("BTC-100K-JAN")

        assert isinstance(market, Market)
        assert market.probability == 0.35  # 35 / 100
        assert market.category == "crypto"  # Normalized from "Crypto"
        assert market.volume == 500000

    @pytest.mark.asyncio
    async def test_get_market_resolved(self, httpx_mock: HTTPXMock):
        """Should correctly parse resolved markets."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/MIDTERM-2022-GOP",
            json=SAMPLE_MARKET_RESOLVED,
        )

        adapter = KalshiAdapter()
        market = await adapter.get_market("MIDTERM-2022-GOP")

        assert isinstance(market, Market)
        assert market.resolved is True
        assert market.resolution == "yes"

    @pytest.mark.asyncio
    async def test_get_market_fallback_to_last_price(self, httpx_mock: HTTPXMock):
        """Should use last_price when yes_ask is None."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/NEW-MARKET-123",
            json=SAMPLE_MARKET_NO_YES_ASK,
        )

        adapter = KalshiAdapter()
        market = await adapter.get_market("NEW-MARKET-123")

        assert isinstance(market, Market)
        assert market.probability == 0.50  # Falls back to last_price / 100

    @pytest.mark.asyncio
    async def test_get_market_yes_ask_preferred(self, httpx_mock: HTTPXMock):
        """Should prefer yes_ask over last_price when both available."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets/BRAND-NEW-MKT",
            json=SAMPLE_MARKET_NO_LAST_PRICE,
        )

        adapter = KalshiAdapter()
        market = await adapter.get_market("BRAND-NEW-MKT")

        assert isinstance(market, Market)
        assert market.probability == 0.60  # yes_ask / 100


class TestKalshiSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_markets(self, httpx_mock: HTTPXMock):
        """Should search markets by ticker query."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=TRUMP",
            json=SAMPLE_MARKETS_SEARCH_TRUMP,
        )

        adapter = KalshiAdapter()
        markets = await adapter.search_markets("TRUMP")

        assert len(markets) >= 1
        assert all(isinstance(m, Market) for m in markets)
        assert any("trump" in m.title.lower() for m in markets)

    @pytest.mark.asyncio
    async def test_search_markets_empty(self, httpx_mock: HTTPXMock):
        """Should handle empty search results."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?ticker=NONEXISTENT",
            json=SAMPLE_MARKETS_EMPTY,
        )

        adapter = KalshiAdapter()
        markets = await adapter.search_markets("NONEXISTENT")

        assert markets == []


class TestKalshiListCategories:
    @pytest.mark.asyncio
    async def test_list_categories(self):
        """Should return list of known categories."""
        adapter = KalshiAdapter()
        categories = await adapter.list_categories()

        assert isinstance(categories, list)
        assert len(categories) >= 1
        assert "politics" in categories


class TestKalshiBrowseCategory:
    @pytest.mark.asyncio
    async def test_browse_category(self, httpx_mock: HTTPXMock):
        """Should browse markets in a category."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?limit=20&status=active",
            json=SAMPLE_MARKETS_LIST,
        )

        adapter = KalshiAdapter()
        markets = await adapter.browse_category("politics", limit=20)

        assert len(markets) >= 1
        assert all(isinstance(m, Market) for m in markets)
        assert all(m.category == "politics" for m in markets)

    @pytest.mark.asyncio
    async def test_browse_category_empty(self, httpx_mock: HTTPXMock):
        """Should return empty list for unknown category."""
        httpx_mock.add_response(
            url="https://api.elections.kalshi.com/trade-api/v2/markets?limit=20&status=active",
            json=SAMPLE_MARKETS_EMPTY,
        )

        adapter = KalshiAdapter()
        markets = await adapter.browse_category("unknown_category", limit=20)

        assert markets == []


class TestKalshiParseMarket:
    def test_parse_market_outcomes(self):
        """Should create Yes/No outcomes for binary markets."""
        adapter = KalshiAdapter()
        market = adapter._parse_market(SAMPLE_MARKET["market"])

        assert len(market.outcomes) == 2
        assert market.outcomes[0].name == "Yes"
        assert market.outcomes[0].probability == 0.55
        assert market.outcomes[1].name == "No"
        assert abs(market.outcomes[1].probability - 0.45) < 0.0001

    def test_parse_market_timestamps(self):
        """Should correctly parse ISO timestamps."""
        adapter = KalshiAdapter()
        market = adapter._parse_market(SAMPLE_MARKET["market"])

        assert market.closes_at is not None
        assert market.closes_at.year == 2024
        assert market.closes_at.month == 11
        assert market.closes_at.day == 6

    def test_parse_market_category_normalization(self):
        """Should normalize category to lowercase."""
        adapter = KalshiAdapter()
        market = adapter._parse_market(SAMPLE_MARKET["market"])

        assert market.category == "politics"

    def test_parse_market_volume(self):
        """Should include volume from API."""
        adapter = KalshiAdapter()
        market = adapter._parse_market(SAMPLE_MARKET["market"])

        assert market.volume == 1500000

    def test_parse_market_url_format(self):
        """Should format URL correctly with ticker."""
        adapter = KalshiAdapter()
        market = adapter._parse_market(SAMPLE_MARKET["market"])

        assert market.url == "https://kalshi.com/markets/PRES-2024-DT"


class TestKalshiClose:
    @pytest.mark.asyncio
    async def test_close(self):
        """Should close the HTTP client."""
        adapter = KalshiAdapter()
        await adapter.close()
        # Should not raise
