"""
Price scraping service.

Uses requests + BeautifulSoup to extract prices from product pages.
Supports common e-commerce meta tags and structured data patterns.
Auto-detects currency from page metadata.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.price_history import PriceHistory

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Map common symbols to ISO 4217 codes
SYMBOL_TO_CURRENCY: dict[str, str] = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
    "₩": "KRW",
    "R$": "BRL",
    "C$": "CAD",
    "A$": "AUD",
    "kr": "SEK",      # also NOK/DKK – we default to SEK
    "CHF": "CHF",
    "ع.د": "IQD",
}

# Known ISO 4217 codes to validate against
KNOWN_CURRENCIES = {
    "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CNY", "INR",
    "IQD", "SEK", "NOK", "DKK", "CHF", "BRL", "MXN", "KRW",
    "NZD", "SGD", "HKD", "TRY", "ZAR", "THB", "PHP", "MYR",
    "IDR", "PLN", "CZK", "HUF", "RUB", "ARS", "CLP", "COP",
    "PEN", "TWD", "AED", "SAR", "EGP", "PKR", "BDT", "VND",
    "NGN", "KES", "GHS", "TZS", "UGX", "QAR", "KWD", "BHD",
    "OMR", "JOD", "LBP", "MAD", "DZD", "TND", "LYD", "RON",
    "BGN", "HRK", "ISK", "UAH", "GEL", "MDL", "BAM", "RSD",
    "MKD", "ALL",
}


def _clean_price(raw: str) -> Optional[Decimal]:
    """Strip currency symbols and parse to Decimal."""
    cleaned = re.sub(r"[^\d.,]", "", raw)
    # Handle comma as thousands separator (1,299.99) or as decimal (12,99)
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts[-1]) <= 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def _detect_currency_from_symbol(text: str) -> Optional[str]:
    """Try to identify currency from symbols in a price string."""
    text = text.strip()
    # Check multi-char symbols first
    for symbol in ("R$", "C$", "A$", "CHF", "kr", "ع.د"):
        if symbol in text:
            return SYMBOL_TO_CURRENCY[symbol]
    # Then single-char symbols
    for symbol in ("€", "£", "₹", "₩", "¥", "$"):
        if symbol in text:
            return SYMBOL_TO_CURRENCY[symbol]
    return None


def scrape_price(url: str) -> tuple[Optional[Decimal], Optional[str]]:
    """
    Attempt to scrape a price AND currency from the given URL.
    Returns (price, currency_code).  Either or both may be None.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return None, None

    soup = BeautifulSoup(resp.text, "html.parser")
    detected_currency: Optional[str] = None

    # --- Strategy 1: OpenGraph / meta tags ---
    price_from_meta: Optional[Decimal] = None
    for attr in ("og:price:amount", "product:price:amount"):
        tag = soup.find("meta", attrs={"property": attr})
        if tag and tag.get("content"):
            price_from_meta = _clean_price(tag["content"])
            break

    # Currency meta tags
    for attr in ("og:price:currency", "product:price:currency"):
        tag = soup.find("meta", attrs={"property": attr})
        if tag and tag.get("content"):
            code = tag["content"].strip().upper()
            if code in KNOWN_CURRENCIES:
                detected_currency = code
                break

    if price_from_meta:
        return price_from_meta, detected_currency

    # --- Strategy 2: Schema.org JSON-LD ---
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                offers = item.get("offers", item)
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                p = offers.get("price") or offers.get("lowPrice")
                if p:
                    price = _clean_price(str(p))
                    if price:
                        cur = offers.get("priceCurrency", "").strip().upper()
                        if cur in KNOWN_CURRENCIES:
                            detected_currency = cur
                        return price, detected_currency
        except Exception:
            continue

    # --- Strategy 3: common CSS class/id patterns ---
    selectors = [
        "[data-price]",
        ".price .current-price",
        ".price-current",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price .a-offscreen",
        ".product-price",
        "[itemprop='price']",
        ".price",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get("content") or el.get("data-price") or el.get_text()
            if text:
                price = _clean_price(text.strip())
                if price and price > 0:
                    # Try to detect currency from the raw text
                    if not detected_currency:
                        detected_currency = _detect_currency_from_symbol(text.strip())
                    # Also check for itemprop="priceCurrency" nearby
                    cur_el = soup.select_one("[itemprop='priceCurrency']")
                    if cur_el:
                        code = (cur_el.get("content") or cur_el.get_text()).strip().upper()
                        if code in KNOWN_CURRENCIES:
                            detected_currency = code
                    return price, detected_currency

    logger.warning("Could not extract price from %s", url)
    return None, detected_currency


def fetch_and_store_price(db: Session, product: Product) -> Optional[PriceHistory]:
    """
    Scrape the price, update product currency if auto-detected,
    and persist a new PriceHistory row.
    """
    price, detected_currency = scrape_price(product.url)

    # Auto-update currency if detected and product still has default
    if detected_currency and detected_currency != product.currency:
        product.currency = detected_currency
        db.add(product)

    if price is None:
        db.commit()  # persist currency update even if price not found
        return None

    entry = PriceHistory(
        product_id=product.id,
        price=price,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def check_all_prices(db: Session) -> None:
    """
    Check prices for ALL tracked products.
    Called by the background scheduler.
    Collects alerts and sends a single summary email per user.

    Alert logic:
    - Only alert if price <= target_price
    - Only alert if price < last_alerted_price (or if never alerted before)
    - Skip users whose email is not verified
    - After sending, update last_alerted_price on each product
    """
    from app.services.notifier import send_daily_alerts

    products = db.query(Product).all()

    # Group alerts by user: { user_id: [ (product, current_price) ] }
    alerts: dict[int, list[tuple[Product, Decimal]]] = {}

    for product in products:
        try:
            entry = fetch_and_store_price(db, product)
            if not entry or not product.target_price:
                continue
            if entry.price > product.target_price:
                continue

            # Smart: only alert if price dropped lower than last alert
            if product.last_alerted_price is not None and entry.price >= product.last_alerted_price:
                continue

            alerts.setdefault(product.user_id, []).append((product, entry.price))
        except Exception as exc:
            logger.error("Error checking price for product %s: %s", product.id, exc)

    # Send one summary email per user who has alerts
    for user_id, user_alerts in alerts.items():
        try:
            user = user_alerts[0][0].user

            # Skip users with unverified email
            if not user.email_verified:
                logger.info(
                    "Skipping alerts for user %s — email not verified", user.username
                )
                continue

            send_daily_alerts(user, user_alerts)

            # Update last_alerted_price so we don't repeat
            for product, price in user_alerts:
                product.last_alerted_price = price
            db.commit()

        except Exception as exc:
            logger.error("Error sending alerts for user %s: %s", user_id, exc)
