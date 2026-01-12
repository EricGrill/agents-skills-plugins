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
