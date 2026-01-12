<p align="center">
  <h1 align="center">MCP Predictive Market</h1>
  <p align="center">
    <strong>Query and analyze prediction markets through Claude</strong>
  </p>
  <p align="center">
    <a href="https://github.com/EricGrill/mcp-predictive-market/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/tools-8-green.svg" alt="8 Tools">
    <img src="https://img.shields.io/badge/platforms-5-purple.svg" alt="5 Platforms">
    <img src="https://img.shields.io/badge/python-%3E%3D3.11-orange.svg" alt="Python >= 3.11">
    <img src="https://img.shields.io/badge/tests-134%20passing-brightgreen.svg" alt="134 Tests">
  </p>
  <p align="center">
    <a href="#-quick-start">Quick Start</a> |
    <a href="#-available-tools">Tools</a> |
    <a href="#-supported-platforms">Platforms</a> |
    <a href="#%EF%B8%8F-configuration">Configuration</a> |
    <a href="https://github.com/EricGrill/agents-skills-plugins">Plugin Marketplace</a>
  </p>
</p>

---

## What is this?

An MCP (Model Context Protocol) server that aggregates prediction market data from **5 major platforms**. Search markets, compare odds, detect arbitrage opportunities, and track predictions through natural language.

**Works with Claude Desktop, Claude Code, Cursor, and any MCP-compatible client.**

**Part of the [Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins).**

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/EricGrill/mcp-predictive-market.git
cd mcp-predictive-market
uv sync

# Run the server
uv run python -m mcp_predictive_market.server
```

Add to your Claude config and start querying markets:

> "Find prediction markets about AI regulation"

---

## Why Use This?

| Feature | Description |
|---------|-------------|
| **Multi-Platform Search** | Query 5 prediction markets simultaneously |
| **Arbitrage Detection** | Find price discrepancies across platforms |
| **Market Tracking** | Build watchlists and monitor odds changes |
| **Platform Comparison** | Side-by-side odds for similar questions |
| **Unified Data Model** | Consistent market schema across all platforms |

---

## Available Tools

### Search & Discovery

| Tool | Description |
|------|-------------|
| `search_markets` | Search markets across all platforms by keyword |
| `list_categories` | Get available market categories |
| `browse_category` | Browse markets in a specific category |

### Market Data

| Tool | Description |
|------|-------------|
| `get_market_odds` | Get current odds for a specific market |
| `compare_platforms` | Side-by-side comparison of similar markets |

### Tracking

| Tool | Description |
|------|-------------|
| `track_market` | Add a market to your watchlist |
| `get_tracked_markets` | View all tracked markets with current prices |

### Analysis

| Tool | Description |
|------|-------------|
| `find_arbitrage` | Detect price discrepancies between platforms |

---

## Supported Platforms

| Platform | URL | Specialization |
|----------|-----|----------------|
| **Manifold Markets** | [manifold.markets](https://manifold.markets) | Play money, wide variety |
| **Polymarket** | [polymarket.com](https://polymarket.com) | Crypto, high liquidity |
| **Metaculus** | [metaculus.com](https://metaculus.com) | Science, long-term forecasts |
| **PredictIt** | [predictit.org](https://predictit.org) | US politics |
| **Kalshi** | [kalshi.com](https://kalshi.com) | CFTC-regulated, real money |

---

## Configuration

### Claude Desktop Setup

Add to your Claude Desktop config:

| Platform | Config Path |
|----------|-------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "prediction-market": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-predictive-market", "python", "-m", "mcp_predictive_market.server"]
    }
  }
}
```

### Claude Code Setup

Add to your project `.mcp.json` or `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "prediction-market": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-predictive-market", "python", "-m", "mcp_predictive_market.server"]
    }
  }
}
```

---

## Examples

<details>
<summary><b>Search & Discovery</b></summary>

```
"Find prediction markets about AI"
"What categories of markets are available?"
"Show me crypto markets on Polymarket"
"Browse politics markets"
```

</details>

<details>
<summary><b>Market Analysis</b></summary>

```
"Get current odds for Manifold market abc123"
"Compare odds for 'Will Bitcoin hit $100k?' across all platforms"
"Show me the probability of a 2024 recession on different platforms"
```

</details>

<details>
<summary><b>Arbitrage Detection</b></summary>

```
"Find arbitrage opportunities with at least 10% spread"
"Are there any markets with significantly different odds across platforms?"
"Show me the biggest price discrepancies right now"
```

</details>

<details>
<summary><b>Market Tracking</b></summary>

```
"Track the Polymarket election market"
"Show all my tracked markets"
"What are the current prices on my watchlist?"
```

</details>

---

## Development

```bash
# Clone
git clone https://github.com/EricGrill/mcp-predictive-market.git
cd mcp-predictive-market

# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest -v

# Run specific test file
uv run pytest tests/test_integration.py -v
```

### Project Structure

```
src/mcp_predictive_market/
├── server.py           # MCP server entry point
├── tools.py            # Tool handler implementations
├── schema.py           # Unified market data models
├── errors.py           # Custom exceptions
├── rate_limiter.py     # Per-platform rate limiting
├── adapters/           # Platform-specific adapters
│   ├── base.py         # Adapter protocol
│   ├── manifold.py
│   ├── polymarket.py
│   ├── metaculus.py
│   ├── predictit.py
│   └── kalshi.py
├── analysis/           # Market analysis modules
│   ├── matching.py     # Cross-platform market matching
│   └── arbitrage.py    # Arbitrage detection
└── state/              # State management
    └── memvid_client.py
```

---

## Troubleshooting

<details>
<summary><b>No results from a platform</b></summary>

1. Platform API may be rate-limited - wait and retry
2. Check platform is online: visit the website directly
3. Some platforms filter certain market types

</details>

<details>
<summary><b>Arbitrage opportunities not found</b></summary>

1. Lower the `min_spread` parameter (default is 5%)
2. Try broader search terms
3. Fewer opportunities exist in efficient markets

</details>

<details>
<summary><b>Market not found</b></summary>

1. Verify the market ID format (varies by platform)
2. Ensure the market hasn't been resolved/closed
3. Check you're using the correct platform name

</details>

---

## Related Projects

- [Claude Code Plugin Marketplace](https://github.com/EricGrill/agents-skills-plugins) - Discover more MCP plugins
- [MCP Proxmox Admin](https://github.com/EricGrill/mcp-proxmox-admin) - Manage Proxmox VE through Claude
- [MCP Memvid State Service](https://github.com/EricGrill/mcp-memvid-state-service) - Persistent state for MCP servers

---

## Contributing

Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `uv run pytest`
4. Commit: `git commit -m 'Add my feature'`
5. Push: `git push origin feature/my-feature`
6. Open a Pull Request

---

## License

MIT
