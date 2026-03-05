import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.db.models  # noqa: F401  — ensure models registered with Base
from app.core.config import CORS_ORIGINS
from app.db.init_db import seed_admin
from app.routes.auth_routes import router as auth_router
from app.routes.product_routes import router as product_router
from app.routes.price_routes import router as price_router
from app.routes.track_routes import router as track_router
from app.routes.admin_routes import router as admin_router
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(application: FastAPI):
    import threading
    # Run seed in background so the health check (/) responds immediately
    threading.Thread(target=seed_admin, daemon=True).start()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Real-Time Price Tracker",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(price_router)
app.include_router(track_router)
app.include_router(admin_router)


@app.get("/")
def health():
    return {"status": "ok"}


CURRENCY_LIST = [
    {"code": "USD", "symbol": "$", "name": "US Dollar"},
    {"code": "EUR", "symbol": "\u20ac", "name": "Euro"},
    {"code": "GBP", "symbol": "\u00a3", "name": "British Pound"},
    {"code": "CAD", "symbol": "C$", "name": "Canadian Dollar"},
    {"code": "AUD", "symbol": "A$", "name": "Australian Dollar"},
    {"code": "JPY", "symbol": "\u00a5", "name": "Japanese Yen"},
    {"code": "CNY", "symbol": "\u00a5", "name": "Chinese Yuan"},
    {"code": "INR", "symbol": "\u20b9", "name": "Indian Rupee"},
    {"code": "IQD", "symbol": "\u0639.\u062f", "name": "Iraqi Dinar"},
    {"code": "SEK", "symbol": "kr", "name": "Swedish Krona"},
    {"code": "NOK", "symbol": "kr", "name": "Norwegian Krone"},
    {"code": "DKK", "symbol": "kr", "name": "Danish Krone"},
    {"code": "CHF", "symbol": "CHF", "name": "Swiss Franc"},
    {"code": "BRL", "symbol": "R$", "name": "Brazilian Real"},
    {"code": "MXN", "symbol": "$", "name": "Mexican Peso"},
    {"code": "KRW", "symbol": "\u20a9", "name": "South Korean Won"},
]


@app.get("/currencies")
def list_currencies():
    return CURRENCY_LIST

