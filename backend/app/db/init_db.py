"""
Seed the database with a default admin user if none exists.
Called during application startup (lifespan).
"""

import logging
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.auth import hash_password

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_USERNAME = "Admin"
DEFAULT_ADMIN_EMAIL = "rtptracker0@gmail.com"
DEFAULT_ADMIN_PASSWORD = "Admin@1234"


def seed_admin() -> None:
    """Ensure at least one admin user exists with a known password."""
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        if admin:
            # Ensure the admin flag is set (lightweight — no bcrypt)
            changed = False
            if not admin.is_admin:
                admin.is_admin = True
                changed = True
            if not admin.email_verified:
                admin.email_verified = True
                changed = True
            if changed:
                db.commit()
            logger.info("Admin user ready: %s", admin.username)
            return

        logger.info("No admin found — creating default admin user '%s'", DEFAULT_ADMIN_USERNAME)
        user = User(
            username=DEFAULT_ADMIN_USERNAME,
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(DEFAULT_ADMIN_PASSWORD),
            email_verified=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        logger.info("Default admin user created (username=%s)", DEFAULT_ADMIN_USERNAME)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to seed admin user: %s", exc)
    finally:
        db.close()
