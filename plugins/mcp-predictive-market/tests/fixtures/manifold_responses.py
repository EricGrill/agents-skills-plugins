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
