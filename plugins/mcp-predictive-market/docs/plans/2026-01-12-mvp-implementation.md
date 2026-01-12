# MCP Predictive Market MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MCP server that queries prediction markets (Manifold, Polymarket, Metaculus, PredictIt, Kalshi) and aggregates data for comparison, tracking, and analysis.

**Architecture:** Python MCP server with platform adapters, unified market schema, and memvid-state-service integration for persistence and semantic search.

**Tech Stack:** Python 3.11+, MCP SDK, httpx, pydantic, pytest, uv

---

## Phase 1: Foundation

### Task 1: Project Setup with uv

**Files:**
- Create: `pyproject.toml`
- Create: `src/mcp_predictive_market/__init__.py`
- Create: `README.md`

**Step 1: Initialize project with uv**

Run:
```bash
cd /home/hitsnorth/mcp-predictive-market/.worktrees/mvp
uv init --lib --name mcp-predictive-market
```

**Step 2: Update pyproject.toml with dependencies**

Replace `pyproject.toml` with:

```toml
[project]
name = "mcp-predictive-market"
version = "0.1.0"
description = "MCP server for querying and aggregating prediction market data"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-httpx>=0.30.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_predictive_market"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 3: Create source directory structure**

Run:
```bash
mkdir -p src/mcp_predictive_market
touch src/mcp_predictive_market/__init__.py
mkdir -p tests
touch tests/__init__.py
```

**Step 4: Install dependencies**

Run:
```bash
uv sync --all-extras
```

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: initialize project with uv and dependencies"
```

---

### Task 2: Schema Definitions

**Files:**
- Create: `src/mcp_predictive_market/schema.py`
- Create: `tests/test_schema.py`

**Step 1: Write the failing test**

Create `tests/test_schema.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_schema.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'mcp_predictive_market.schema'"

**Step 3: Write minimal implementation**

Create `src/mcp_predictive_market/schema.py`:

```python
"""Unified market schema for prediction market data."""
from datetime import datetime
from pydantic import BaseModel, Field, computed_field, field_validator


class Outcome(BaseModel):
    """A possible outcome in a multi-outcome market."""

    name: str
    probability: float = Field(ge=0.0, le=1.0)


class PricePoint(BaseModel):
    """A historical price point for tracking."""

    timestamp: datetime
    probability: float = Field(ge=0.0, le=1.0)


class Market(BaseModel):
    """Unified market representation across all platforms."""

    # Identity
    platform: str
    native_id: str
    url: str

    # Content
    title: str
    description: str
    category: str

    # Pricing
    probability: float = Field(ge=0.0, le=1.0)
    outcomes: list[Outcome] = Field(default_factory=list)

    # Metadata
    volume: float | None = None
    liquidity: float | None = None
    created_at: datetime
    closes_at: datetime | None = None
    resolved: bool = False
    resolution: str | None = None

    # Tracking
    last_fetched: datetime
    price_history: list[PricePoint] = Field(default_factory=list)

    @computed_field
    @property
    def id(self) -> str:
        """Unique ID across platforms: platform:native_id."""
        return f"{self.platform}:{self.native_id}"

    @field_validator("probability")
    @classmethod
    def validate_probability(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Probability must be between 0 and 1")
        return v
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_schema.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/mcp_predictive_market/schema.py tests/test_schema.py
git commit -m "feat: add unified market schema with pydantic models"
```

---

### Task 3: Base Platform Adapter Protocol

**Files:**
- Create: `src/mcp_predictive_market/adapters/__init__.py`
- Create: `src/mcp_predictive_market/adapters/base.py`
- Create: `tests/test_adapters/__init__.py`
- Create: `tests/test_adapters/test_base.py`

**Step 1: Write the failing test**

Create `tests/test_adapters/__init__.py` (empty file).

Create `tests/test_adapters/test_base.py`:

```python
"""Tests for base adapter protocol."""
from typing import Protocol, runtime_checkable

import pytest

from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market


def test_platform_adapter_is_protocol():
    """PlatformAdapter should be a runtime-checkable Protocol."""
    assert isinstance(PlatformAdapter, type)
    # Should be able to check if a class implements the protocol
    assert hasattr(PlatformAdapter, "__protocol_attrs__") or hasattr(
        PlatformAdapter, "_is_protocol"
    )


def test_platform_adapter_required_methods():
    """PlatformAdapter should define required async methods."""
    # Check the protocol defines expected methods
    assert hasattr(PlatformAdapter, "search_markets")
    assert hasattr(PlatformAdapter, "get_market")
    assert hasattr(PlatformAdapter, "list_categories")
    assert hasattr(PlatformAdapter, "browse_category")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_adapters/test_base.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/mcp_predictive_market/adapters/__init__.py`:

```python
"""Platform adapters for prediction markets."""
from .base import PlatformAdapter

__all__ = ["PlatformAdapter"]
```

Create `src/mcp_predictive_market/adapters/base.py`:

```python
"""Base protocol for platform adapters."""
from typing import Protocol, runtime_checkable

from mcp_predictive_market.schema import Market


@runtime_checkable
class PlatformAdapter(Protocol):
    """Protocol that all platform adapters must implement."""

    platform: str

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query."""
        ...

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by its native ID."""
        ...

    async def list_categories(self) -> list[str]:
        """List available market categories."""
        ...

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a specific category."""
        ...
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_adapters/test_base.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/mcp_predictive_market/adapters/ tests/test_adapters/
git commit -m "feat: add PlatformAdapter protocol for adapter interface"
```

---

### Task 4: Memvid Client Wrapper

**Files:**
- Create: `src/mcp_predictive_market/state/__init__.py`
- Create: `src/mcp_predictive_market/state/memvid_client.py`
- Create: `tests/test_state/__init__.py`
- Create: `tests/test_state/test_memvid_client.py`

**Step 1: Write the failing test**

Create `tests/test_state/__init__.py` (empty file).

Create `tests/test_state/test_memvid_client.py`:

```python
"""Tests for memvid state client wrapper."""
import pytest

from mcp_predictive_market.state.memvid_client import MemvidClient


class TestMemvidClient:
    def test_client_initialization(self):
        """Client should initialize with capsule names."""
        client = MemvidClient()
        assert client.capsules == {
            "market-cache",
            "tracked-markets",
            "market-mappings",
            "category-index",
        }

    def test_store_memory_signature(self):
        """Client should have store_memory method."""
        client = MemvidClient()
        assert hasattr(client, "store_memory")
        assert callable(client.store_memory)

    def test_semantic_search_signature(self):
        """Client should have semantic_search method."""
        client = MemvidClient()
        assert hasattr(client, "semantic_search")
        assert callable(client.semantic_search)

    def test_text_search_signature(self):
        """Client should have text_search method."""
        client = MemvidClient()
        assert hasattr(client, "text_search")
        assert callable(client.text_search)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_state/test_memvid_client.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/mcp_predictive_market/state/__init__.py`:

```python
"""State management via memvid-state-service."""
from .memvid_client import MemvidClient

__all__ = ["MemvidClient"]
```

Create `src/mcp_predictive_market/state/memvid_client.py`:

```python
"""Client wrapper for mcp-memvid-state-service."""
from typing import Any


class MemvidClient:
    """Wrapper for interacting with memvid-state-service MCP.

    This client will call the memvid-state-service MCP server
    for persistent storage and semantic search capabilities.
    """

    CAPSULES = {
        "market-cache",
        "tracked-markets",
        "market-mappings",
        "category-index",
    }

    def __init__(self) -> None:
        """Initialize the memvid client."""
        self._capsules = self.CAPSULES.copy()

    @property
    def capsules(self) -> set[str]:
        """Return the set of capsule names used by this service."""
        return self._capsules

    async def store_memory(
        self,
        capsule: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store content in a memvid capsule.

        Args:
            capsule: Name of the capsule to store in
            content: Text content to store (will be embedded)
            metadata: Optional metadata dict

        Returns:
            ID of the stored memory
        """
        # TODO: Implement MCP client call to memvid-state-service
        raise NotImplementedError("MCP client integration pending")

    async def semantic_search(
        self,
        capsule: str,
        query: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Search capsule using semantic similarity.

        Args:
            capsule: Name of the capsule to search
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of matching memories with metadata
        """
        # TODO: Implement MCP client call to memvid-state-service
        raise NotImplementedError("MCP client integration pending")

    async def text_search(
        self,
        capsule: str,
        query: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Search capsule using BM25 text matching.

        Args:
            capsule: Name of the capsule to search
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of matching memories with metadata
        """
        # TODO: Implement MCP client call to memvid-state-service
        raise NotImplementedError("MCP client integration pending")

    async def recent_memories(
        self,
        capsule: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get most recent memories from a capsule.

        Args:
            capsule: Name of the capsule
            limit: Number of recent memories to return

        Returns:
            List of recent memories with metadata
        """
        # TODO: Implement MCP client call to memvid-state-service
        raise NotImplementedError("MCP client integration pending")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_state/test_memvid_client.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/mcp_predictive_market/state/ tests/test_state/
git commit -m "feat: add memvid client wrapper with method stubs"
```

---

## Phase 2: First Platform (Manifold)

### Task 5: Manifold Adapter - Basic Structure

**Files:**
- Create: `src/mcp_predictive_market/adapters/manifold.py`
- Create: `tests/test_adapters/test_manifold.py`
- Create: `tests/fixtures/__init__.py`
- Create: `tests/fixtures/manifold_responses.py`

**Step 1: Write the failing test**

Create `tests/fixtures/__init__.py` (empty file).

Create `tests/fixtures/manifold_responses.py`:

```python
"""Sample API responses from Manifold Markets for testing."""

SAMPLE_MARKET = {
    "id": "abc123xyz",
    "creatorId": "user123",
    "creatorUsername": "testuser",
    "creatorName": "Test User",
    "createdTime": 1704067200000,  # 2024-01-01
    "closeTime": 1735689600000,  # 2025-01-01
    "question": "Will AI pass the Turing test by 2025?",
    "description": "Resolves YES if a generally recognized AI system passes a standard Turing test.",
    "url": "https://manifold.markets/testuser/will-ai-pass-the-turing-test",
    "pool": {"YES": 1000, "NO": 1500},
    "probability": 0.4,
    "volume": 5000,
    "volume24Hours": 100,
    "isResolved": False,
    "resolution": None,
    "resolutionTime": None,
    "outcomeType": "BINARY",
    "mechanism": "cpmm-1",
    "groupSlugs": ["ai", "technology"],
}

SAMPLE_MARKETS_LIST = [
    SAMPLE_MARKET,
    {
        "id": "def456uvw",
        "creatorId": "user456",
        "creatorUsername": "anotheruser",
        "creatorName": "Another User",
        "createdTime": 1704153600000,
        "closeTime": None,
        "question": "Will Bitcoin hit $100k in 2025?",
        "description": "Resolves YES if BTC/USD exceeds $100,000.",
        "url": "https://manifold.markets/anotheruser/bitcoin-100k",
        "pool": {"YES": 2000, "NO": 3000},
        "probability": 0.35,
        "volume": 10000,
        "volume24Hours": 500,
        "isResolved": False,
        "resolution": None,
        "resolutionTime": None,
        "outcomeType": "BINARY",
        "mechanism": "cpmm-1",
        "groupSlugs": ["crypto", "bitcoin"],
    },
]
```

Create `tests/test_adapters/test_manifold.py`:

```python
"""Tests for Manifold Markets adapter."""
from datetime import datetime, timezone

import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market
from tests.fixtures.manifold_responses import SAMPLE_MARKET, SAMPLE_MARKETS_LIST


class TestManifoldAdapter:
    def test_implements_protocol(self):
        """ManifoldAdapter should implement PlatformAdapter protocol."""
        adapter = ManifoldAdapter()
        assert isinstance(adapter, PlatformAdapter)

    def test_platform_name(self):
        """Platform name should be 'manifold'."""
        adapter = ManifoldAdapter()
        assert adapter.platform == "manifold"


class TestManifoldGetMarket:
    @pytest.mark.asyncio
    async def test_get_market_success(self, httpx_mock: HTTPXMock):
        """Should fetch and parse a single market."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        adapter = ManifoldAdapter()
        market = await adapter.get_market("abc123xyz")

        assert isinstance(market, Market)
        assert market.platform == "manifold"
        assert market.native_id == "abc123xyz"
        assert market.title == "Will AI pass the Turing test by 2025?"
        assert market.probability == 0.4
        assert market.volume == 5000


class TestManifoldSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_markets(self, httpx_mock: HTTPXMock):
        """Should search markets by query."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=AI&limit=20",
            json=SAMPLE_MARKETS_LIST,
        )

        adapter = ManifoldAdapter()
        markets = await adapter.search_markets("AI")

        assert len(markets) == 2
        assert all(isinstance(m, Market) for m in markets)
        assert markets[0].title == "Will AI pass the Turing test by 2025?"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_adapters/test_manifold.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/mcp_predictive_market/adapters/manifold.py`:

```python
"""Manifold Markets platform adapter."""
from datetime import datetime, timezone

import httpx

from mcp_predictive_market.schema import Market, Outcome


class ManifoldAdapter:
    """Adapter for Manifold Markets API."""

    platform = "manifold"
    BASE_URL = "https://api.manifold.markets/v0"

    # Map Manifold group slugs to normalized categories
    CATEGORY_MAP = {
        "politics": "politics",
        "us-politics": "politics",
        "world-politics": "politics",
        "sports": "sports",
        "crypto": "crypto",
        "bitcoin": "crypto",
        "ethereum": "crypto",
        "ai": "ai",
        "technology": "technology",
        "science": "science",
        "economics": "economics",
        "finance": "finance",
        "entertainment": "entertainment",
        "gaming": "gaming",
    }

    def __init__(self) -> None:
        """Initialize the adapter with an HTTP client."""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_market(self, native_id: str) -> Market:
        """Get a specific market by ID."""
        response = await self._client.get(f"{self.BASE_URL}/market/{native_id}")
        response.raise_for_status()
        data = response.json()
        return self._parse_market(data)

    async def search_markets(
        self, query: str, category: str | None = None
    ) -> list[Market]:
        """Search for markets matching a query."""
        params = {"term": query, "limit": 20}
        response = await self._client.get(
            f"{self.BASE_URL}/search-markets", params=params
        )
        response.raise_for_status()
        data = response.json()
        return [self._parse_market(m) for m in data]

    async def list_categories(self) -> list[str]:
        """List available categories (normalized)."""
        return sorted(set(self.CATEGORY_MAP.values()))

    async def browse_category(self, category: str, limit: int = 20) -> list[Market]:
        """Browse markets in a category."""
        # Manifold uses group slugs, find matching ones
        slugs = [k for k, v in self.CATEGORY_MAP.items() if v == category]
        if not slugs:
            return []

        # Search with first matching slug as filter
        params = {"term": "", "filter": "open", "limit": limit}
        response = await self._client.get(
            f"{self.BASE_URL}/search-markets", params=params
        )
        response.raise_for_status()
        data = response.json()

        # Filter to matching categories
        markets = []
        for m in data:
            market = self._parse_market(m)
            if market.category == category:
                markets.append(market)
                if len(markets) >= limit:
                    break
        return markets

    def _parse_market(self, data: dict) -> Market:
        """Parse Manifold API response into Market schema."""
        # Determine category from group slugs
        category = "other"
        for slug in data.get("groupSlugs", []):
            if slug in self.CATEGORY_MAP:
                category = self.CATEGORY_MAP[slug]
                break

        # Parse timestamps (Manifold uses milliseconds)
        created_at = datetime.fromtimestamp(
            data["createdTime"] / 1000, tz=timezone.utc
        )
        closes_at = None
        if data.get("closeTime"):
            closes_at = datetime.fromtimestamp(
                data["closeTime"] / 1000, tz=timezone.utc
            )

        # Build outcomes for binary markets
        outcomes = []
        if data.get("outcomeType") == "BINARY":
            prob = data.get("probability", 0.5)
            outcomes = [
                Outcome(name="Yes", probability=prob),
                Outcome(name="No", probability=1 - prob),
            ]

        return Market(
            platform=self.platform,
            native_id=data["id"],
            url=data.get("url", f"https://manifold.markets/market/{data['id']}"),
            title=data["question"],
            description=data.get("description", ""),
            category=category,
            probability=data.get("probability", 0.5),
            outcomes=outcomes,
            volume=data.get("volume"),
            liquidity=None,  # Manifold doesn't expose this directly
            created_at=created_at,
            closes_at=closes_at,
            resolved=data.get("isResolved", False),
            resolution=data.get("resolution"),
            last_fetched=datetime.now(timezone.utc),
            price_history=[],
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_adapters/test_manifold.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/mcp_predictive_market/adapters/manifold.py tests/test_adapters/test_manifold.py tests/fixtures/
git commit -m "feat: add Manifold Markets adapter with search and get_market"
```

---

### Task 6: MCP Server Entry Point

**Files:**
- Create: `src/mcp_predictive_market/server.py`
- Create: `tests/test_server.py`

**Step 1: Write the failing test**

Create `tests/test_server.py`:

```python
"""Tests for MCP server entry point."""
import pytest

from mcp_predictive_market.server import create_server


def test_create_server_returns_mcp_server():
    """create_server should return an MCP Server instance."""
    server = create_server()
    # Check it has the expected MCP server attributes
    assert hasattr(server, "name")
    assert server.name == "mcp-predictive-market"


def test_server_has_tools():
    """Server should register the expected tools."""
    server = create_server()
    # The server should have tools registered
    assert hasattr(server, "list_tools") or hasattr(server, "_tool_manager")
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_server.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/mcp_predictive_market/server.py`:

```python
"""MCP server entry point for prediction market aggregation."""
from mcp.server import Server
from mcp.types import Tool, TextContent

from mcp_predictive_market.adapters.manifold import ManifoldAdapter


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("mcp-predictive-market")

    # Initialize adapters
    adapters = {
        "manifold": ManifoldAdapter(),
    }

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="search_markets",
                description="Search for prediction markets across platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'Will Trump win 2024?')",
                        },
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: filter to specific platforms",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_market_odds",
                description="Get current odds for a specific market",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Platform name (manifold, polymarket, etc.)",
                        },
                        "market_id": {
                            "type": "string",
                            "description": "The market's native ID",
                        },
                    },
                    "required": ["platform", "market_id"],
                },
            ),
            Tool(
                name="list_categories",
                description="List available market categories",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="browse_category",
                description="Browse markets in a specific category",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to browse",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max markets to return (default 20)",
                            "default": 20,
                        },
                    },
                    "required": ["category"],
                },
            ),
        ]

    return server


def main() -> None:
    """Run the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    server = create_server()

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_server.py -v`
Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/mcp_predictive_market/server.py tests/test_server.py
git commit -m "feat: add MCP server entry point with tool definitions"
```

---

### Task 7: Implement Tool Handlers

**Files:**
- Create: `src/mcp_predictive_market/tools.py`
- Modify: `src/mcp_predictive_market/server.py`
- Create: `tests/test_tools.py`

**Step 1: Write the failing test**

Create `tests/test_tools.py`:

```python
"""Tests for MCP tool handlers."""
import pytest
from pytest_httpx import HTTPXMock

from mcp_predictive_market.tools import ToolHandlers
from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from tests.fixtures.manifold_responses import SAMPLE_MARKET, SAMPLE_MARKETS_LIST


class TestSearchMarkets:
    @pytest.mark.asyncio
    async def test_search_returns_formatted_results(self, httpx_mock: HTTPXMock):
        """search_markets should return formatted market data."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/search-markets?term=AI&limit=20",
            json=SAMPLE_MARKETS_LIST,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.search_markets(query="AI")

        assert "markets" in result
        assert len(result["markets"]) == 2
        assert result["markets"][0]["title"] == "Will AI pass the Turing test by 2025?"
        assert result["markets"][0]["probability"] == 0.4


class TestGetMarketOdds:
    @pytest.mark.asyncio
    async def test_get_market_odds_success(self, httpx_mock: HTTPXMock):
        """get_market_odds should return market details."""
        httpx_mock.add_response(
            url="https://api.manifold.markets/v0/market/abc123xyz",
            json=SAMPLE_MARKET,
        )

        adapters = {"manifold": ManifoldAdapter()}
        handlers = ToolHandlers(adapters)

        result = await handlers.get_market_odds(
            platform="manifold", market_id="abc123xyz"
        )

        assert result["platform"] == "manifold"
        assert result["probability"] == 0.4
        assert result["title"] == "Will AI pass the Turing test by 2025?"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tools.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

Create `src/mcp_predictive_market/tools.py`:

```python
"""Tool handler implementations for the MCP server."""
from typing import Any

from mcp_predictive_market.adapters.base import PlatformAdapter
from mcp_predictive_market.schema import Market


class ToolHandlers:
    """Handlers for MCP tool calls."""

    def __init__(self, adapters: dict[str, PlatformAdapter]) -> None:
        """Initialize with platform adapters."""
        self._adapters = adapters

    def _market_to_dict(self, market: Market) -> dict[str, Any]:
        """Convert Market to API response dict."""
        return {
            "id": market.id,
            "platform": market.platform,
            "native_id": market.native_id,
            "url": market.url,
            "title": market.title,
            "description": market.description,
            "category": market.category,
            "probability": market.probability,
            "volume": market.volume,
            "resolved": market.resolved,
            "resolution": market.resolution,
            "last_fetched": market.last_fetched.isoformat(),
        }

    async def search_markets(
        self,
        query: str,
        platforms: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search for markets across platforms."""
        target_adapters = self._adapters
        if platforms:
            target_adapters = {
                k: v for k, v in self._adapters.items() if k in platforms
            }

        all_markets = []
        errors = []

        for name, adapter in target_adapters.items():
            try:
                markets = await adapter.search_markets(query)
                all_markets.extend(markets)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        return {
            "markets": [self._market_to_dict(m) for m in all_markets],
            "errors": errors,
        }

    async def get_market_odds(
        self,
        platform: str,
        market_id: str,
    ) -> dict[str, Any]:
        """Get current odds for a specific market."""
        if platform not in self._adapters:
            raise ValueError(f"Unknown platform: {platform}")

        adapter = self._adapters[platform]
        market = await adapter.get_market(market_id)
        return self._market_to_dict(market)

    async def list_categories(self) -> dict[str, Any]:
        """List available categories across platforms."""
        all_categories: set[str] = set()

        for adapter in self._adapters.values():
            try:
                categories = await adapter.list_categories()
                all_categories.update(categories)
            except Exception:
                pass

        return {"categories": sorted(all_categories)}

    async def browse_category(
        self,
        category: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Browse markets in a category."""
        all_markets = []
        errors = []

        for name, adapter in self._adapters.items():
            try:
                markets = await adapter.browse_category(category, limit)
                all_markets.extend(markets)
            except Exception as e:
                errors.append({"platform": name, "error": str(e)})

        # Sort by volume (highest first) and limit
        all_markets.sort(key=lambda m: m.volume or 0, reverse=True)
        all_markets = all_markets[:limit]

        return {
            "markets": [self._market_to_dict(m) for m in all_markets],
            "errors": errors,
        }
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_tools.py -v`
Expected: PASS (2 tests)

**Step 5: Update server.py to use ToolHandlers**

Update `src/mcp_predictive_market/server.py` - add call_tool handler:

```python
"""MCP server entry point for prediction market aggregation."""
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

from mcp_predictive_market.adapters.manifold import ManifoldAdapter
from mcp_predictive_market.tools import ToolHandlers


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("mcp-predictive-market")

    # Initialize adapters
    adapters = {
        "manifold": ManifoldAdapter(),
    }
    handlers = ToolHandlers(adapters)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="search_markets",
                description="Search for prediction markets across platforms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'Will Trump win 2024?')",
                        },
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: filter to specific platforms",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_market_odds",
                description="Get current odds for a specific market",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Platform name (manifold, polymarket, etc.)",
                        },
                        "market_id": {
                            "type": "string",
                            "description": "The market's native ID",
                        },
                    },
                    "required": ["platform", "market_id"],
                },
            ),
            Tool(
                name="list_categories",
                description="List available market categories",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="browse_category",
                description="Browse markets in a specific category",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to browse",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max markets to return (default 20)",
                            "default": 20,
                        },
                    },
                    "required": ["category"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        if name == "search_markets":
            result = await handlers.search_markets(**arguments)
        elif name == "get_market_odds":
            result = await handlers.get_market_odds(**arguments)
        elif name == "list_categories":
            result = await handlers.list_categories()
        elif name == "browse_category":
            result = await handlers.browse_category(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    return server


def main() -> None:
    """Run the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    server = create_server()

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
```

**Step 6: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass

**Step 7: Commit**

```bash
git add src/mcp_predictive_market/tools.py src/mcp_predictive_market/server.py tests/test_tools.py
git commit -m "feat: implement tool handlers for search, get_market, categories"
```

---

## Phase 3: Remaining Adapters

### Task 8: Polymarket Adapter

**Files:**
- Create: `src/mcp_predictive_market/adapters/polymarket.py`
- Create: `tests/test_adapters/test_polymarket.py`
- Create: `tests/fixtures/polymarket_responses.py`

**Note:** Polymarket uses a GraphQL API for market data. Follow the same pattern as Manifold adapter. Key differences:
- Base URL: `https://gamma-api.polymarket.com`
- Uses GraphQL queries
- Probability from `outcomePrices`
- Category from `tags`

**Step 1-5:** Follow the same TDD pattern as Task 5.

**Commit message:** `feat: add Polymarket adapter`

---

### Task 9: Metaculus Adapter

**Files:**
- Create: `src/mcp_predictive_market/adapters/metaculus.py`
- Create: `tests/test_adapters/test_metaculus.py`
- Create: `tests/fixtures/metaculus_responses.py`

**Note:** Metaculus uses a REST API.
- Base URL: `https://www.metaculus.com/api2`
- Probability from `community_prediction.full.q2`
- Category from `categories`

**Step 1-5:** Follow the same TDD pattern as Task 5.

**Commit message:** `feat: add Metaculus adapter`

---

### Task 10: PredictIt Adapter

**Files:**
- Create: `src/mcp_predictive_market/adapters/predictit.py`
- Create: `tests/test_adapters/test_predictit.py`
- Create: `tests/fixtures/predictit_responses.py`

**Note:** PredictIt has a simple REST API.
- Base URL: `https://www.predictit.org/api/marketdata`
- Probability from `lastTradePrice` or `bestBuyYesCost`
- Categories from `market.name` patterns

**Step 1-5:** Follow the same TDD pattern as Task 5.

**Commit message:** `feat: add PredictIt adapter`

---

### Task 11: Kalshi Adapter

**Files:**
- Create: `src/mcp_predictive_market/adapters/kalshi.py`
- Create: `tests/test_adapters/test_kalshi.py`
- Create: `tests/fixtures/kalshi_responses.py`

**Note:** Kalshi has a REST API (public for market data).
- Base URL: `https://api.elections.kalshi.com/trade-api/v2`
- Probability from `yes_ask` price
- Strict rate limits (10 req/min)

**Step 1-5:** Follow the same TDD pattern as Task 5.

**Commit message:** `feat: add Kalshi adapter`

---

### Task 12: Register All Adapters

**Files:**
- Modify: `src/mcp_predictive_market/server.py`
- Modify: `src/mcp_predictive_market/adapters/__init__.py`

**Step 1: Update adapters/__init__.py**

```python
"""Platform adapters for prediction markets."""
from .base import PlatformAdapter
from .manifold import ManifoldAdapter
from .polymarket import PolymarketAdapter
from .metaculus import MetaculusAdapter
from .predictit import PredictItAdapter
from .kalshi import KalshiAdapter

__all__ = [
    "PlatformAdapter",
    "ManifoldAdapter",
    "PolymarketAdapter",
    "MetaculusAdapter",
    "PredictItAdapter",
    "KalshiAdapter",
]
```

**Step 2: Update server.py to use all adapters**

Update the adapters dict in `create_server()`:

```python
adapters = {
    "manifold": ManifoldAdapter(),
    "polymarket": PolymarketAdapter(),
    "metaculus": MetaculusAdapter(),
    "predictit": PredictItAdapter(),
    "kalshi": KalshiAdapter(),
}
```

**Step 3: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass

**Step 4: Commit**

```bash
git add src/mcp_predictive_market/adapters/__init__.py src/mcp_predictive_market/server.py
git commit -m "feat: register all platform adapters in server"
```

---

## Phase 4: Analysis Features

### Task 13: Market Matching Logic

**Files:**
- Create: `src/mcp_predictive_market/analysis/__init__.py`
- Create: `src/mcp_predictive_market/analysis/matching.py`
- Create: `tests/test_analysis/__init__.py`
- Create: `tests/test_analysis/test_matching.py`

Implement semantic similarity matching for markets. Use memvid's semantic_search to find similar markets across platforms.

**Commit message:** `feat: add market matching with semantic similarity`

---

### Task 14: Arbitrage Detection

**Files:**
- Create: `src/mcp_predictive_market/analysis/arbitrage.py`
- Create: `tests/test_analysis/test_arbitrage.py`

Implement arbitrage detection:
1. Find similar markets across platforms (using matching.py)
2. Compare probabilities
3. Flag discrepancies above threshold

**Commit message:** `feat: add arbitrage detection across platforms`

---

### Task 15: Tracking Tools

**Files:**
- Modify: `src/mcp_predictive_market/tools.py`
- Modify: `src/mcp_predictive_market/server.py`
- Create: `tests/test_tracking.py`

Add tools:
- `track_market` - Store in memvid tracked-markets capsule
- `get_tracked_markets` - Retrieve and refresh tracked markets

**Commit message:** `feat: add market tracking tools with memvid persistence`

---

### Task 16: Analysis Tools

**Files:**
- Modify: `src/mcp_predictive_market/tools.py`
- Modify: `src/mcp_predictive_market/server.py`

Add tools:
- `find_arbitrage` - Call arbitrage detection
- `compare_platforms` - Side-by-side comparison

**Commit message:** `feat: add arbitrage and comparison tools`

---

## Phase 5: Polish

### Task 17: Rate Limiting

**Files:**
- Create: `src/mcp_predictive_market/rate_limiter.py`
- Modify all adapter files to use rate limiter

Implement per-platform rate limiting using asyncio.

**Commit message:** `feat: add per-platform rate limiting`

---

### Task 18: Error Handling

**Files:**
- Create: `src/mcp_predictive_market/errors.py`
- Modify: `src/mcp_predictive_market/tools.py`

Create PlatformError exception, ensure partial results on failures.

**Commit message:** `feat: improve error handling with partial results`

---

### Task 19: Documentation

**Files:**
- Create: `README.md` (update with usage)
- Ensure all public functions have docstrings

**Commit message:** `docs: add README with setup and usage instructions`

---

### Task 20: Final Integration Test

**Files:**
- Create: `tests/test_integration.py`

End-to-end test using all platforms (with mocked responses).

**Commit message:** `test: add integration tests for full workflow`

---

## Execution Complete

After all tasks are done:

1. Merge feature branch to main
2. Tag release v0.1.0
3. Close worktree
