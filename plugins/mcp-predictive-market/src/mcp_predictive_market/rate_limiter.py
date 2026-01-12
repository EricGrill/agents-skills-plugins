"""Per-platform rate limiting for API calls."""
import asyncio
from collections import defaultdict
from typing import Any


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""

    # Default rate limits (requests per minute)
    DEFAULT_LIMITS = {
        "kalshi": 10,
        "polymarket": 30,
        "metaculus": 60,
        "predictit": 20,
        "manifold": 100,
    }

    def __init__(self, limits: dict[str, int] | None = None) -> None:
        """Initialize with optional custom limits."""
        self._limits = limits or self.DEFAULT_LIMITS.copy()
        self._tokens: dict[str, float] = defaultdict(lambda: 0.0)
        self._last_update: dict[str, float] = defaultdict(float)
        self._lock = asyncio.Lock()

    async def acquire(self, platform: str) -> None:
        """Acquire a rate limit token, waiting if necessary."""
        async with self._lock:
            limit = self._limits.get(platform, 60)  # Default to 60/min
            tokens_per_second = limit / 60.0

            now = asyncio.get_event_loop().time()

            # Initialize if first request
            if platform not in self._last_update or self._last_update[platform] == 0:
                self._tokens[platform] = limit
                self._last_update[platform] = now

            # Refill tokens based on time elapsed
            elapsed = now - self._last_update[platform]
            self._tokens[platform] = min(
                limit, self._tokens[platform] + elapsed * tokens_per_second
            )
            self._last_update[platform] = now

            # Wait if no tokens available
            if self._tokens[platform] < 1:
                wait_time = (1 - self._tokens[platform]) / tokens_per_second
                await asyncio.sleep(wait_time)
                self._tokens[platform] = 1

            # Consume token
            self._tokens[platform] -= 1

    def get_limit(self, platform: str) -> int:
        """Get the rate limit for a platform."""
        return self._limits.get(platform, 60)

    def set_limit(self, platform: str, limit: int) -> None:
        """Set a custom rate limit for a platform."""
        self._limits[platform] = limit
