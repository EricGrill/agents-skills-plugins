"""Tests for arbitrage detection logic."""
from datetime import datetime, timezone

import pytest

from mcp_predictive_market.analysis.arbitrage import (
    ArbitrageDetector,
    ArbitrageOpportunity,
)
from mcp_predictive_market.analysis.matching import MarketMatcher
from mcp_predictive_market.schema import Market


def make_market(
    platform: str, native_id: str, title: str, probability: float = 0.5
) -> Market:
    """Create a test market."""
    return Market(
        platform=platform,
        native_id=native_id,
        url=f"https://{platform}.com/{native_id}",
        title=title,
        description="",
        category="politics",
        probability=probability,
        outcomes=[],
        volume=1000,
        liquidity=500,
        created_at=datetime.now(timezone.utc),
        closes_at=None,
        resolved=False,
        resolution=None,
        last_fetched=datetime.now(timezone.utc),
        price_history=[],
    )


class TestArbitrageDetector:
    def test_find_arbitrage_finds_opportunities_when_spread_exceeds_threshold(self):
        """Should find arbitrage when spread is above min_spread."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Will Trump win 2024?", probability=0.40),
            make_market("polymarket", "xyz", "Trump wins 2024", probability=0.55),
        ]

        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 1
        assert opportunities[0].spread == pytest.approx(0.15)
        assert opportunities[0].match_confidence == 1.0

    def test_find_arbitrage_respects_min_spread_filter(self):
        """Should not return opportunities below min_spread."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Will Trump win 2024?", probability=0.50),
            make_market("polymarket", "xyz", "Trump wins 2024", probability=0.52),
        ]

        # Spread is 0.02, below min_spread of 0.05
        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 0

        # Lower threshold should find the opportunity
        opportunities = detector.find_arbitrage(
            markets, min_spread=0.01, min_match_confidence=0.5
        )

        assert len(opportunities) == 1
        assert opportunities[0].spread == pytest.approx(0.02)

    def test_find_arbitrage_does_not_duplicate_pairs(self):
        """Should not return the same pair twice."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Will Trump win 2024?", probability=0.40),
            make_market("polymarket", "xyz", "Trump wins 2024", probability=0.60),
        ]

        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        # Should only return one opportunity, not two (one for each direction)
        assert len(opportunities) == 1

    def test_find_arbitrage_determines_correct_direction_buy_a_sell_b(self):
        """Should set direction to buy_a_sell_b when market_a has lower probability."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Will Trump win 2024?", probability=0.40),
            make_market("polymarket", "xyz", "Trump wins 2024", probability=0.60),
        ]

        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 1
        # market_a (manifold) has lower probability, so buy cheap (a) sell expensive (b)
        assert opportunities[0].direction == "buy_a_sell_b"

    def test_find_arbitrage_determines_correct_direction_buy_b_sell_a(self):
        """Should set direction to buy_b_sell_a when market_b has lower probability."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Will Trump win 2024?", probability=0.60),
            make_market("polymarket", "xyz", "Trump wins 2024", probability=0.40),
        ]

        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 1
        # market_a (manifold) has higher probability, so buy cheap (b) sell expensive (a)
        assert opportunities[0].direction == "buy_b_sell_a"

    def test_find_arbitrage_sorted_by_spread_descending(self):
        """Should return opportunities sorted by spread (highest first)."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:m1", "polymarket:p1")
        matcher.add_manual_mapping("manifold:m2", "polymarket:p2")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "m1", "Market 1", probability=0.50),
            make_market("polymarket", "p1", "Market 1 poly", probability=0.60),  # 0.10 spread
            make_market("manifold", "m2", "Market 2", probability=0.30),
            make_market("polymarket", "p2", "Market 2 poly", probability=0.55),  # 0.25 spread
        ]

        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 2
        # Higher spread should come first
        assert opportunities[0].spread == pytest.approx(0.25)
        assert opportunities[1].spread == pytest.approx(0.10)

    def test_find_arbitrage_respects_min_match_confidence(self):
        """Should only find arbitrage for matches above confidence threshold."""
        detector = ArbitrageDetector()

        markets = [
            make_market("manifold", "abc", "Bitcoin price prediction", probability=0.40),
            make_market("polymarket", "xyz", "Bitcoin price forecast", probability=0.60),
        ]

        # With very high confidence threshold, text matching may not reach it
        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.99
        )

        # No manual mapping, text similarity likely won't reach 0.99
        assert len(opportunities) == 0

    def test_find_arbitrage_uses_default_matcher(self):
        """Should create a default MarketMatcher if none provided."""
        detector = ArbitrageDetector()

        markets = [
            make_market("manifold", "abc", "Bitcoin price prediction 2024", probability=0.40),
            make_market("polymarket", "xyz", "Bitcoin price prediction 2024", probability=0.60),
        ]

        # Identical titles should match with high confidence
        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 1

    def test_find_arbitrage_no_matches(self):
        """Should return empty list when no matches found."""
        detector = ArbitrageDetector()

        markets = [
            make_market("manifold", "abc", "Bitcoin price", probability=0.40),
            make_market("polymarket", "xyz", "Weather forecast", probability=0.60),
        ]

        opportunities = detector.find_arbitrage(
            markets, min_spread=0.05, min_match_confidence=0.5
        )

        assert len(opportunities) == 0


class TestArbitrageDetectorComparePlatforms:
    def test_compare_platforms_groups_matched_markets(self):
        """Should group matched markets across platforms."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Will Trump win 2024?", probability=0.45),
            make_market("polymarket", "xyz", "Trump wins 2024", probability=0.52),
        ]

        result = detector.compare_platforms(markets, min_match_confidence=0.5)

        assert "comparisons" in result
        assert len(result["comparisons"]) == 1

        comparison = result["comparisons"][0]
        assert comparison["title"] == "Will Trump win 2024?"
        assert "manifold" in comparison["platforms"]
        assert "polymarket" in comparison["platforms"]

    def test_compare_platforms_calculates_max_spread_correctly(self):
        """Should calculate max_spread as difference between highest and lowest probability."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")
        matcher.add_manual_mapping("manifold:abc", "kalshi:k1")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Test market", probability=0.40),
            make_market("polymarket", "xyz", "Test market poly", probability=0.55),
            make_market("kalshi", "k1", "Test market kalshi", probability=0.60),
        ]

        result = detector.compare_platforms(markets, min_match_confidence=0.5)

        assert len(result["comparisons"]) == 1
        comparison = result["comparisons"][0]
        # max_spread should be 0.60 - 0.40 = 0.20
        assert comparison["max_spread"] == pytest.approx(0.20)

    def test_compare_platforms_includes_platform_details(self):
        """Should include probability and URL for each platform."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "abc", "Test market", probability=0.45),
            make_market("polymarket", "xyz", "Test market poly", probability=0.52),
        ]

        result = detector.compare_platforms(markets, min_match_confidence=0.5)

        comparison = result["comparisons"][0]

        assert comparison["platforms"]["manifold"]["probability"] == pytest.approx(0.45)
        assert comparison["platforms"]["manifold"]["url"] == "https://manifold.com/abc"
        assert comparison["platforms"]["polymarket"]["probability"] == pytest.approx(0.52)
        assert comparison["platforms"]["polymarket"]["url"] == "https://polymarket.com/xyz"

    def test_compare_platforms_no_matches(self):
        """Should return empty comparisons list when no matches found."""
        detector = ArbitrageDetector()

        markets = [
            make_market("manifold", "abc", "Bitcoin price", probability=0.40),
            make_market("polymarket", "xyz", "Weather forecast", probability=0.60),
        ]

        result = detector.compare_platforms(markets, min_match_confidence=0.5)

        assert result["comparisons"] == []

    def test_compare_platforms_does_not_repeat_markets(self):
        """Should not include the same market in multiple comparisons."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:m1", "polymarket:p1")

        detector = ArbitrageDetector(matcher=matcher)

        markets = [
            make_market("manifold", "m1", "Market 1", probability=0.50),
            make_market("polymarket", "p1", "Market 1 poly", probability=0.60),
        ]

        result = detector.compare_platforms(markets, min_match_confidence=0.5)

        # Should only have one comparison
        assert len(result["comparisons"]) == 1


class TestArbitrageOpportunity:
    def test_arbitrage_opportunity_dataclass(self):
        """Should create ArbitrageOpportunity with correct fields."""
        market_a = make_market("manifold", "abc", "Test", probability=0.40)
        market_b = make_market("polymarket", "xyz", "Test", probability=0.60)

        opportunity = ArbitrageOpportunity(
            market_a=market_a,
            market_b=market_b,
            spread=0.20,
            match_confidence=0.95,
            direction="buy_a_sell_b",
        )

        assert opportunity.market_a == market_a
        assert opportunity.market_b == market_b
        assert opportunity.spread == 0.20
        assert opportunity.match_confidence == 0.95
        assert opportunity.direction == "buy_a_sell_b"
