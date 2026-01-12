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

    def test_recent_memories_signature(self):
        """Client should have recent_memories method."""
        client = MemvidClient()
        assert hasattr(client, "recent_memories")
        assert callable(client.recent_memories)
