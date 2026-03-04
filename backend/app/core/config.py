import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# ------------------------------------------------------------
# Environment mode
# ------------------------------------------------------------
ENV = os.getenv("ENV", "local").lower()  # local | prod
IS_PROD = ENV == "prod" or os.getenv("RENDER") is not None

# Load .env only locally, and never override real env vars
if not IS_PROD:
    load_dotenv(override=False)

# ------------------------------------------------------------
# DATABASE_URL
# ------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# In production, DATABASE_URL must exist (never fall back to localhost)
if IS_PROD and not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required in production (Render). Set it in Render env vars / blueprint."
    )

# Local fallback: build from DB_* variables (for laptop/dev)
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "real_time_price")

    if not DB_PASS:
        raise RuntimeError("DB_PASS is not set for local development.")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# Normalize scheme for SQLAlchemy + psycopg2 driver
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Optional debug (set DEBUG_CONFIG=1 on Render temporarily)
if os.getenv("DEBUG_CONFIG") == "1":
    print("ENV =", ENV)
    print("IS_PROD =", IS_PROD)
    print("DATABASE_URL startswith =", DATABASE_URL.split("://", 1)[0])

# ------------------------------------------------------------
# Auth / Security
# ------------------------------------------------------------
SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_LATER")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ------------------------------------------------------------
# CORS
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