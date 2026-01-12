"""Market matching logic for finding similar markets across platforms."""
import re
from dataclasses import dataclass

from mcp_predictive_market.schema import Market


@dataclass
class MatchResult:
    """Result of matching two markets."""

    market_a: Market
    market_b: Market
    confidence: float  # 0.0 to 1.0
    match_type: str  # "text", "semantic", "manual"


class MarketMatcher:
    """Matches similar markets across platforms."""

    def __init__(self) -> None:
        """Initialize the matcher."""
        self._manual_mappings: dict[str, set[str]] = {}  # market_id -> set of equivalent market_ids

    def add_manual_mapping(self, market_id_a: str, market_id_b: str) -> None:
        """Add a manual mapping between two equivalent markets."""
        if market_id_a not in self._manual_mappings:
            self._manual_mappings[market_id_a] = set()
        if market_id_b not in self._manual_mappings:
            self._manual_mappings[market_id_b] = set()
        self._manual_mappings[market_id_a].add(market_id_b)
        self._manual_mappings[market_id_b].add(market_id_a)

    def find_matches(
        self,
        target: Market,
        candidates: list[Market],
        min_confidence: float = 0.5,
    ) -> list[MatchResult]:
        """Find markets that match the target from candidates."""
        results = []

        for candidate in candidates:
            # Skip same market
            if candidate.id == target.id:
                continue

            # Check manual mappings first
            if self._is_manual_match(target.id, candidate.id):
                results.append(
                    MatchResult(
                        market_a=target,
                        market_b=candidate,
                        confidence=1.0,
                        match_type="manual",
                    )
                )
                continue

            # Text similarity
            confidence = self._text_similarity(target.title, candidate.title)
            if confidence >= min_confidence:
                results.append(
                    MatchResult(
                        market_a=target,
                        market_b=candidate,
                        confidence=confidence,
                        match_type="text",
                    )
                )

        # Sort by confidence descending
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    def _is_manual_match(self, id_a: str, id_b: str) -> bool:
        """Check if two markets have a manual mapping."""
        return id_b in self._manual_mappings.get(id_a, set())

    def _text_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate simple text similarity between two strings."""
        # Normalize: lowercase and remove punctuation
        text_a_clean = re.sub(r"[^\w\s]", "", text_a.lower())
        text_b_clean = re.sub(r"[^\w\s]", "", text_b.lower())

        # Tokenize
        words_a = set(text_a_clean.split())
        words_b = set(text_b_clean.split())

        # Remove common stop words
        stop_words = {"will", "the", "a", "an", "by", "in", "on", "to", "be", "is", "of"}
        words_a -= stop_words
        words_b -= stop_words

        if not words_a or not words_b:
            return 0.0

        # Jaccard similarity
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0
