"""
Background scheduler that checks all tracked product prices once per day.
Uses APScheduler with a CronTrigger (default: every day at 08:00).
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import PRICE_CHECK_HOUR, PRICE_CHECK_MINUTE
from app.db.session import SessionLocal
from app.services.price_checker import check_all_prices

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _run_price_check() -> None:
    """Wrapper that opens a DB session, runs checks, then closes it."""
    logger.info("Daily price check starting …")
    db = SessionLocal()
    try:
        check_all_prices(db)
    except Exception as exc:
        logger.error("Daily price check failed: %s", exc)
    finally:
        db.close()
    logger.info("Daily price check finished.")


def start_scheduler() -> None:
    scheduler.add_job(
        _run_price_check,
        trigger=CronTrigger(hour=PRICE_CHECK_HOUR, minute=PRICE_CHECK_MINUTE),
        id="daily_price_checker",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Price check scheduler started — runs daily at %02d:%02d",
        PRICE_CHECK_HOUR, PRICE_CHECK_MINUTE,
    )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Price check scheduler stopped.")
