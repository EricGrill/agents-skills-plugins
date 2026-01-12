"""Tests for error handling."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from mcp_predictive_market.errors import PlatformError
from mcp_predictive_market.tools import ToolHandlers
from mcp_predictive_market.schema import Market


class TestPlatformError:
    """Tests for PlatformError exception class."""

    def test_platform_error_attributes(self):
        """PlatformError should have platform and message attributes."""
        error = PlatformError(platform="manifold", message="Connection timeout")

        assert error.platform == "manifold"
        assert error.message == "Connection timeout"

    def test_platform_error_str_formatting(self):
        """PlatformError __str__ should return formatted error message."""
        error = PlatformError(platform="polymarket", message="Rate limit exceeded")

        result = str(error)

        assert result == "[polymarket] Rate limit exceeded"

    def test_platform_error_inherits_from_exception(self):
        """PlatformError should inherit from Exception."""
        error = PlatformError(platform="kalshi", message="API error")

        assert isinstance(error, Exception)

    def test_platform_error_can_be_raised_and_caught(self):
        """PlatformError can be raised and caught."""
        with pytest.raises(PlatformError) as exc_info:
            raise PlatformError(platform="metaculus", message="Not found")

        assert exc_info.value.platform == "metaculus"
        assert exc_info.value.message == "Not found"


class TestPartialResultsOnFailure:
    """Tests for partial results when some platforms fail."""

    def _create_mock_adapter(
        self, platform: str, markets: list[Market] | None = None, error: Exception | None = None
    ):
        """Create a mock adapter that returns markets or raises an error."""
        adapter = MagicMock()
        adapter.platform = platform

        if error:
            adapter.search_markets = AsyncMock(side_effect=error)
            adapter.browse_category = AsyncMock(side_effect=error)
        else:
            adapter.search_markets = AsyncMock(return_value=markets or [])
            adapter.browse_category = AsyncMock(return_value=markets or [])

        return adapter

    def _create_sample_market(self, platform: str, title: str) -> Market:
        """Create a sample market for testing."""
        from datetime import datetime, timezone

        return Market(
            platform=platform,
            native_id="test123",
            url=f"https://{platform}.com/market/test123",
            title=title,
            description="Test market",
            category="technology",
            probability=0.5,
            volume=1000.0,
            resolved=False,
            resolution=None,
            created_at=datetime.now(timezone.utc),
            last_fetched=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_search_markets_returns_partial_results_on_platform_failure(self):
        """search_markets should return results from successful platforms when one fails."""
        # Create a working adapter and a failing adapter
        working_market = self._create_sample_market("manifold", "AI Test Market")
        working_adapter = self._create_mock_adapter("manifold", markets=[working_market])

        failing_adapter = self._create_mock_adapter(
            "polymarket",
            error=PlatformError(platform="polymarket", message="API timeout"),
        )

        adapters = {"manifold": working_adapter, "polymarket": failing_adapter}
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="AI")

        # Should have results from the working adapter
        assert len(result["markets"]) == 1
        assert result["markets"][0]["platform"] == "manifold"
        assert result["markets"][0]["title"] == "AI Test Market"

        # Should have error info for the failing adapter
        assert len(result["errors"]) == 1
        assert result["errors"][0]["platform"] == "polymarket"
        assert "API timeout" in result["errors"][0]["error"]

    @pytest.mark.asyncio
    async def test_search_markets_returns_all_results_when_no_failures(self):
        """search_markets should return all results when all platforms succeed."""
        market1 = self._create_sample_market("manifold", "Manifold Market")
        market2 = self._create_sample_market("polymarket", "Polymarket Market")

        adapter1 = self._create_mock_adapter("manifold", markets=[market1])
        adapter2 = self._create_mock_adapter("polymarket", markets=[market2])

        adapters = {"manifold": adapter1, "polymarket": adapter2}
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="test")

        assert len(result["markets"]) == 2
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_search_markets_returns_empty_when_all_platforms_fail(self):
        """search_markets should return empty results with errors when all fail."""
        failing_adapter1 = self._create_mock_adapter(
            "manifold",
            error=PlatformError(platform="manifold", message="Server error"),
        )
        failing_adapter2 = self._create_mock_adapter(
            "polymarket",
            error=PlatformError(platform="polymarket", message="Network error"),
        )

        adapters = {"manifold": failing_adapter1, "polymarket": failing_adapter2}
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="test")

        assert result["markets"] == []
        assert len(result["errors"]) == 2

    @pytest.mark.asyncio
    async def test_find_arbitrage_returns_partial_results_on_platform_failure(self):
        """find_arbitrage should work with partial data when some platforms fail."""
        working_market = self._create_sample_market("manifold", "Bitcoin 100k")
        working_adapter = self._create_mock_adapter("manifold", markets=[working_market])

        failing_adapter = self._create_mock_adapter(
            "polymarket",
            error=Exception("Connection refused"),
        )

        adapters = {"manifold": working_adapter, "polymarket": failing_adapter}
        handlers = ToolHandlers(adapters)

        result = await handlers.find_arbitrage(min_spread=0.05)

        # Should have arbitrage data (even if empty due to single platform)
        assert "opportunities" in result

        # Should have error info for the failing platform
        assert len(result["errors"]) == 1
        assert result["errors"][0]["platform"] == "polymarket"
        assert "Connection refused" in result["errors"][0]["error"]

    @pytest.mark.asyncio
    async def test_browse_category_returns_partial_results_on_platform_failure(self):
        """browse_category should return results from successful platforms."""
        working_market = self._create_sample_market("manifold", "Politics Market")
        working_adapter = self._create_mock_adapter("manifold", markets=[working_market])

        failing_adapter = self._create_mock_adapter(
            "kalshi",
            error=PlatformError(platform="kalshi", message="Unauthorized"),
        )

        adapters = {"manifold": working_adapter, "kalshi": failing_adapter}
        handlers = ToolHandlers(adapters)

        result = await handlers.browse_category(category="politics")

        # Should have results from the working adapter
        assert len(result["markets"]) == 1
        assert result["markets"][0]["platform"] == "manifold"

        # Should have error info
        assert len(result["errors"]) == 1
        assert result["errors"][0]["platform"] == "kalshi"

    @pytest.mark.asyncio
    async def test_compare_platforms_returns_partial_results_on_platform_failure(self):
        """compare_platforms should work with partial data when some platforms fail."""
        working_market = self._create_sample_market("manifold", "Election 2024")
        working_adapter = self._create_mock_adapter("manifold", markets=[working_market])

        failing_adapter = self._create_mock_adapter(
            "predictit",
            error=PlatformError(platform="predictit", message="Service unavailable"),
        )

        adapters = {"manifold": working_adapter, "predictit": failing_adapter}
        handlers = ToolHandlers(adapters)

        result = await handlers.compare_platforms(query="election")

        # Should have comparison data
        assert "comparisons" in result

        # Should have error info
        assert len(result["errors"]) == 1
        assert result["errors"][0]["platform"] == "predictit"


class TestPlatformErrorInResponse:
    """Tests for proper PlatformError handling in response formatting."""

    def _create_mock_adapter_with_platform_error(self, platform: str):
        """Create a mock adapter that raises PlatformError."""
        adapter = MagicMock()
        adapter.platform = platform
        adapter.search_markets = AsyncMock(
            side_effect=PlatformError(platform=platform, message="API rate limit exceeded")
        )
        return adapter

    @pytest.mark.asyncio
    async def test_platform_error_message_is_included_in_response(self):
        """PlatformError message should be properly formatted in response."""
        failing_adapter = self._create_mock_adapter_with_platform_error("polymarket")

        adapters = {"polymarket": failing_adapter}
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="test")

        assert len(result["errors"]) == 1
        # The error message should contain the formatted PlatformError string
        assert "polymarket" in result["errors"][0]["error"]
        assert "API rate limit exceeded" in result["errors"][0]["error"]


class TestListCategoriesErrorHandling:
    """Tests for list_categories error handling."""

    def _create_mock_adapter(
        self, platform: str, categories: list[str] | None = None, error: Exception | None = None
    ):
        """Create a mock adapter that returns categories or raises an error."""
        adapter = MagicMock()
        adapter.platform = platform

        if error:
            adapter.list_categories = AsyncMock(side_effect=error)
        else:
            adapter.list_categories = AsyncMock(return_value=categories or [])

        return adapter

    @pytest.mark.asyncio
    async def test_list_categories_returns_partial_results_on_platform_failure(self):
        """list_categories should return categories from successful platforms and errors from failed ones."""
        working_adapter = self._create_mock_adapter("manifold", categories=["politics", "technology"])
        failing_adapter = self._create_mock_adapter(
            "polymarket",
            error=PlatformError(platform="polymarket", message="API timeout"),
        )

        adapters = {"manifold": working_adapter, "polymarket": failing_adapter}
        handlers = ToolHandlers(adapters)

        result = await handlers.list_categories()

        # Should have categories from the working adapter
        assert "categories" in result
        assert "politics" in result["categories"]
        assert "technology" in result["categories"]

        # Should have error info for the failing adapter
        assert "errors" in result
        assert len(result["errors"]) == 1
        assert result["errors"][0]["platform"] == "polymarket"
        assert "API timeout" in result["errors"][0]["error"]

    @pytest.mark.asyncio
    async def test_list_categories_returns_all_categories_when_no_failures(self):
        """list_categories should return all categories when all platforms succeed."""
        adapter1 = self._create_mock_adapter("manifold", categories=["politics", "technology"])
        adapter2 = self._create_mock_adapter("polymarket", categories=["sports", "technology"])

        adapters = {"manifold": adapter1, "polymarket": adapter2}
        handlers = ToolHandlers(adapters)

        result = await handlers.list_categories()

        # Should have combined unique categories
        assert set(result["categories"]) == {"politics", "technology", "sports"}
        # Should have no errors
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_list_categories_returns_empty_with_errors_when_all_fail(self):
        """list_categories should return empty categories with errors when all platforms fail."""
        failing_adapter1 = self._create_mock_adapter(
            "manifold",
            error=PlatformError(platform="manifold", message="Server error"),
        )
        failing_adapter2 = self._create_mock_adapter(
            "polymarket",
            error=PlatformError(platform="polymarket", message="Network error"),
        )

        adapters = {"manifold": failing_adapter1, "polymarket": failing_adapter2}
        handlers = ToolHandlers(adapters)

        result = await handlers.list_categories()

        assert result["categories"] == []
        assert len(result["errors"]) == 2


class TestGetTrackedMarketsErrorHandling:
    """Tests for get_tracked_markets error handling."""

    def _create_sample_market(self, platform: str, title: str) -> Market:
        """Create a sample market for testing."""
        from datetime import datetime, timezone

        return Market(
            platform=platform,
            native_id="test123",
            url=f"https://{platform}.com/market/test123",
            title=title,
            description="Test market",
            category="technology",
            probability=0.5,
            volume=1000.0,
            resolved=False,
            resolution=None,
            created_at=datetime.now(timezone.utc),
            last_fetched=datetime.now(timezone.utc),
        )

    @pytest.mark.asyncio
    async def test_get_tracked_markets_collects_errors_for_failed_refreshes(self):
        """get_tracked_markets should collect errors when refreshing tracked markets fails."""
        # Create adapters - one will succeed, one will fail
        market = self._create_sample_market("manifold", "Test Market")

        working_adapter = MagicMock()
        working_adapter.get_market = AsyncMock(return_value=market)

        failing_adapter = MagicMock()
        failing_adapter.get_market = AsyncMock(
            side_effect=PlatformError(platform="polymarket", message="Market not found")
        )

        adapters = {"manifold": working_adapter, "polymarket": failing_adapter}
        handlers = ToolHandlers(adapters)

        # Manually add tracked markets (simulating previous track_market calls)
        handlers._tracked_markets = {
            "manifold:market1": {"alias": "m1", "tracked_at": "2024-01-01T00:00:00Z"},
            "polymarket:market2": {"alias": "m2", "tracked_at": "2024-01-01T00:00:00Z"},
        }

        result = await handlers.get_tracked_markets()

        # Should have one successful result
        assert len(result["tracked_markets"]) == 1
        assert result["tracked_markets"][0]["alias"] == "m1"

        # Should have one error
        assert len(result["errors"]) == 1
        assert result["errors"][0]["market_id"] == "polymarket:market2"
        assert "Market not found" in result["errors"][0]["error"]


class TestGetMarketOddsErrorHandling:
    """Tests for get_market_odds error handling."""

    @pytest.mark.asyncio
    async def test_get_market_odds_raises_on_adapter_failure(self):
        """get_market_odds should propagate exception when adapter.get_market fails."""
        failing_adapter = MagicMock()
        failing_adapter.get_market = AsyncMock(
            side_effect=PlatformError(platform="manifold", message="Market not found")
        )

        adapters = {"manifold": failing_adapter}
        handlers = ToolHandlers(adapters)

        with pytest.raises(PlatformError) as exc_info:
            await handlers.get_market_odds(platform="manifold", market_id="nonexistent")

        assert exc_info.value.platform == "manifold"
        assert exc_info.value.message == "Market not found"

    @pytest.mark.asyncio
    async def test_get_market_odds_raises_value_error_for_unknown_platform(self):
        """get_market_odds should raise ValueError for unknown platform."""
        adapters = {"manifold": MagicMock()}
        handlers = ToolHandlers(adapters)

        with pytest.raises(ValueError) as exc_info:
            await handlers.get_market_odds(platform="unknown_platform", market_id="test123")

        assert "Unknown platform" in str(exc_info.value)
