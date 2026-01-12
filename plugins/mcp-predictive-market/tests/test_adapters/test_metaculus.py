"""Tests for Metaculus adapter."""
from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.adapters.metaculus import MetaculusAdapter
from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market
from tests.fixtures.metaculus_responses import (
    SAMPLE_QUESTION,
    SAMPLE_QUESTION_NO_PREDICTION,
    SAMPLE_QUESTION_RESOLVED,
    SAMPLE_QUESTIONS_LIST,
    SAMPLE_QUESTIONS_BY_CATEGORY,
)


class TestMetaculusAdapter:
    def test_implements_protocol(self):
        """MetaculusAdapter should implement PlatformAdapter protocol."""
        adapter = MetaculusAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        """Platform name should be 'metaculus'."""
        adapter = MetaculusAdapter()
        assert adapter.platform == "metaculus"


class TestMetaculusGetMarket:
    @pytest.mark.asyncio
    async def test_get_market_success(self, httpx_mock: HTTPXMock):
        """Should fetch and parse a single market."""
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/12345/",
            json=SAMPLE_QUESTION,
        )

        adapter = MetaculusAdapter()
        market = await adapter.get_market("12345")

        assert isinstance(market, Market)
        assert market.platform == "metaculus"
        assert market.native_id == "12345"
        assert market.title == "Will AGI be developed by 2030?"
        assert market.probability == 0.35
        assert market.url == "https://www.metaculus.com/questions/12345/"
        assert market.category == "ai"

    @pytest.mark.asyncio
    async def test_get_market_no_prediction(self, httpx_mock: HTTPXMock):
        """Should handle markets without community predictions."""
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/12346/",
            json=SAMPLE_QUESTION_NO_PREDICTION,
        )

        adapter = MetaculusAdapter()
        market = await adapter.get_market("12346")

        assert isinstance(market, Market)
        assert market.probability == 0.5  # Default when no prediction

    @pytest.mark.asyncio
    async def test_get_market_resolved(self, httpx_mock: HTTPXMock):
        """Should correctly parse resolved markets."""
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/12347/",
            json=SAMPLE_QUESTION_RESOLVED,
        )

        adapter = MetaculusAdapter()
        market = await adapter.get_market("12347")

        assert isinstance(market, Market)
        assert market.resolved is True
        assert market.resolution == "1.0"


class TestMetaculusSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_markets(self, httpx_mock: HTTPXMock):
        """Should search markets by query."""
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=AGI&limit=20",
            json=SAMPLE_QUESTIONS_LIST,
        )

        adapter = MetaculusAdapter()
        markets = await adapter.search_markets("AGI")

        assert len(markets) == 2
        assert all(isinstance(m, Market) for m in markets)
        assert markets[0].title == "Will AGI be developed by 2030?"

    @pytest.mark.asyncio
    async def test_search_markets_empty(self, httpx_mock: HTTPXMock):
        """Should handle empty search results."""
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?search=nonexistent&limit=20",
            json={"results": [], "count": 0, "next": None, "previous": None},
        )

        adapter = MetaculusAdapter()
        markets = await adapter.search_markets("nonexistent")

        assert markets == []


class TestMetaculusListCategories:
    @pytest.mark.asyncio
    async def test_list_categories(self):
        """Should return list of normalized categories."""
        adapter = MetaculusAdapter()
        categories = await adapter.list_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "ai" in categories
        assert "science" in categories


class TestMetaculusBrowseCategory:
    @pytest.mark.asyncio
    async def test_browse_category(self, httpx_mock: HTTPXMock):
        """Should browse markets in a category."""
        httpx_mock.add_response(
            url="https://www.metaculus.com/api2/questions/?limit=20",
            json=SAMPLE_QUESTIONS_BY_CATEGORY,
        )

        adapter = MetaculusAdapter()
        markets = await adapter.browse_category("ai", limit=20)

        assert len(markets) >= 1
        assert all(isinstance(m, Market) for m in markets)


class TestMetaculusParseMarket:
    def test_parse_timestamps(self):
        """Should correctly parse ISO timestamps."""
        adapter = MetaculusAdapter()
        market = adapter._parse_market(SAMPLE_QUESTION)

        assert market.created_at == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert market.closes_at == datetime(2029, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    def test_parse_categories_to_normalized(self):
        """Should normalize Metaculus categories."""
        adapter = MetaculusAdapter()
        market = adapter._parse_market(SAMPLE_QUESTION)

        assert market.category == "ai"

    def test_parse_outcomes(self):
        """Should create Yes/No outcomes for binary questions."""
        adapter = MetaculusAdapter()
        market = adapter._parse_market(SAMPLE_QUESTION)

        assert len(market.outcomes) == 2
        assert market.outcomes[0].name == "Yes"
        assert market.outcomes[0].probability == 0.35
        assert market.outcomes[1].name == "No"
        assert market.outcomes[1].probability == 0.65


class TestMetaculusClose:
    @pytest.mark.asyncio
    async def test_close(self):
        """Should close the HTTP client."""
        adapter = MetaculusAdapter()
        await adapter.close()
        # Should not raise
