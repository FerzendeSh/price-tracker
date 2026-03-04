from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.schemas.price_history import PriceHistoryRead

router = APIRouter(prefix="/products", tags=["Price History"])


@router.get("/{product_id}/prices", response_model=list[PriceHistoryRead])
def get_price_history(
    product_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return price history for a product, newest first."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prices = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    return prices
