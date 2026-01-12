"""Arbitrage detection across prediction markets."""
from dataclasses import dataclass

from mcp_predictive_market.schema import Market
from mcp_predictive_market.analysis.matching import MarketMatcher, MatchResult


@dataclass
class ArbitrageOpportunity:
    """A potential arbitrage opportunity between two markets."""

    market_a: Market
    market_b: Market
    spread: float  # Absolute difference in probability
    match_confidence: float  # How confident we are these are the same market
    direction: str  # "buy_a_sell_b" or "buy_b_sell_a"


class ArbitrageDetector:
    """Detects arbitrage opportunities across platforms."""

    def __init__(self, matcher: MarketMatcher | None = None) -> None:
        """Initialize with optional market matcher."""
        self._matcher = matcher or MarketMatcher()

    def find_arbitrage(
        self,
        markets: list[Market],
        min_spread: float = 0.05,
        min_match_confidence: float = 0.5,
    ) -> list[ArbitrageOpportunity]:
        """Find arbitrage opportunities in a set of markets.

        Args:
            markets: List of markets from various platforms
            min_spread: Minimum probability difference to report (default 5%)
            min_match_confidence: Minimum confidence that markets are equivalent

        Returns:
            List of arbitrage opportunities, sorted by spread (highest first)
        """
        opportunities = []
        seen_pairs: set[tuple[str, str]] = set()

        for target in markets:
            # Get other markets as candidates
            candidates = [m for m in markets if m.id != target.id]

            # Find matches
            matches = self._matcher.find_matches(
                target, candidates, min_confidence=min_match_confidence
            )

            for match in matches:
                # Skip if we've seen this pair already
                pair = tuple(sorted([match.market_a.id, match.market_b.id]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                # Calculate spread
                spread = abs(match.market_a.probability - match.market_b.probability)

                if spread >= min_spread:
                    # Determine direction
                    if match.market_a.probability < match.market_b.probability:
                        direction = "buy_a_sell_b"
                    else:
                        direction = "buy_b_sell_a"

                    opportunities.append(
                        ArbitrageOpportunity(
                            market_a=match.market_a,
                            market_b=match.market_b,
                            spread=spread,
                            match_confidence=match.confidence,
                            direction=direction,
                        )
                    )

        # Sort by spread descending
        opportunities.sort(key=lambda o: o.spread, reverse=True)
        return opportunities

    def compare_platforms(
        self,
        markets: list[Market],
        min_match_confidence: float = 0.5,
    ) -> dict[str, list[dict]]:
        """Compare probabilities for similar markets across platforms.

        Returns dict with structure:
        {
            "comparisons": [
                {
                    "title": "...",
                    "platforms": {
                        "manifold": {"probability": 0.45, "url": "..."},
                        "polymarket": {"probability": 0.52, "url": "..."},
                    },
                    "max_spread": 0.07,
                }
            ]
        }
        """
        # Group markets by match
        comparisons = []
        processed: set[str] = set()

        for target in markets:
            if target.id in processed:
                continue

            processed.add(target.id)
            candidates = [
                m for m in markets if m.id != target.id and m.id not in processed
            ]
            matches = self._matcher.find_matches(
                target, candidates, min_confidence=min_match_confidence
            )

            if matches:
                platforms = {
                    target.platform: {
                        "probability": target.probability,
                        "url": target.url,
                    }
                }
                probs = [target.probability]

                for match in matches:
                    processed.add(match.market_b.id)
                    platforms[match.market_b.platform] = {
                        "probability": match.market_b.probability,
                        "url": match.market_b.url,
                    }
                    probs.append(match.market_b.probability)

                comparisons.append(
                    {
                        "title": target.title,
                        "platforms": platforms,
                        "max_spread": max(probs) - min(probs),
                    }
                )

        return {"comparisons": comparisons}
