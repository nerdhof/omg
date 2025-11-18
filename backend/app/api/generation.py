"""Generation API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime

from ..models.schemas import (
    GenerationRequest,
    GenerationSubmitResponse,
    JobResponse,
    JobStatus,
    QueueItemResponse,
    QueueListResponse,
    ReorderQueueRequest,
    PresetInfo,
    LyricsGenerationRequest,
    LyricsGenerationResponse
)
from ..services.job_manager import job_manager
from ..services.lyrics_service import LyricsService

router = APIRouter()

# Initialize lyrics service
lyrics_service = LyricsService()


@router.post("/generate", response_model=GenerationSubmitResponse)
async def submit_generation(request: GenerationRequest):
    """
    Submit a music generation request to the queue.
    
    Returns a job ID and queue position.
    """
    try:
        job_id = job_manager.create_job(
            prompt=request.prompt,
            duration=request.duration,
            lyrics=request.lyrics,
            num_versions=request.num_versions,
            seed=request.seed
        )
        
        job = job_manager.get_job(job_id)
        queue_position = job.get("queue_position") if job else None
        
        return GenerationSubmitResponse(
            job_id=job_id,
            status="pending",
            queue_position=queue_position
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create generation job: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a generation job.
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Get progress from job
    progress = job.get("progress")
    
    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=progress,
        versions=job.get("versions"),
        error=job.get("error"),
        queue_position=job.get("queue_position")
    )


@router.get("/queue", response_model=QueueListResponse)
async def get_queue():
    """
    Get all items in the queue with their positions and statuses.
    """
    queue_items = job_manager.get_queue()
    
    items = []
    for job in queue_items:
        # Get progress from job
        progress = job.get("progress")
        
        items.append(QueueItemResponse(
            job_id=job["job_id"],
            status=job["status"],
            queue_position=job.get("queue_position", 0),
            progress=progress,
            prompt=job["prompt"],
            duration=job["duration"],
            num_versions=job["num_versions"],
            lyrics=job.get("lyrics"),
            seed=job.get("seed"),
            versions=job.get("versions"),
            error=job.get("error"),
            created_at=job["created_at"].isoformat() if isinstance(job["created_at"], datetime) else str(job["created_at"])
        ))
    
    return QueueListResponse(
        items=items,
        total=len(items)
    )


@router.get("/queue/{job_id}", response_model=QueueItemResponse)
async def get_queue_item(job_id: str):
    """
    Get details of a specific queue item.
    """
    job = job_manager.get_queue_item(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Queue item {job_id} not found"
        )
    
    # Calculate progress
    progress = None
    if job["status"] == JobStatus.PROCESSING:
        progress = 50.0  # Placeholder
    elif job["status"] == JobStatus.COMPLETED:
        progress = 100.0
    
    return QueueItemResponse(
        job_id=job["job_id"],
        status=job["status"],
        queue_position=job.get("queue_position", 0),
        progress=progress,
        prompt=job["prompt"],
        duration=job["duration"],
        num_versions=job["num_versions"],
        lyrics=job.get("lyrics"),
        seed=job.get("seed"),
        versions=job.get("versions"),
        error=job.get("error"),
        created_at=job["created_at"].isoformat() if isinstance(job["created_at"], datetime) else str(job["created_at"])
    )


@router.delete("/queue/{job_id}")
async def remove_from_queue(job_id: str):
    """
    Remove a job from the queue.
    """
    success = job_manager.remove_from_queue(job_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Queue item {job_id} not found"
        )
    
    return {"message": f"Job {job_id} removed from queue"}


@router.patch("/queue/reorder")
async def reorder_queue(request: ReorderQueueRequest):
    """
    Reorder items in the queue by moving a job to a new position.
    """
    success = job_manager.reorder_queue(request.job_id, request.new_position)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to reorder job {request.job_id}. Job may not exist, position may be invalid, or job may be currently processing."
        )
    
    return {"message": f"Job {request.job_id} moved to position {request.new_position}"}


@router.get("/queue/{job_id}/preset", response_model=PresetInfo)
async def get_queue_item_preset(job_id: str):
    """
    Get preset information from a queue item (for reusing parameters).
    """
    job = job_manager.get_queue_item(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Queue item {job_id} not found"
        )
    
    return PresetInfo(
        prompt=job["prompt"],
        duration=job["duration"],
        num_versions=job["num_versions"],
        lyrics=job.get("lyrics"),
        seed=job.get("seed")
    )


@router.post("/lyrics/generate", response_model=LyricsGenerationResponse)
async def generate_lyrics(request: LyricsGenerationRequest):
    """
    Generate or refine lyrics using Ollama/Mistral.
    
    Accepts song context (prompt, duration, topic) and optionally existing lyrics
    for refinement. Returns generated or refined lyrics.
    """
    try:
        lyrics = await lyrics_service.generate_lyrics(
            topic=request.topic,
            song_prompt=request.prompt,
            duration=request.duration,
            current_lyrics=request.current_lyrics
        )
        
        return LyricsGenerationResponse(lyrics=lyrics)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate lyrics: {str(e)}"
        )

