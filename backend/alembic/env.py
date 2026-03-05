from logging.config import fileConfig
import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# ------------------------------------------------------------
# Alembic config
# ------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure project root is importable
sys.path.append(str(Path(__file__).resolve().parents[1]))

# ------------------------------------------------------------
# Load .env only locally (never on Render)
# Render sets RENDER=1, but we also support ENV=prod.
# ------------------------------------------------------------
ENV = os.getenv("ENV", "local").lower()
IS_PROD = ENV == "prod" or os.getenv("RENDER") is not None

if not IS_PROD:
    # Load .env from project root for local development only
    load_dotenv(str(Path(__file__).resolve().parents[1] / ".env"), override=False)

# ------------------------------------------------------------
# Import models / metadata
# ------------------------------------------------------------
import app.models  # noqa: F401  (ensures all tables are registered)
from app.db.base import Base

target_metadata = Base.metadata

# ------------------------------------------------------------
# Determine DB URL
# Production: use DATABASE_URL from Render
# Local: build from DB_* vars
# ------------------------------------------------------------
db_url = os.getenv("DATABASE_URL")

if IS_PROD:
    if not db_url:
        raise RuntimeError("DATABASE_URL is required in production (Render) for Alembic migrations.")
else:
    if not db_url:
        _user = os.getenv("DB_USER", "postgres")
        _pw = os.getenv("DB_PASS", "")
        _host = os.getenv("DB_HOST", "localhost")
        _port = os.getenv("DB_PORT", "5432")
        _name = os.getenv("DB_NAME", "real_time_price")

        if not _pw:
            raise RuntimeError("DB_PASS is not set for local development (Alembic).")

        db_url = f"postgresql+psycopg2://{_user}:{quote_plus(_pw)}@{_host}:{_port}/{_name}"

# Normalize scheme for psycopg2
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Tell Alembic to use this URL
# escape % for configparser
config.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))

# Validated ✓


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    url = config.get_main_option("sqlalchemy.url")

    connectable = create_engine(url, poolclass=pool.NullPool, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()