"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationRequest(BaseModel):
    """Request model for music generation."""
    prompt: str = Field(..., description="Text prompt describing the music to generate")
    duration: float = Field(..., gt=0, le=300, description="Target duration in seconds")
    lyrics: Optional[str] = Field(None, description="Optional lyrics for the music")
    num_versions: int = Field(3, ge=1, le=5, description="Number of versions to generate")


class VersionInfo(BaseModel):
    """Information about a generated version."""
    id: str
    metadata: Dict[str, Any]


class JobResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: JobStatus
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    versions: Optional[List[VersionInfo]] = None
    error: Optional[str] = None


class GenerationSubmitResponse(BaseModel):
    """Response when submitting a generation request."""
    job_id: str
    status: str

