"""
Notification service.

Sends a daily summary email when tracked products hit/drop below target price.
"""
from __future__ import annotations

import logging
import smtplib
from decimal import Decimal
from email.message import EmailMessage
from typing import TYPE_CHECKING

from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User

logger = logging.getLogger(__name__)


# ── Currency symbol lookup (duplicated lightly to avoid circular imports) ──
_SYMBOLS: dict[str, str] = {
    "USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", "AUD": "A$",
    "JPY": "¥", "CNY": "¥", "INR": "₹", "IQD": "ع.د", "SEK": "kr",
    "NOK": "kr", "DKK": "kr", "CHF": "CHF", "BRL": "R$", "MXN": "$",
    "KRW": "₩",
}

def _sym(code: str) -> str:
    return _SYMBOLS.get(code, code + " ")


def send_daily_alerts(user: "User", alerts: list[tuple["Product", Decimal]]) -> None:
    """
    Send one summary email to *user* listing every product that is at or
    below target price.

    Parameters
    ----------
    user   : the User ORM object (must have .email and .username)
    alerts : list of (Product, current_price) tuples
    """
    # ── Always log ──────────────────────────────────────────────
    for product, price in alerts:
        s = _sym(product.currency)
        logger.info(
            "PRICE ALERT  user=%s  product='%s'  price=%s%s  target=%s%s  url=%s",
            user.username, product.name,
            s, price, s, product.target_price, product.url,
        )

    # ── Build email ─────────────────────────────────────────────
    if not SMTP_HOST:
        logger.info("SMTP not configured — skipping email for %s", user.username)
        return

    if not user.email:
        logger.warning("User %s has no email — cannot send alert", user.username)
        return

    subject = f"🔔 Price Tracker Daily Alert — {len(alerts)} product(s) hit your target!"

    # ── Plain-text body ─────────────────────────────────────────
    lines = [
        f"Hi {user.username},\n",
        f"Great news! {len(alerts)} of your tracked products are at or below your target price.\n",
        "=" * 60,
    ]
    for product, price in alerts:
        s = _sym(product.currency)
        lines.append(f"\n  Product : {product.name}")
        lines.append(f"  Price   : {s}{price:.2f} {product.currency}")
        lines.append(f"  Target  : {s}{product.target_price:.2f}")
        savings = product.target_price - price
        lines.append(f"  Savings : {s}{savings:.2f} below target")
        lines.append(f"  URL     : {product.url}")
        lines.append("-" * 60)
    lines.append("\nHappy shopping!")
    lines.append("— Real-Time Price Tracker")
    plain = "\n".join(lines)

    # ── HTML body ───────────────────────────────────────────────
    rows_html = ""
    for product, price in alerts:
        s = _sym(product.currency)
        savings = product.target_price - price
        rows_html += f"""
        <tr>
          <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">
            <a href="{product.url}" style="color:#4f46e5;text-decoration:none;font-weight:600;">
              {product.name}
            </a>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#059669;font-weight:700;">
            {s}{price:.2f}
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">
            {s}{product.target_price:.2f}
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#059669;">
            ▼ {s}{savings:.2f}
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;">
            {product.currency}
          </td>
        </tr>"""

    html = f"""\
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1f2937;margin:0;padding:20px;background:#f9fafb;">
      <div style="max-width:640px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);">
        <div style="background:#4f46e5;padding:24px 30px;">
          <h1 style="margin:0;color:#fff;font-size:22px;">🔔 Price Alert</h1>
          <p style="margin:6px 0 0;color:#c7d2fe;font-size:14px;">
            {len(alerts)} product(s) hit your target price!
          </p>
        </div>
        <div style="padding:24px 30px;">
          <p>Hi <strong>{user.username}</strong>,</p>
          <p>The following products are now at or below the price you wanted:</p>
          <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
            <thead>
              <tr style="background:#f3f4f6;">
                <th style="text-align:left;padding:10px 14px;font-weight:600;">Product</th>
                <th style="text-align:left;padding:10px 14px;font-weight:600;">Current Price</th>
                <th style="text-align:left;padding:10px 14px;font-weight:600;">Target</th>
                <th style="text-align:left;padding:10px 14px;font-weight:600;">Savings</th>
                <th style="text-align:left;padding:10px 14px;font-weight:600;">Currency</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
          <p style="margin-top:20px;font-size:13px;color:#6b7280;">
            Act fast — prices can change at any time.
          </p>
        </div>
        <div style="background:#f3f4f6;padding:16px 30px;text-align:center;font-size:12px;color:#9ca3af;">
          Real-Time Price Tracker &bull; Automated daily alert
        </div>
      </div>
    </body>
    </html>"""

    try:
        _send_email(to=user.email, subject=subject, plain=plain, html=html)
        logger.info("Alert email sent to %s (%s products)", user.email, len(alerts))
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", user.email, exc)


def _send_email(to: str, subject: str, plain: str, html: str) -> None:
    email = EmailMessage()
    email["From"] = EMAIL_FROM
    email["To"] = to
    email["Subject"] = subject
    email.set_content(plain)
    email.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
