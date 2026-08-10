from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.recordings import router as recordings_router
from app.api.routes.transcriptions import (
    router as transcriptions_router,
)
from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create local development tables during application startup."""

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description=(
        "API for transforming recorded conversations into "
        "reviewable transcripts and structured notes."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recordings_router)
app.include_router(transcriptions_router)
app.include_router(recordings_router)
app.include_router(transcriptions_router)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Return the current health of the API."""

    return {
        "status": "healthy",
        "service": "clearnote-api",
        "version": settings.app_version,
    }