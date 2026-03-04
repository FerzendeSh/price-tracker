from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Integer, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class PriceHistory(Base):
    __tablename__ = "price_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    product = relationship("Product", back_populates="price_histories")

# Composite index on product_id and timestamp
Index("ix_price_histories_product_id_timestamp", PriceHistory.product_id, PriceHistory.timestamp)
