"""Model service main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .api import generation
from .core import get_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Music Generation Model Service",
    description="Microservice for running music generation models (ACE-Step)",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    try:
        # Initialize music generation model based on MUSIC_PROVIDER env var
        import os
        default_provider = os.getenv("MUSIC_PROVIDER", "ace-step").lower()
        model = get_model()
        if model.is_available():
            logger.info(f"{default_provider} model ready")
        else:
            logger.warning(f"{default_provider} model started but model is not available")
    except Exception as e:
        logger.error(f"Failed to initialize music generation model: {e}")
    
    # Note: Mistral model is no longer initialized on startup.
    # It runs in a subprocess per request to ensure proper cleanup.
    logger.info("Mistral lyrics model will be loaded in subprocess per request")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from .core import get_current_provider
    model = get_model()
    current_provider = get_current_provider()
    return {
        "status": "healthy" if model.is_available() else "degraded",
        "current_provider": current_provider,
        "model_info": model.get_model_info()
    }


# Include routers
app.include_router(generation.router, prefix="/model/v1", tags=["generation"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MODEL_SERVICE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

