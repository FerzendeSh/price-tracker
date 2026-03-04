import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# ------------------------------------------------------------
# Load .env only in local development (never on Render)
# Render sets the env var RENDER=1 inside the runtime.
# ------------------------------------------------------------
if os.getenv("RENDER") is None:
    load_dotenv()

# ------------------------------------------------------------
# DATABASE_URL
# ------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# If running on Render, DATABASE_URL must be provided by Render
if os.getenv("RENDER") and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required on Render (set in Render env vars / blueprint).")

# Local fallback: build from DB_* variables (for laptop/dev)
if not DATABASE_URL:
    _DB_USER = os.getenv("DB_USER", "postgres")
    _DB_PASS = os.getenv("DB_PASS", "")  # don't hardcode secrets
    _DB_HOST = os.getenv("DB_HOST", "localhost")
    _DB_PORT = os.getenv("DB_PORT", "5432")
    _DB_NAME = os.getenv("DB_NAME", "real_time_price")

    if not _DB_PASS:
        raise RuntimeError("DB_PASS is not set for local development.")

    DATABASE_URL = (
        f"postgresql+psycopg2://{_DB_USER}:{quote_plus(_DB_PASS)}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}"
    )

# Normalize scheme for SQLAlchemy + psycopg2 driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# ------------------------------------------------------------
# Auth / Security
# ------------------------------------------------------------
SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_LATER")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ------------------------------------------------------------
# CORS
# (Render: set CORS_ORIGINS to your deployed frontend URL)
# ------------------------------------------------------------
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

# ------------------------------------------------------------
# Daily price-check schedule
# ------------------------------------------------------------
PRICE_CHECK_HOUR: int = int(os.getenv("PRICE_CHECK_HOUR", "8"))
PRICE_CHECK_MINUTE: int = int(os.getenv("PRICE_CHECK_MINUTE", "0"))

# ------------------------------------------------------------
# SMTP / Email notifications
# ------------------------------------------------------------
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@pricetracker.dev")

# ------------------------------------------------------------
# Frontend URL
# ------------------------------------------------------------
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")