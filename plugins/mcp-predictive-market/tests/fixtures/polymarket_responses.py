"""Sample API responses from Polymarket for testing."""

SAMPLE_MARKET = {
    "id": "0xabc123def",
    "question": "Will Bitcoin reach $100k by end of 2025?",
    "description": "This market resolves YES if BTC/USD exceeds $100,000.",
    "slug": "bitcoin-100k-2025",
    "active": True,
    "closed": False,
    "archived": False,
    "outcomes": ["Yes", "No"],
    "outcomePrices": ["0.45", "0.55"],
    "volume": "125000.00",
    "liquidity": "50000.00",
    "startDate": "2024-01-01T00:00:00Z",
    "endDate": "2025-12-31T23:59:59Z",
    "tags": ["crypto", "bitcoin"],
}

SAMPLE_MARKETS_LIST = [
    SAMPLE_MARKET,
    {
        "id": "0xdef456ghi",
        "question": "Will ETH flip BTC by market cap?",
        "description": "Resolves YES if ETH market cap exceeds BTC.",
        "slug": "eth-flip-btc",
        "active": True,
        "closed": False,
        "archived": False,
        "outcomes": ["Yes", "No"],
        "outcomePrices": ["0.12", "0.88"],
        "volume": "75000.00",
        "liquidity": "25000.00",
        "startDate": "2024-02-01T00:00:00Z",
        "endDate": None,
        "tags": ["crypto", "ethereum"],
    },
]
