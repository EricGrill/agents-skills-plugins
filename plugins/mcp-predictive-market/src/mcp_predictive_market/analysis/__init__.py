"""Market analysis modules for matching and comparing markets."""

from mcp_predictive_market.analysis.arbitrage import (
    ArbitrageDetector,
    ArbitrageOpportunity,
)
from mcp_predictive_market.analysis.matching import MarketMatcher, MatchResult

__all__ = ["ArbitrageDetector", "ArbitrageOpportunity", "MarketMatcher", "MatchResult"]
