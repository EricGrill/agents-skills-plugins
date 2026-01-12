"""Tests for market schema definitions."""
from datetime import datetime, timezone

import pytest

from mcp_predictive_market.schema import Market, Outcome, PricePoint


class TestMarket:
    def test_market_id_format(self):
        """Market ID should be platform:native_id format."""
        market = Market(
            platform="manifold",
            native_id="abc123",
            url="https://manifold.markets/test",
            title="Will it rain tomorrow?",
            description="Resolves YES if it rains.",
            category="weather",
            probability=0.65,
            outcomes=[],
            volume=1000.0,
            liquidity=500.0,
            created_at=datetime.now(timezone.utc),
            closes_at=None,
            resolved=False,
            resolution=None,
            last_fetched=datetime.now(timezone.utc),
            price_history=[],
        )
        assert market.id == "manifold:abc123"

    def test_market_probability_bounds(self):
        """Probability must be between 0 and 1."""
        with pytest.raises(ValueError):
            Market(
                platform="manifold",
                native_id="abc123",
                url="https://manifold.markets/test",
                title="Test",
                description="Test",
                category="test",
                probability=1.5,  # Invalid
                outcomes=[],
                volume=None,
                liquidity=None,
                created_at=datetime.now(timezone.utc),
                closes_at=None,
                resolved=False,
                resolution=None,
                last_fetched=datetime.now(timezone.utc),
                price_history=[],
            )


class TestOutcome:
    def test_outcome_creation(self):
        """Outcome should store name and probability."""
        outcome = Outcome(name="Yes", probability=0.7)
        assert outcome.name == "Yes"
        assert outcome.probability == 0.7


class TestPricePoint:
    def test_price_point_creation(self):
        """PricePoint should store timestamp and probability."""
        ts = datetime.now(timezone.utc)
        point = PricePoint(timestamp=ts, probability=0.55)
        assert point.timestamp == ts
        assert point.probability == 0.55
