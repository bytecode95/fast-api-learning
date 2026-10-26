import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import app_router
from app.core.config import settings
from app.core.request_logging import RequestLoggingMiddleware
from app.database.session import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database schema is managed by Alembic, not create_all().
    yield
    await engine.dispose()


is_production = settings.app_env == "production"
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if is_production != "production" else None,
    redoc_url="/redoc" if is_production != "production" else None,
)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(app_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to FAST API"}


@app.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}
