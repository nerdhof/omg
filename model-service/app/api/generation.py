"""Generation API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from ..models.ace_step import ACEStepModel
from ..core import get_model

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerationRequest(BaseModel):
    """Request model for music generation."""
    prompt: str = Field(..., description="Text prompt describing the music to generate")
    duration: float = Field(..., gt=0, le=300, description="Target duration in seconds (max 300)")
    lyrics: Optional[str] = Field(None, description="Optional lyrics for the music (default: '[inst]' for instrumental)")
    num_versions: int = Field(1, ge=1, le=5, description="Number of versions to generate (1-5)")
    format: str = Field("wav", description="Output format ('wav' or 'mp3')")
    manual_seeds: Optional[int] = Field(None, description="Optional seed for reproducibility")


class VersionResponse(BaseModel):
    """Response model for a single generated version."""
    id: str
    audio_path: str
    metadata: Dict[str, Any]


class GenerationResponse(BaseModel):
    """Response model for generation request."""
    versions: List[VersionResponse]


@router.post("/generate", response_model=GenerationResponse)
async def generate_music(request: GenerationRequest):
    """
    Generate music based on the provided prompt.
    
    Args:
        request: Generation request with prompt, duration, and num_versions
        
    Returns:
        List of generated audio versions
    """
    try:
        model = get_model()
        
        if not model.is_available():
            raise HTTPException(
                status_code=503,
                detail="Model is not available. Please check model service configuration."
            )
        
        logger.info(
            f"Generating {request.num_versions} version(s) with prompt: {request.prompt[:50]}... "
            f"lyrics: {request.lyrics[:50] if request.lyrics else '[inst]'}..."
        )
        
        results = model.generate(
            prompt=request.prompt,
            duration=request.duration,
            lyrics=request.lyrics,
            num_versions=request.num_versions,
            format=request.format,
            manual_seeds=request.manual_seeds
        )
        
        return GenerationResponse(
            versions=[
                VersionResponse(
                    id=r["id"],
                    audio_path=r["audio_path"],
                    metadata=r["metadata"]
                )
                for r in results
            ]
        )
    
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

