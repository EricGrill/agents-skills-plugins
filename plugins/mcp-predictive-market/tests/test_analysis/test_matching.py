"""Tests for market matching logic."""
from datetime import datetime, timezone

import pytest

from mcp_predictive_market.analysis.matching import MarketMatcher, MatchResult
from mcp_predictive_market.schema import Market


def make_market(platform: str, native_id: str, title: str) -> Market:
    """Create a test market."""
    return Market(
        platform=platform,
        native_id=native_id,
        url=f"https://{platform}.com/{native_id}",
        title=title,
        description="",
        category="politics",
        probability=0.5,
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


class TestMarketMatcher:
    def test_find_matches_similar_titles(self):
        """Should match markets with similar titles."""
        matcher = MarketMatcher()

        target = make_market("manifold", "abc", "Will Trump win 2024 election?")
        candidates = [
            make_market("polymarket", "xyz", "Trump wins 2024 presidential election"),
            make_market("kalshi", "pres", "Will Biden win 2024?"),
        ]

        results = matcher.find_matches(target, candidates, min_confidence=0.3)

        assert len(results) >= 1
        assert results[0].market_b.platform == "polymarket"
        assert results[0].confidence > 0.3

    def test_find_matches_manual_mapping(self):
        """Should return manual mappings with confidence 1.0."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        target = make_market("manifold", "abc", "Some market")
        candidates = [make_market("polymarket", "xyz", "Different title")]

        results = matcher.find_matches(target, candidates)

        assert len(results) == 1
        assert results[0].confidence == 1.0
        assert results[0].match_type == "manual"

    def test_find_matches_excludes_same_market(self):
        """Should not match a market with itself."""
        matcher = MarketMatcher()

        market = make_market("manifold", "abc", "Test market")

        results = matcher.find_matches(market, [market])

        assert len(results) == 0

    def test_text_similarity(self):
        """Should calculate Jaccard similarity."""
        matcher = MarketMatcher()

        # Identical (excluding stop words)
        sim = matcher._text_similarity("Will Trump win?", "Trump win")
        assert sim > 0.5

        # Completely different
        sim = matcher._text_similarity("Bitcoin price", "Football game")
        assert sim == 0.0

    def test_add_manual_mapping_bidirectional(self):
        """Should add mappings in both directions."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("a:1", "b:2")

        assert matcher._is_manual_match("a:1", "b:2")
        assert matcher._is_manual_match("b:2", "a:1")

    def test_find_matches_respects_min_confidence(self):
        """Should filter out matches below min_confidence."""
        matcher = MarketMatcher()

        target = make_market("manifold", "abc", "Bitcoin price prediction")
        candidates = [
            make_market("polymarket", "xyz", "Bitcoin price forecast tomorrow"),
            make_market("kalshi", "pres", "Ethereum gas fees"),
        ]

        # With high threshold, should get fewer matches
        high_threshold_results = matcher.find_matches(
            target, candidates, min_confidence=0.8
        )
        low_threshold_results = matcher.find_matches(
            target, candidates, min_confidence=0.1
        )

        assert len(high_threshold_results) <= len(low_threshold_results)

    def test_find_matches_sorted_by_confidence(self):
        """Should return results sorted by confidence descending."""
        matcher = MarketMatcher()
        matcher.add_manual_mapping("manifold:abc", "polymarket:xyz")

        target = make_market("manifold", "abc", "Will Trump win 2024?")
        candidates = [
            make_market("kalshi", "k1", "Trump wins 2024"),
            make_market("polymarket", "xyz", "Some other market"),  # manual match
        ]

        results = matcher.find_matches(target, candidates, min_confidence=0.1)

        # Manual match should come first with confidence 1.0
        assert len(results) >= 1
        assert results[0].match_type == "manual"
        assert results[0].confidence == 1.0

    def test_text_similarity_empty_after_stop_words(self):
        """Should return 0.0 if all words are stop words."""
        matcher = MarketMatcher()

        sim = matcher._text_similarity("the a an", "is to be")
        assert sim == 0.0

    def test_match_result_contains_markets(self):
        """Should include both markets in the result."""
        matcher = MarketMatcher()

        target = make_market("manifold", "abc", "Bitcoin prediction")
        candidate = make_market("polymarket", "xyz", "Bitcoin prediction")

        results = matcher.find_matches(target, [candidate], min_confidence=0.0)

        assert len(results) == 1
        assert results[0].market_a == target
        assert results[0].market_b == candidate
