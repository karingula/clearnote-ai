from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.recordings import router as recordings_router

app = FastAPI(
    title="ClearNote AI API",
    description=(
        "API for transforming recorded conversations into "
        "reviewable transcripts and structured notes."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recordings_router)

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Return the current health of the API."""

    return {
        "status": "healthy",
        "service": "clearnote-api",
        "version": "0.2.0",
    }