"""Job management for generation requests."""

import uuid
import asyncio
from typing import Dict, Optional
from datetime import datetime
import logging

from ..models.schemas import JobStatus, VersionInfo
from .model_client import ModelServiceClient

logger = logging.getLogger(__name__)


class JobManager:
    """Manages generation jobs."""
    
    def __init__(self):
        """Initialize the job manager."""
        self.jobs: Dict[str, Dict] = {}
        self.model_client = ModelServiceClient()
    
    def create_job(
        self,
        prompt: str,
        duration: float,
        num_versions: int,
        lyrics: Optional[str] = None
    ) -> str:
        """
        Create a new generation job.
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        job = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "prompt": prompt,
            "lyrics": lyrics,
            "duration": duration,
            "num_versions": num_versions,
            "versions": None,
            "error": None,
            "created_at": datetime.now(),
            "task": None
        }
        
        self.jobs[job_id] = job
        
        # Start async generation task
        task = asyncio.create_task(self._process_job(job_id))
        job["task"] = task
        
        logger.info(f"Created job {job_id} with prompt: {prompt[:50]}...")
        
        return job_id
    
    async def _process_job(self, job_id: str):
        """Process a generation job asynchronously."""
        job = self.jobs.get(job_id)
        if not job:
            return
        
        try:
            job["status"] = JobStatus.PROCESSING
            logger.info(f"Processing job {job_id}")
            
            # Request generation from model service
            versions = await self.model_client.generate(
                prompt=job["prompt"],
                duration=job["duration"],
                lyrics=job.get("lyrics"),
                num_versions=job["num_versions"]
            )
            
            # Store version info with audio paths
            version_list = []
            for v in versions:
                version_info = VersionInfo(
                    id=v["id"],
                    metadata={
                        **v.get("metadata", {}),
                        "audio_path": v.get("audio_path")  # Store audio path in metadata
                    }
                )
                version_list.append(version_info)
            
            job["versions"] = version_list
            # Also store a mapping for quick lookup
            job["version_paths"] = {v["id"]: v.get("audio_path") for v in versions}
            
            job["status"] = JobStatus.COMPLETED
            logger.info(f"Job {job_id} completed with {len(versions)} versions")
        
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            job["status"] = JobStatus.FAILED
            job["error"] = str(e)
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job status."""
        return self.jobs.get(job_id)
    
    def get_version_audio_path(self, job_id: str, version_id: str) -> Optional[str]:
        """
        Get the audio path for a specific version.
        """
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        # Try to get from version_paths mapping first
        if job.get("version_paths") and version_id in job["version_paths"]:
            return job["version_paths"][version_id]
        
        # Fallback: search through versions
        if job.get("versions"):
            for version in job["versions"]:
                if version.id == version_id:
                    return version.metadata.get("audio_path")
        
        return None


# Global job manager instance
job_manager = JobManager()

