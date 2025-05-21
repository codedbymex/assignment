from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator


class RawProduct(BaseModel):
    name: str
    price_usd: Union[str, float]
    rating: Union[int, float, str, list]
    num_reviews: Union[str, int]
    description_raw: Optional[str] = None
    url: str
    last_scraped: datetime

    @field_validator("price_usd", mode="before")
    def parse_price(cls, v: Union[str, float]) -> float:
        if isinstance(v, str):
            try:
                return float(v.replace("$", "").strip())
            except ValueError:
                raise ValueError(f"Invalid price format: {v}")
        return float(v)

    @field_validator("num_reviews", mode="before")
    def parse_reviews(cls, v: Union[str, int]) -> int:
        if isinstance(v, str):
            parts = v.strip().split()
            if parts and parts[0].isdigit():
                return int(parts[0])
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"Invalid review count format: {v}")

    @field_validator("rating", mode="before")
    def parse_rating(cls, v: Union[str, int, float, list]) -> float:
        if isinstance(v, list):
            return float(len(v))
        try:
            return float(str(v).strip())
        except (ValueError, TypeError):
            return 0.0

class StructuredProduct(BaseModel):
    name: str
    price: float
    currency: str = "USD"
    rating: float
    num_reviews: int
    description: str
    url: str
    last_scraped: datetime

    brand: Optional[str]
    screen_inches: Optional[float]
    ram_gb: Optional[int]
    storage_gb: Optional[int]
    cpu: Optional[str]
    os: Optional[str]