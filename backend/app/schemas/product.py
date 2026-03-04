from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, AnyUrl, Field

SUPPORTED_CURRENCIES = ("USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "INR", "IQD", "SEK", "NOK", "DKK", "CHF", "BRL", "MXN", "KRW")

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    url: AnyUrl
    currency: str = Field(default="USD", description="ISO 4217 currency code")
    target_price: Decimal | None = None

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    url: AnyUrl | None = None
    currency: str | None = None
    target_price: Decimal | None = None

class ProductRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    url: str
    currency: str = "USD"
    target_price: Decimal | None = None
    latest_price: Decimal | None = None
    price_change: Decimal | None = None  # difference from previous price
    price_change_pct: float | None = None  # percentage change

    class Config:
        from_attributes = True
