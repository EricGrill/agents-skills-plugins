"""Sample API responses from Metaculus for testing."""

SAMPLE_QUESTION = {
    "id": 12345,
    "title": "Will AGI be developed by 2030?",
    "description": "This question resolves positively if...",
    "url": "/questions/12345/will-agi-be-developed",
    "page_url": "https://www.metaculus.com/questions/12345/",
    "created_time": "2024-01-01T00:00:00Z",
    "close_time": "2029-12-31T23:59:59Z",
    "resolve_time": None,
    "resolution": None,
    "active_state": "OPEN",
    "community_prediction": {
        "full": {"q2": 0.35}
    },
    "number_of_forecasters": 500,
    "categories": [{"id": 1, "name": "AI"}],
}

SAMPLE_QUESTION_NO_PREDICTION = {
    "id": 12346,
    "title": "Will humans land on Mars by 2035?",
    "description": "This question resolves YES if...",
    "url": "/questions/12346/mars-landing-2035",
    "page_url": "https://www.metaculus.com/questions/12346/",
    "created_time": "2024-02-01T00:00:00Z",
    "close_time": "2034-12-31T23:59:59Z",
    "resolve_time": None,
    "resolution": None,
    "active_state": "OPEN",
    "community_prediction": None,
    "number_of_forecasters": 0,
    "categories": [{"id": 2, "name": "Space"}],
}

SAMPLE_QUESTION_RESOLVED = {
    "id": 12347,
    "title": "Will SpaceX launch Starship in 2024?",
    "description": "This question resolves YES if SpaceX successfully launches...",
    "url": "/questions/12347/starship-2024",
    "page_url": "https://www.metaculus.com/questions/12347/",
    "created_time": "2023-06-01T00:00:00Z",
    "close_time": "2024-12-31T23:59:59Z",
    "resolve_time": "2024-03-15T12:00:00Z",
    "resolution": 1.0,
    "active_state": "RESOLVED",
    "community_prediction": {
        "full": {"q2": 0.85}
    },
    "number_of_forecasters": 1200,
    "categories": [{"id": 2, "name": "Space"}, {"id": 3, "name": "Technology"}],
}

SAMPLE_QUESTIONS_LIST = {
    "results": [
        SAMPLE_QUESTION,
        {
            "id": 12348,
            "title": "Will Bitcoin exceed $100k by end of 2025?",
            "description": "Resolves YES if BTC/USD exceeds $100,000.",
            "url": "/questions/12348/bitcoin-100k-2025",
            "page_url": "https://www.metaculus.com/questions/12348/",
            "created_time": "2024-03-01T00:00:00Z",
            "close_time": "2025-12-31T23:59:59Z",
            "resolve_time": None,
            "resolution": None,
            "active_state": "OPEN",
            "community_prediction": {
                "full": {"q2": 0.55}
            },
            "number_of_forecasters": 300,
            "categories": [{"id": 4, "name": "Crypto"}, {"id": 5, "name": "Finance"}],
        },
    ],
    "count": 2,
    "next": None,
    "previous": None,
}

SAMPLE_QUESTIONS_BY_CATEGORY = {
    "results": [
        SAMPLE_QUESTION,
        SAMPLE_QUESTION_RESOLVED,
    ],
    "count": 2,
    "next": None,
    "previous": None,
}
