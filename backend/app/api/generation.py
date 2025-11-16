"""Generation API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from ..models.schemas import (
    GenerationRequest,
    GenerationSubmitResponse,
    JobResponse,
    JobStatus
)
from ..services.job_manager import job_manager

router = APIRouter()


@router.post("/generate", response_model=GenerationSubmitResponse)
async def submit_generation(request: GenerationRequest):
    """
    Submit a music generation request.
    
    Returns a job ID that can be used to check status.
    """
    try:
        job_id = job_manager.create_job(
            prompt=request.prompt,
            duration=request.duration,
            lyrics=request.lyrics,
            num_versions=request.num_versions
        )
        
        return GenerationSubmitResponse(
            job_id=job_id,
            status="pending"
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
    
    # Calculate progress (simplified - in production, track actual progress)
    progress = None
    if job["status"] == JobStatus.PROCESSING:
        progress = 50.0  # Placeholder
    elif job["status"] == JobStatus.COMPLETED:
        progress = 100.0
    
    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=progress,
        versions=job.get("versions"),
        error=job.get("error")
    )

