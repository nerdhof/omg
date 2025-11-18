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
    num_versions: int = Field(1, ge=1, le=5, description="Number of versions to generate")
    seed: Optional[int] = Field(None, description="Optional seed for reproducible generation")


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
    queue_position: Optional[int] = Field(None, description="Position in the queue (1-based), if in queue")


class GenerationSubmitResponse(BaseModel):
    """Response when submitting a generation request."""
    job_id: str
    status: str
    queue_position: Optional[int] = Field(None, description="Position in the queue (1-based)")


class QueueItemResponse(BaseModel):
    """Response model for a queue item."""
    job_id: str
    status: JobStatus
    queue_position: int = Field(..., description="Position in the queue (1-based)")
    progress: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    prompt: str
    duration: float
    num_versions: int
    lyrics: Optional[str] = None
    seed: Optional[int] = None
    versions: Optional[List[VersionInfo]] = None
    error: Optional[str] = None
    created_at: str


class QueueListResponse(BaseModel):
    """Response model for queue list."""
    items: List[QueueItemResponse]
    total: int


class ReorderQueueRequest(BaseModel):
    """Request model for reordering queue."""
    job_id: str = Field(..., description="Job ID to move")
    new_position: int = Field(..., ge=1, description="New position in queue (1-based)")


class PresetInfo(BaseModel):
    """Preset information from a queue item."""
    prompt: str
    duration: float
    num_versions: int
    lyrics: Optional[str] = None
    seed: Optional[int] = None


class LyricsGenerationRequest(BaseModel):
    """Request model for lyrics generation/refinement."""
    current_lyrics: Optional[str] = Field(None, description="Existing lyrics for refinement")
    prompt: str = Field(..., description="Song prompt describing the music")
    duration: float = Field(..., gt=0, le=300, description="Target duration in seconds")
    topic: str = Field(..., description="Topic for the lyrics")


class LyricsGenerationResponse(BaseModel):
    """Response model for lyrics generation."""
    lyrics: str = Field(..., description="Generated or refined lyrics")

