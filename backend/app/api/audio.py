"""Audio file serving endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

from ..services.job_manager import job_manager

router = APIRouter()


@router.get("/versions/{version_id}/audio")
async def get_audio_file(version_id: str):
    """
    Download the audio file for a specific version.
    
    Note: This is a simplified implementation. In production, you'd want to:
    - Store audio paths in a database
    - Implement proper file storage (S3, etc.)
    - Add authentication/authorization
    - Handle file streaming for large files
    """
    # Search through all jobs to find the version
    audio_path = None
    for job_id, job in job_manager.jobs.items():
        path = job_manager.get_version_audio_path(job_id, version_id)
        if path:
            audio_path = path
            break
    
    if not audio_path:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version_id} not found"
        )
    
    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=404,
            detail=f"Audio file for version {version_id} not found on disk"
        )
    
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=f"{version_id}.wav"
    )

