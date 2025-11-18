"""Job management for generation requests."""

import uuid
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import logging

from ..models.schemas import JobStatus, VersionInfo
from .model_client import ModelServiceClient

logger = logging.getLogger(__name__)


class JobManager:
    """Manages generation jobs in a sequential queue."""
    
    def __init__(self):
        """Initialize the job manager."""
        self.jobs: Dict[str, Dict] = {}
        self.queue: List[str] = []  # Ordered list of job IDs
        self.currently_processing_job_id: Optional[str] = None
        self.model_client = ModelServiceClient()
        self._processing_lock = asyncio.Lock()
    
    def create_job(
        self,
        prompt: str,
        duration: float,
        num_versions: int,
        lyrics: Optional[str] = None,
        seed: Optional[int] = None,
        provider: Optional[str] = None
    ) -> str:
        """
        Create a new generation job and add it to the queue.
        
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
            "seed": seed,
            "provider": provider,
            "versions": None,
            "error": None,
            "created_at": datetime.now(),
            "task": None,
            "queue_position": 0,  # Will be set by _update_queue_positions
            "progress": 0.0,  # Progress percentage (0-100)
            "model_service_job_id": None,  # Job ID from model service
            "cancelled": False
        }
        
        self.jobs[job_id] = job
        self.queue.append(job_id)
        
        # Update queue positions
        self._update_queue_positions()
        
        # Start processing if no job is currently processing
        if self.currently_processing_job_id is None:
            asyncio.create_task(self._process_next_job())
        
        logger.info(f"Created job {job_id} with prompt: {prompt[:50]}... (queue position: {job['queue_position']})")
        
        return job_id
    
    def _update_queue_positions(self):
        """Update queue positions for all jobs in the queue."""
        for idx, job_id in enumerate(self.queue, start=1):
            if job_id in self.jobs:
                self.jobs[job_id]["queue_position"] = idx
    
    async def _process_next_job(self):
        """Process the next job in the queue."""
        async with self._processing_lock:
            # Check if there's already a job processing
            if self.currently_processing_job_id is not None:
                return
            
            # Find next pending job
            next_job_id = None
            for job_id in self.queue:
                job = self.jobs.get(job_id)
                if job and job["status"] == JobStatus.PENDING:
                    next_job_id = job_id
                    break
            
            if not next_job_id:
                return
            
            self.currently_processing_job_id = next_job_id
            task = asyncio.create_task(self._process_job(next_job_id))
            self.jobs[next_job_id]["task"] = task
    
    async def _process_job(self, job_id: str):
        """Process a generation job asynchronously."""
        job = self.jobs.get(job_id)
        if not job:
            self.currently_processing_job_id = None
            await self._process_next_job()
            return
        
        try:
            job["status"] = JobStatus.PROCESSING
            job["progress"] = 0.0
            logger.info(f"Processing job {job_id}")
            
            # Start generation job on model service
            model_job_id = await self.model_client.start_generation(
                prompt=job["prompt"],
                duration=job["duration"],
                lyrics=job.get("lyrics"),
                num_versions=job["num_versions"],
                seed=job.get("seed"),
                provider=job.get("provider"),
                job_id=job_id  # Use backend job_id as model-service job_id
            )
            
            job["model_service_job_id"] = model_job_id
            
            # Poll for progress and completion
            while True:
                # Check if job was cancelled
                if job.get("cancelled", False):
                    # Try to cancel on model service
                    try:
                        await self.model_client.cancel_generation(model_job_id)
                    except Exception as e:
                        logger.warning(f"Failed to cancel model-service job {model_job_id}: {e}")
                    job["status"] = JobStatus.FAILED
                    job["error"] = "Job was cancelled"
                    break
                
                # Poll for progress
                try:
                    progress_data = await self.model_client.get_generation_progress(model_job_id)
                    job["progress"] = progress_data.get("progress", 0.0)
                    
                    # Check status
                    status_data = await self.model_client.get_generation_status(model_job_id)
                    status = status_data.get("status")
                    
                    if status == "completed":
                        # Get results
                        versions_data = status_data.get("versions", [])
                        
                        # Store version info with audio paths
                        version_list = []
                        for v in versions_data:
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
                        job["version_paths"] = {v["id"]: v.get("audio_path") for v in versions_data}
                        
                        job["status"] = JobStatus.COMPLETED
                        job["progress"] = 100.0
                        logger.info(f"Job {job_id} completed with {len(version_list)} versions")
                        break
                    
                    elif status in ("failed", "cancelled"):
                        error = status_data.get("error", f"Generation {status}")
                        job["status"] = JobStatus.FAILED
                        job["error"] = error
                        logger.error(f"Job {job_id} {status}: {error}")
                        break
                    
                    # Continue polling if status is "pending" or "processing"
                    await asyncio.sleep(5.0)  # Poll every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Error polling progress for job {job_id}: {e}", exc_info=True)
                    # Continue polling on error (might be transient)
                    await asyncio.sleep(2.0)
        
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            job["status"] = JobStatus.FAILED
            job["error"] = str(e)
        finally:
            # Mark as no longer processing and start next job
            if self.currently_processing_job_id == job_id:
                self.currently_processing_job_id = None
            await self._process_next_job()
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job status."""
        return self.jobs.get(job_id)
    
    def get_queue(self) -> List[Dict]:
        """Get all queue items with their positions."""
        queue_items = []
        for job_id in self.queue:
            job = self.jobs.get(job_id)
            if job:
                queue_items.append(job)
        return queue_items
    
    def get_queue_item(self, job_id: str) -> Optional[Dict]:
        """Get a specific queue item with queue position info."""
        job = self.jobs.get(job_id)
        if job and job_id in self.queue:
            return job
        return None
    
    def remove_from_queue(self, job_id: str) -> bool:
        """
        Remove a job from the queue and cancel it if processing.
        
        Returns:
            True if removed, False if not found
        """
        if job_id not in self.queue:
            return False
        
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        # If currently processing, cancel the job
        if self.currently_processing_job_id == job_id:
            job["cancelled"] = True
            
            # Cancel model-service job if it exists
            model_job_id = job.get("model_service_job_id")
            if model_job_id:
                # Cancel asynchronously (don't wait)
                asyncio.create_task(self.model_client.cancel_generation(model_job_id))
            
            # Cancel the processing task
            task = job.get("task")
            if task and not task.done():
                task.cancel()
            
            self.currently_processing_job_id = None
            # Start next job
            asyncio.create_task(self._process_next_job())
        
        # Remove from queue
        self.queue.remove(job_id)
        self._update_queue_positions()
        
        logger.info(f"Removed job {job_id} from queue")
        return True
    
    def reorder_queue(self, job_id: str, new_position: int) -> bool:
        """
        Move a job to a new position in the queue.
        
        Args:
            job_id: Job ID to move
            new_position: New position (1-based)
            
        Returns:
            True if reordered, False if not found or invalid position
        """
        if job_id not in self.queue:
            return False
        
        if new_position < 1 or new_position > len(self.queue):
            return False
        
        # Don't allow reordering if currently processing
        if self.currently_processing_job_id == job_id:
            return False
        
        # Remove from current position
        self.queue.remove(job_id)
        
        # Insert at new position (convert to 0-based index)
        self.queue.insert(new_position - 1, job_id)
        
        # Update all queue positions
        self._update_queue_positions()
        
        logger.info(f"Reordered job {job_id} to position {new_position}")
        return True
    
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

