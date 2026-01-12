"""Sample API responses from Kalshi for testing."""

SAMPLE_MARKET = {
    "market": {
        "ticker": "PRES-2024-DT",
        "event_ticker": "PRES-2024",
        "title": "Will Donald Trump win the 2024 presidential election?",
        "subtitle": "Event Contract",
        "yes_ask": 55,
        "yes_bid": 54,
        "no_ask": 46,
        "no_bid": 45,
        "last_price": 55,
        "volume": 1500000,
        "open_interest": 250000,
        "status": "active",
        "close_time": "2024-11-06T00:00:00Z",
        "expiration_time": "2024-11-30T00:00:00Z",
        "category": "Politics",
        "result": None,
    }
}

SAMPLE_MARKET_CRYPTO = {
    "market": {
        "ticker": "BTC-100K-JAN",
        "event_ticker": "BTC-100K",
        "title": "Will Bitcoin reach $100,000 by January 2025?",
        "subtitle": "Crypto Event",
        "yes_ask": 35,
        "yes_bid": 33,
        "no_ask": 68,
        "no_bid": 66,
        "last_price": 34,
        "volume": 500000,
        "open_interest": 75000,
        "status": "active",
        "close_time": "2025-01-31T23:59:59Z",
        "expiration_time": "2025-02-15T00:00:00Z",
        "category": "Crypto",
        "result": None,
    }
}

SAMPLE_MARKET_RESOLVED = {
    "market": {
        "ticker": "MIDTERM-2022-GOP",
        "event_ticker": "MIDTERM-2022",
        "title": "Will Republicans win the House in 2022?",
        "subtitle": "Midterm Elections",
        "yes_ask": 100,
        "yes_bid": 100,
        "no_ask": 0,
        "no_bid": 0,
        "last_price": 100,
        "volume": 2000000,
        "open_interest": 0,
        "status": "finalized",
        "close_time": "2022-11-08T00:00:00Z",
        "expiration_time": "2022-12-01T00:00:00Z",
        "category": "Politics",
        "result": "yes",
    }
}

SAMPLE_MARKET_NO_YES_ASK = {
    "market": {
        "ticker": "NEW-MARKET-123",
        "event_ticker": "NEW-EVENT",
        "title": "Will something happen?",
        "subtitle": "New Market",
        "yes_ask": None,
        "yes_bid": None,
        "no_ask": None,
        "no_bid": None,
        "last_price": 50,
        "volume": 0,
        "open_interest": 0,
        "status": "active",
        "close_time": "2025-06-01T00:00:00Z",
        "expiration_time": "2025-06-15T00:00:00Z",
        "category": "Science",
        "result": None,
    }
}

SAMPLE_MARKET_NO_LAST_PRICE = {
    "market": {
        "ticker": "BRAND-NEW-MKT",
        "event_ticker": "BRAND-NEW",
        "title": "Brand new market with no trades",
        "subtitle": "Brand New",
        "yes_ask": 60,
        "yes_bid": 55,
        "no_ask": 45,
        "no_bid": 40,
        "last_price": None,
        "volume": 0,
        "open_interest": 0,
        "status": "active",
        "close_time": "2025-12-31T23:59:59Z",
        "expiration_time": "2026-01-15T00:00:00Z",
        "category": "Entertainment",
        "result": None,
    }
}

SAMPLE_MARKETS_LIST = {
    "markets": [
        {
            "ticker": "PRES-2024-DT",
            "event_ticker": "PRES-2024",
            "title": "Will Donald Trump win the 2024 presidential election?",
            "subtitle": "Event Contract",
            "yes_ask": 55,
            "yes_bid": 54,
            "no_ask": 46,
            "no_bid": 45,
            "last_price": 55,
            "volume": 1500000,
            "open_interest": 250000,
            "status": "active",
            "close_time": "2024-11-06T00:00:00Z",
            "expiration_time": "2024-11-30T00:00:00Z",
            "category": "Politics",
            "result": None,
        },
        {
            "ticker": "PRES-2024-JB",
            "event_ticker": "PRES-2024",
            "title": "Will Joe Biden win the 2024 presidential election?",
            "subtitle": "Event Contract",
            "yes_ask": 30,
            "yes_bid": 28,
            "no_ask": 73,
            "no_bid": 71,
            "last_price": 29,
            "volume": 1200000,
            "open_interest": 180000,
            "status": "active",
            "close_time": "2024-11-06T00:00:00Z",
            "expiration_time": "2024-11-30T00:00:00Z",
            "category": "Politics",
            "result": None,
        },
        {
            "ticker": "BTC-100K-JAN",
            "event_ticker": "BTC-100K",
            "title": "Will Bitcoin reach $100,000 by January 2025?",
            "subtitle": "Crypto Event",
            "yes_ask": 35,
            "yes_bid": 33,
            "no_ask": 68,
            "no_bid": 66,
            "last_price": 34,
            "volume": 500000,
            "open_interest": 75000,
            "status": "active",
            "close_time": "2025-01-31T23:59:59Z",
            "expiration_time": "2025-02-15T00:00:00Z",
            "category": "Crypto",
            "result": None,
        },
    ],
    "cursor": "next_page_token",
}

SAMPLE_MARKETS_SEARCH_TRUMP = {
    "markets": [
        {
            "ticker": "PRES-2024-DT",
            "event_ticker": "PRES-2024",
            "title": "Will Donald Trump win the 2024 presidential election?",
            "subtitle": "Event Contract",
            "yes_ask": 55,
            "yes_bid": 54,
            "no_ask": 46,
            "no_bid": 45,
            "last_price": 55,
            "volume": 1500000,
            "open_interest": 250000,
            "status": "active",
            "close_time": "2024-11-06T00:00:00Z",
            "expiration_time": "2024-11-30T00:00:00Z",
            "category": "Politics",
            "result": None,
        },
    ],
    "cursor": None,
}

SAMPLE_MARKETS_EMPTY = {
    "markets": [],
    "cursor": None,
}

SAMPLE_MARKETS_POLITICS_CATEGORY = {
    "markets": [
        {
            "ticker": "PRES-2024-DT",
            "event_ticker": "PRES-2024",
            "title": "Will Donald Trump win the 2024 presidential election?",
            "subtitle": "Event Contract",
            "yes_ask": 55,
            "yes_bid": 54,
            "no_ask": 46,
            "no_bid": 45,
            "last_price": 55,
            "volume": 1500000,
            "open_interest": 250000,
            "status": "active",
            "close_time": "2024-11-06T00:00:00Z",
            "expiration_time": "2024-11-30T00:00:00Z",
            "category": "Politics",
            "result": None,
        },
        {
            "ticker": "PRES-2024-JB",
            "event_ticker": "PRES-2024",
            "title": "Will Joe Biden win the 2024 presidential election?",
            "subtitle": "Event Contract",
            "yes_ask": 30,
            "yes_bid": 28,
            "no_ask": 73,
            "no_bid": 71,
            "last_price": 29,
            "volume": 1200000,
            "open_interest": 180000,
            "status": "active",
            "close_time": "2024-11-06T00:00:00Z",
            "expiration_time": "2024-11-30T00:00:00Z",
            "category": "Politics",
            "result": None,
        },
    ],
    "cursor": None,
}
