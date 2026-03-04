from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class PriceHistoryCreate(BaseModel):
    product_id: int
    price: Decimal
    timestamp: datetime | None = None  # you can set default in DB/service

class PriceHistoryRead(BaseModel):
    id: int
    product_id: int
    price: Decimal
    timestamp: datetime

    class Config:
        from_attributes = True
