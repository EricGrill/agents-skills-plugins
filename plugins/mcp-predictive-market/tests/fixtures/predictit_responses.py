"""Sample API responses from PredictIt for testing."""

SAMPLE_MARKET = {
    "id": 7456,
    "name": "Who will win the 2024 presidential election?",
    "shortName": "2024 President",
    "image": "https://www.predictit.org/api/marketdata/image/7456",
    "url": "https://www.predictit.org/markets/detail/7456",
    "status": "Open",
    "contracts": [
        {
            "id": 23456,
            "name": "Donald Trump",
            "shortName": "Trump",
            "image": "https://www.predictit.org/api/marketdata/image/23456",
            "status": "Open",
            "lastTradePrice": 0.55,
            "bestBuyYesCost": 0.56,
            "bestBuyNoCost": 0.46,
            "bestSellYesCost": 0.54,
            "bestSellNoCost": 0.44,
        },
        {
            "id": 23457,
            "name": "Joe Biden",
            "shortName": "Biden",
            "image": "https://www.predictit.org/api/marketdata/image/23457",
            "status": "Open",
            "lastTradePrice": 0.35,
            "bestBuyYesCost": 0.36,
            "bestBuyNoCost": 0.66,
            "bestSellYesCost": 0.34,
            "bestSellNoCost": 0.64,
        },
    ],
    "timeStamp": "2024-01-01T12:00:00Z",
}

SAMPLE_MARKET_BINARY = {
    "id": 7500,
    "name": "Will Congress pass the spending bill by March 1?",
    "shortName": "Spending Bill March",
    "image": "https://www.predictit.org/api/marketdata/image/7500",
    "url": "https://www.predictit.org/markets/detail/7500",
    "status": "Open",
    "contracts": [
        {
            "id": 24000,
            "name": "Yes",
            "shortName": "Yes",
            "status": "Open",
            "lastTradePrice": 0.72,
            "bestBuyYesCost": 0.73,
            "bestBuyNoCost": 0.29,
            "bestSellYesCost": 0.71,
            "bestSellNoCost": 0.27,
        },
    ],
    "timeStamp": "2024-02-15T10:30:00Z",
}

SAMPLE_MARKET_CLOSED = {
    "id": 7100,
    "name": "Which party will control the Senate in 2025?",
    "shortName": "Senate 2025",
    "image": "https://www.predictit.org/api/marketdata/image/7100",
    "url": "https://www.predictit.org/markets/detail/7100",
    "status": "Closed",
    "contracts": [
        {
            "id": 22000,
            "name": "Republican",
            "shortName": "GOP",
            "status": "Closed",
            "lastTradePrice": 1.00,
            "bestBuyYesCost": None,
            "bestBuyNoCost": None,
            "bestSellYesCost": None,
            "bestSellNoCost": None,
        },
        {
            "id": 22001,
            "name": "Democratic",
            "shortName": "Dem",
            "status": "Closed",
            "lastTradePrice": 0.00,
            "bestBuyYesCost": None,
            "bestBuyNoCost": None,
            "bestSellYesCost": None,
            "bestSellNoCost": None,
        },
    ],
    "timeStamp": "2024-11-10T00:00:00Z",
}

SAMPLE_MARKET_NO_TRADES = {
    "id": 7600,
    "name": "Will X happen by Y date?",
    "shortName": "X by Y",
    "image": "https://www.predictit.org/api/marketdata/image/7600",
    "url": "https://www.predictit.org/markets/detail/7600",
    "status": "Open",
    "contracts": [
        {
            "id": 25000,
            "name": "Yes",
            "shortName": "Yes",
            "status": "Open",
            "lastTradePrice": None,
            "bestBuyYesCost": 0.50,
            "bestBuyNoCost": 0.52,
            "bestSellYesCost": None,
            "bestSellNoCost": None,
        },
    ],
    "timeStamp": "2024-03-01T08:00:00Z",
}

SAMPLE_ALL_MARKETS = {
    "markets": [
        SAMPLE_MARKET,
        SAMPLE_MARKET_BINARY,
        SAMPLE_MARKET_CLOSED,
    ]
}

SAMPLE_SEARCH_RESULTS = {
    "markets": [
        SAMPLE_MARKET,
        SAMPLE_MARKET_BINARY,
    ]
}
