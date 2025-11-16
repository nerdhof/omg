"""Backend API main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from .api import generation, audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Music Generation API",
    description="Backend API for music generation web application",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generation.router, prefix="/api/v1", tags=["generation"])
app.include_router(audio.router, prefix="/api/v1", tags=["audio"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Music Generation API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from .services.model_client import ModelServiceClient
    
    model_client = ModelServiceClient()
    model_healthy = await model_client.health_check()
    
    return {
        "status": "healthy" if model_healthy else "degraded",
        "model_service": "available" if model_healthy else "unavailable"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

