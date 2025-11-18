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
        # Initialize ACE-Step model
        model = get_model()
        if model.is_available():
            logger.info("ACE-Step model ready")
        else:
            logger.warning("ACE-Step model started but model is not available")
    except Exception as e:
        logger.error(f"Failed to initialize ACE-Step model: {e}")
    
    try:
        # Initialize Mistral lyrics model (lazy loading, so just check availability)
        from .core import get_mistral_model
        mistral_model = get_mistral_model()
        if mistral_model.is_available():
            logger.info("Mistral lyrics model ready")
        else:
            logger.warning("Mistral lyrics model not available (will be loaded on first use)")
    except Exception as e:
        logger.warning(f"Mistral lyrics model initialization check failed: {e} (will be loaded on first use)")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model = get_model()
    return {
        "status": "healthy" if model.is_available() else "degraded",
        "model_info": model.get_model_info()
    }


# Include routers
app.include_router(generation.router, prefix="/model/v1", tags=["generation"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MODEL_SERVICE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

