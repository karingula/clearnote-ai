from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ClearNote AI API",
    description=(
        "API for transforming recorded conversations into "
        "reviewable transcripts and structured notes."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Return the current health of the API."""

    return {
        "status": "healthy",
        "service": "clearnote-api",
        "version": "0.1.0",
    }