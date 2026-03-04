import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

ENV = os.getenv("ENV", "local").lower()
IS_PROD = ENV == "prod" or os.getenv("RENDER") is not None

# Only load .env locally
if not IS_PROD:
    load_dotenv(override=False)

DATABASE_URL = os.getenv("DATABASE_URL")

# PROD: must come from platform (Render)
if IS_PROD:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing in production. Set it on Render (price-tracker-api → Environment).")
    # Prevent silent localhost usage
    if "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL:
        raise RuntimeError(f"Invalid DATABASE_URL in production (points to localhost): {DATABASE_URL}")

else:
    # LOCAL: build from DB_* fallback
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "real_time_price")

    if not DB_PASS:
        raise RuntimeError("DB_PASS is not set for local development.")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Normalize scheme for psycopg2
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

print("✅ Using DATABASE_URL:", DATABASE_URL)  # TEMP: remove after it works