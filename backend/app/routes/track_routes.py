"""Manual trigger to check price for a single product right now."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.services.price_checker import fetch_and_store_price
from app.schemas.price_history import PriceHistoryRead

router = APIRouter(prefix="/track", tags=["Tracking"])


@router.post("/{product_id}/check", response_model=PriceHistoryRead)
def check_price_now(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scrape the product page right now and store the price."""
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    entry = fetch_and_store_price(db, product)
    if entry is None:
        raise HTTPException(status_code=502, detail="Could not scrape the price from this URL")

    return entry
