"""Unified market schema for prediction market data."""
from datetime import datetime
from pydantic import BaseModel, Field, computed_field, field_validator


class Outcome(BaseModel):
    """A possible outcome in a multi-outcome market."""

    name: str
    probability: float = Field(ge=0.0, le=1.0)


class PricePoint(BaseModel):
    """A historical price point for tracking."""

    timestamp: datetime
    probability: float = Field(ge=0.0, le=1.0)


class Market(BaseModel):
    """Unified market representation across all platforms."""

    # Identity
    platform: str
    native_id: str
    url: str

    # Content
    title: str
    description: str
    category: str

    # Pricing
    probability: float = Field(ge=0.0, le=1.0)
    outcomes: list[Outcome] = Field(default_factory=list)

    # Metadata
    volume: float | None = None
    liquidity: float | None = None
    created_at: datetime
    closes_at: datetime | None = None
    resolved: bool = False
    resolution: str | None = None

    # Tracking
    last_fetched: datetime
    price_history: list[PricePoint] = Field(default_factory=list)

    @computed_field
    @property
    def id(self) -> str:
        """Unique ID across platforms: platform:native_id."""
        return f"{self.platform}:{self.native_id}"

    @field_validator("probability")
    @classmethod
    def validate_probability(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Probability must be between 0 and 1")
        return v
