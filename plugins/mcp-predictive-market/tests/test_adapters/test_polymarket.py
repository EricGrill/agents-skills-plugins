"""Tests for Polymarket adapter."""
import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.adapters.polymarket import PolymarketAdapter
from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market
from tests.fixtures.polymarket_responses import SAMPLE_MARKET, SAMPLE_MARKETS_LIST


class TestPolymarketAdapter:
    def test_implements_protocol(self):
        """PolymarketAdapter should implement PlatformAdapter protocol."""
        adapter = PolymarketAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        """Platform name should be 'polymarket'."""
        adapter = PolymarketAdapter()
        assert adapter.platform == "polymarket"


class TestPolymarketGetMarket:
    @pytest.mark.asyncio
    async def test_get_market_success(self, httpx_mock: HTTPXMock):
        """Should fetch and parse a single market."""
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets/0xabc123def",
            json=SAMPLE_MARKET,
        )

        adapter = PolymarketAdapter()
        market = await adapter.get_market("0xabc123def")

        assert isinstance(market, Market)
        assert market.platform == "polymarket"
        assert market.native_id == "0xabc123def"
        assert market.title == "Will Bitcoin reach $100k by end of 2025?"
        assert market.probability == 0.45
        assert market.volume == 125000.0


class TestPolymarketSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_markets(self, httpx_mock: HTTPXMock):
        """Should search markets by query."""
        httpx_mock.add_response(
            url="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=20&title_like=Bitcoin",
            json=SAMPLE_MARKETS_LIST,
        )

        adapter = PolymarketAdapter()
        markets = await adapter.search_markets("Bitcoin")

        assert len(markets) == 2
        assert all(isinstance(m, Market) for m in markets)
        assert markets[0].title == "Will Bitcoin reach $100k by end of 2025?"
