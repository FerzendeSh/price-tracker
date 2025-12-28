from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes.auth_routes import router as auth_router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # startup
    yield       # app runs



app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
