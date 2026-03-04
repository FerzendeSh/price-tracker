from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.deps import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.price_checker import scrape_price

router = APIRouter(prefix="/products", tags=["Products"])


def _enrich(product: Product) -> dict:
    """Add latest_price, price_change, and price_change_pct to a product."""
    histories = product.price_histories or []
    latest = histories[-1] if histories else None
    previous = histories[-2] if len(histories) >= 2 else None

    price_change = None
    price_change_pct = None
    if latest and previous:
        price_change = latest.price - previous.price
        if previous.price:
            price_change_pct = round(float(price_change / previous.price * 100), 2)

    return {
        "id": product.id,
        "user_id": product.user_id,
        "name": product.name,
        "description": product.description,
        "url": product.url,
        "currency": product.currency,
        "target_price": product.target_price,
        "latest_price": latest.price if latest else None,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
    }


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Prevent duplicate URL per user
    existing = (
        db.query(Product)
        .filter(Product.user_id == current_user.id, Product.url == str(data.url))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="You are already tracking this URL")

    # Auto-detect currency from the page
    _price, detected_currency = scrape_price(str(data.url))
    currency = detected_currency or data.currency  # fallback to user choice

    product = Product(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        url=str(data.url),
        currency=currency,
        target_price=data.target_price,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Store the initial price if we got one
    if _price is not None:
        from datetime import datetime, timezone
        from app.models.price_history import PriceHistory
        entry = PriceHistory(
            product_id=product.id,
            price=_price,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(entry)
        db.commit()
        db.refresh(product)

    return _enrich(product)


@router.get("/", response_model=list[ProductRead])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = (
        db.query(Product)
        .filter(Product.user_id == current_user.id)
        .order_by(Product.id.desc())
        .all()
    )
    return [_enrich(p) for p in products]


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _enrich(product)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "url" and value is not None:
            value = str(value)
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return _enrich(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == current_user.id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
