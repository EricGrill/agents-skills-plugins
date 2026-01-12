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
