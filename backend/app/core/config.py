import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------
ENV = os.getenv("ENV", "local").lower()
IS_PROD = ENV == "prod" or os.getenv("RENDER") is not None

# Only load .env locally
if not IS_PROD:
    load_dotenv(override=False)

# ------------------------------------------------------------
# DATABASE_URL (Render-safe + Docker-safe)
# ------------------------------------------------------------
# If DATABASE_URL is provided (Docker/Render/etc.), always use it.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "real_time_price")

    if not DB_PASS:
        raise RuntimeError("DB_PASS is not set for local development.")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if IS_PROD:
    if "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL:
        raise RuntimeError(f"Invalid DATABASE_URL in production (points to localhost): {DATABASE_URL}")

# Normalize scheme for SQLAlchemy + psycopg2
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Validated ✓

# ------------------------------------------------------------
# Security / Auth
# ------------------------------------------------------------
SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_LATER")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ------------------------------------------------------------
# CORS  ✅ (this fixes your ImportError)
# ------------------------------------------------------------
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

# ------------------------------------------------------------
# Frontend URL
# ------------------------------------------------------------
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

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
