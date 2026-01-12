"""Tests for rate limiting."""
import asyncio

import pytest

from mcp_predictive_market.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_default_limits(self):
        """Should have default limits for known platforms."""
        limiter = RateLimiter()
        assert limiter.get_limit("kalshi") == 10
        assert limiter.get_limit("manifold") == 100

    def test_custom_limits(self):
        """Should accept custom limits."""
        limiter = RateLimiter({"custom": 5})
        assert limiter.get_limit("custom") == 5

    def test_set_limit(self):
        """Should allow setting limits after init."""
        limiter = RateLimiter()
        limiter.set_limit("kalshi", 20)
        assert limiter.get_limit("kalshi") == 20

    @pytest.mark.asyncio
    async def test_acquire_succeeds(self):
        """Should acquire without waiting when under limit."""
        limiter = RateLimiter({"test": 100})
        await limiter.acquire("test")  # Should not block

    @pytest.mark.asyncio
    async def test_acquire_multiple(self):
        """Should handle multiple rapid acquires."""
        limiter = RateLimiter({"test": 100})
        for _ in range(10):
            await limiter.acquire("test")
        # Should complete quickly since under limit

    @pytest.mark.asyncio
    async def test_unknown_platform_uses_default(self):
        """Unknown platforms should use default limit of 60."""
        limiter = RateLimiter()
        assert limiter.get_limit("unknown") == 60
