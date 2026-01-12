"""Tests for Manifold Markets adapter."""
from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market
from tests.fixtures.manifold_responses import SAMPLE_MARKET, SAMPLE_MARKETS_LIST


class TestManifoldAdapter:
    def test_implements_protocol(self):
        """ManifoldAdapter should implement PlatformAdapter protocol."""
        adapter = ManifoldAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        """Platform name should be 'manifold'."""
        adapter = ManifoldAdapter()
        assert adapter.platform == "manifold"


class TestManifoldGetMarket:
    @pytest.mark.asyncio
    async def test_get_market_success(self, httpx_mock: HTTPXMock):
        """Should fetch and parse a single market."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        adapter = ManifoldAdapter()
        market = await adapter.get_market("abc123xyz")

        assert isinstance(market, Market)
        assert market.platform == "manifold"
        assert market.native_id == "abc123xyz"
        assert market.title == "Will AI pass the Turing test by 2025?"
        assert market.probability == 0.4
        assert market.volume == 5000


class TestManifoldSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_markets(self, httpx_mock: HTTPXMock):
        """Should search markets by query."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=AI&limit=20",
            json=SAMPLE_MARKETS_LIST,
        )

        adapter = ManifoldAdapter()
        markets = await adapter.search_markets("AI")

        assert len(markets) == 2
        assert all(isinstance(m, Market) for m in markets)
        assert markets[0].title == "Will AI pass the Turing test by 2025?"
