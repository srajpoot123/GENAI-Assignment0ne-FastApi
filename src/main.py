from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import settings
from src.joke.router import router as joke_router
from src.logging_config import configure_logging
from src.summary.router import router as summary_router
from src.weather.router import router as weather_router

logger = configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("FastAPI microservice starting up")
    logger.info("App API key configured: %s", bool(settings.app_api_key))
    logger.info("Weather API key configured: %s",
                bool(settings.openweather_api_key))
    try:
        yield
    finally:
        logger.info("FastAPI microservice shutting down")


app = FastAPI(
    title="FastAPI Microservice",
    version="1.0.0",
    description="Weather, jokes, and authenticated LLM summary endpoints.",
    lifespan=lifespan,
)

app.include_router(weather_router)
app.include_router(joke_router)
app.include_router(summary_router)


@app.get("/")
def root() -> dict:
    return {
        "message": "FastAPI Assignment API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception for %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
