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
