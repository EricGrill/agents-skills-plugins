# MCP Predictive Market Design

## Overview

An MCP server that queries prediction market platforms and aggregates data for comparison, tracking, and analysis.

## Decisions

| Aspect | Decision |
|--------|----------|
| Language | Python |
| Platforms | Kalshi, Polymarket, Metaculus, PredictIt, Manifold |
| Scope | Read-only MVP, trading extensibility later |
| Tools | 8 tools (search, tracking, analysis, browse) |
| State | mcp-memvid-state-service (4 capsules) |
| Queries | On-demand with caching |
| Matching | Semantic search + manual overrides + categories |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Client (Claude)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 mcp-predictive-market                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ Tool Layer  │ │ Normalizer  │ │   Platform Adapters     ││
│  │ (8 tools)   │ │ (unified    │ │ ┌───────┐ ┌──────────┐ ││
│  │             │ │  schema)    │ │ │Kalshi │ │Polymarket│ ││
│  └──────┬──────┘ └──────┬──────┘ │ ├───────┤ ├──────────┤ ││
│         │               │        │ │Metacul│ │PredictIt │ ││
│         └───────┬───────┘        │ ├───────┤ └──────────┘ ││
│                 │                │ │Manifold│             ││
│                 ▼                │ └───────┘              ││
│  ┌─────────────────────────────┐ └─────────────────────────┘│
│  │     MCP Client Interface    │                            │
│  │  (calls memvid-state-svc)   │                            │
│  └─────────────────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              mcp-memvid-state-service                        │
│         (semantic search, capsules, persistence)             │
└─────────────────────────────────────────────────────────────┘
```

**Components:**
- **Tool Layer** - 8 MCP tools exposed to the AI
- **Normalizer** - Converts each platform's data into a unified market schema
- **Platform Adapters** - One adapter per platform, handles API quirks
- **MCP Client Interface** - Calls memvid state service for storage/search

## Unified Market Schema

```python
@dataclass
class Market:
    # Identity
    id: str                    # Unique across platforms: "{platform}:{native_id}"
    platform: str              # "kalshi", "polymarket", "metaculus", "predictit", "manifold"
    native_id: str             # Platform's own ID
    url: str                   # Direct link to market

    # Content
    title: str                 # Market question
    description: str           # Full description/resolution criteria
    category: str              # Normalized category (politics, sports, crypto, ai, science, etc.)

    # Pricing
    probability: float         # 0.0 to 1.0 (main outcome or YES price)
    outcomes: list[Outcome]    # For multi-outcome markets

    # Metadata
    volume: float | None       # Trading volume (USD equivalent where possible)
    liquidity: float | None    # Available liquidity
    created_at: datetime
    closes_at: datetime | None
    resolved: bool
    resolution: str | None     # Outcome if resolved

    # For tracking
    last_fetched: datetime
    price_history: list[PricePoint]  # Populated for tracked markets

@dataclass
class Outcome:
    name: str
    probability: float

@dataclass
class PricePoint:
    timestamp: datetime
    probability: float
```

**Normalizations:**
- Prices converted to probability (0-1) regardless of platform format
- Volume converted to USD equivalent
- Categories mapped to a fixed set (~10 categories)
- All timestamps in UTC

## Platform Adapters

```python
class PlatformAdapter(Protocol):
    platform: str

    async def search_markets(self, query: str, category: str | None) -> list[Market]: ...
    async def get_market(self, native_id: str) -> Market: ...
    async def list_categories(self) -> list[str]: ...
    async def browse_category(self, category: str, limit: int) -> list[Market]: ...
```

| Platform | API Type | Auth Required | Rate Limits | Notes |
|----------|----------|---------------|-------------|-------|
| **Polymarket** | REST + GraphQL | No | Moderate | Uses CLOB API for odds, GraphQL for metadata |
| **Kalshi** | REST | No (public data) | Strict | Auth needed only for trading; public markets endpoint |
| **Metaculus** | REST | No | Generous | Community predictions, not real money |
| **PredictIt** | REST | No | Moderate | Limited new markets, but existing ones active |
| **Manifold** | REST | No | Generous | Play money, very open API, easiest to work with |

**Error handling per adapter:**
- Retry with exponential backoff on rate limits
- Return partial results if one platform fails
- Log failures but continue with available platforms

## MCP Tools

### Search Tools

```python
@tool
async def search_markets(query: str, platforms: list[str] | None = None) -> list[Market]:
    """
    Find markets matching a query across all platforms.

    Args:
        query: Natural language search (e.g., "Will Trump win 2024?")
        platforms: Optional filter to specific platforms

    Returns: Markets ranked by relevance, with platform source indicated
    """

@tool
async def get_market_odds(platform: str, market_id: str) -> Market:
    """
    Get current odds for a specific market.

    Args:
        platform: Platform name (kalshi, polymarket, etc.)
        market_id: The platform's native market ID
    """
```

### Tracking Tools

```python
@tool
async def track_market(platform: str, market_id: str, alias: str | None = None) -> TrackingConfirmation:
    """
    Add a market to the watchlist. Stores in memvid capsule "tracked-markets".

    Args:
        alias: Optional friendly name (e.g., "trump-2024")
    """

@tool
async def get_tracked_markets() -> list[TrackedMarket]:
    """
    Get all tracked markets with current odds and price history.
    Fetches fresh data, updates memvid, returns with sparkline trend.
    """
```

### Analysis Tools

```python
@tool
async def find_arbitrage(min_spread: float = 0.05) -> list[ArbitrageOpportunity]:
    """
    Find price discrepancies across platforms on equivalent markets.
    Uses semantic search + manual mappings to match markets.

    Args:
        min_spread: Minimum probability difference to report (default 5%)
    """

@tool
async def compare_platforms(query: str) -> ComparisonTable:
    """
    Side-by-side odds comparison for markets matching a query.
    Shows same event across platforms with price differences highlighted.
    """
```

### Browse Tools

```python
@tool
async def list_categories() -> list[Category]:
    """List available categories with market counts per platform."""

@tool
async def browse_category(category: str, limit: int = 20) -> list[Market]:
    """List top markets in a category across all platforms."""
```

## Memvid State Integration

### Capsule Structure

```
memvid capsules/
├── market-cache          # Cached market data from API calls
├── tracked-markets       # User's watchlist with price history
├── market-mappings       # Manual equivalence mappings across platforms
└── category-index        # Category metadata and market counts
```

### Usage Patterns

**Storing market data (after API fetch):**
```python
await memvid.store_memory(
    capsule="market-cache",
    content=market.title + " " + market.description,
    metadata={
        "market_id": market.id,
        "platform": market.platform,
        "category": market.category,
        "probability": market.probability,
        "fetched_at": datetime.utcnow().isoformat()
    }
)
```

**Semantic search (for search_markets tool):**
```python
# First check memvid cache
cached = await memvid.semantic_search(
    capsule="market-cache",
    query=user_query,
    top_k=20
)

# Filter stale results (>1 hour old), refresh those from APIs
fresh_ids = [m for m in cached if not is_stale(m)]
stale_platforms = get_platforms_needing_refresh(cached)

# Fetch fresh data for stale/missing, merge results
```

**Tracking markets:**
```python
await memvid.store_memory(
    capsule="tracked-markets",
    content=market.title,
    metadata={
        "market_id": market.id,
        "alias": user_alias,
        "price_history": [{"ts": now, "prob": market.probability}]
    }
)
```

**Cache invalidation:**
- Market cache entries expire after 1 hour (configurable)
- Tracked markets refresh on every get_tracked_markets call
- Stale check before returning any cached result

## Project Structure

```
mcp-predictive-market/
├── pyproject.toml              # uv/pip config, dependencies
├── README.md                   # Setup and usage docs
│
├── src/
│   └── mcp_predictive_market/
│       ├── __init__.py
│       ├── server.py           # MCP server entry point
│       ├── tools.py            # 8 tool definitions
│       │
│       ├── schema.py           # Market, Outcome, PricePoint dataclasses
│       ├── normalizer.py       # Platform-agnostic normalization logic
│       │
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── base.py         # PlatformAdapter protocol
│       │   ├── kalshi.py
│       │   ├── polymarket.py
│       │   ├── metaculus.py
│       │   ├── predictit.py
│       │   └── manifold.py
│       │
│       ├── state/
│       │   ├── __init__.py
│       │   └── memvid_client.py  # Wrapper to call memvid-state-service
│       │
│       └── analysis/
│           ├── __init__.py
│           ├── arbitrage.py      # Arbitrage detection logic
│           └── matching.py       # Market equivalence matching
│
└── tests/
    ├── test_adapters/
    ├── test_tools.py
    └── fixtures/                 # Sample API responses for testing
```

**Dependencies:**
- `mcp` - MCP Python SDK
- `httpx` - Async HTTP client
- `pydantic` - Data validation (optional, could use dataclasses)

## Error Handling

### Platform Failures

```python
class PlatformError(Exception):
    platform: str
    recoverable: bool

# On search, return partial results with error note
SearchResult(
    markets=[...],  # Markets from working platforms
    errors=[PlatformError("kalshi", "rate limited, retry in 60s")]
)
```

- Never fail entirely if one platform is down
- Return results from available platforms + list of errors
- Let the AI decide whether to retry or inform the user

### Rate Limiting

```python
rate_limiters = {
    "kalshi": AsyncLimiter(10, 60),      # 10 requests/minute
    "polymarket": AsyncLimiter(30, 60),
    "metaculus": AsyncLimiter(60, 60),
    "predictit": AsyncLimiter(20, 60),
    "manifold": AsyncLimiter(100, 60),
}
```

- Preemptive limiting (don't wait for 429s)
- Exponential backoff on actual rate limit responses
- Queue requests during backoff period

### Market Matching

**Problem:** "Trump wins 2024" on Polymarket vs "Trump wins presidential election" on Kalshi

**Approach:**
1. Semantic similarity score from memvid search
2. Confidence threshold (>0.85 = likely same)
3. Manual overrides stored in market-mappings capsule
4. Arbitrage tool shows confidence score for user verification

## Implementation Order

**Phase 1: Foundation**
1. Project setup with uv, pyproject.toml
2. Schema definitions (Market, Outcome, PricePoint)
3. Memvid client wrapper
4. Base adapter protocol

**Phase 2: First Platform (Manifold)**
- Start with Manifold - easiest API, most permissive
- Implement all 8 tools against single platform
- Validates the architecture end-to-end

**Phase 3: Remaining Adapters**
- Add Polymarket, Metaculus, PredictIt, Kalshi
- Each adapter follows same pattern
- Test cross-platform search and comparison

**Phase 4: Analysis Features**
- Arbitrage detection with confidence scoring
- Market matching/equivalence logic
- Category normalization across platforms

**Phase 5: Polish**
- Rate limiting and error handling
- Caching strategy refinement
- Documentation
