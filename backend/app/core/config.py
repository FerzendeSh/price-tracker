import os
from dotenv import load_dotenv

from urllib.parse import quote_plus

load_dotenv()

# Build DATABASE_URL with properly encoded password
_DB_USER = os.getenv("DB_USER", "postgres")
_DB_PASS = os.getenv("DB_PASS", "P0stgres!Dev_2026#")
_DB_HOST = os.getenv("DB_HOST", "localhost")
_DB_PORT = os.getenv("DB_PORT", "5432")
_DB_NAME = os.getenv("DB_NAME", "real_time_price")

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{_DB_USER}:{quote_plus(_DB_PASS)}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}",
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_LATER")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# CORS
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Daily price-check schedule (24-h clock)
PRICE_CHECK_HOUR: int = int(os.getenv("PRICE_CHECK_HOUR", "8"))
PRICE_CHECK_MINUTE: int = int(os.getenv("PRICE_CHECK_MINUTE", "0"))

# SMTP / Email notifications (optional)
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@pricetracker.dev")

# Frontend URL (for verification links)
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
