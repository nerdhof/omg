"""Background generation job management service."""

import uuid
import multiprocessing
import threading
from typing import Dict, Optional, Callable
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Generation job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationJob:
    """Represents a background generation job."""
    
    def __init__(
        self,
        job_id: str,
        prompt: str,
        duration: float,
        lyrics: Optional[str] = None,
        num_versions: int = 1,
        format: str = "mp3",
        manual_seeds: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize a generation job.
        
        Args:
            job_id: Unique job identifier
            prompt: Text prompt for generation
            duration: Target duration in seconds
            lyrics: Optional lyrics
            num_versions: Number of versions to generate
            format: Output format
            manual_seeds: Optional seed
            **kwargs: Additional generation parameters
        """
        self.job_id = job_id
        self.prompt = prompt
        self.duration = duration
        self.lyrics = lyrics
        self.num_versions = num_versions
        self.format = format
        self.manual_seeds = manual_seeds
        self.kwargs = kwargs
        
        self.created_at = datetime.now()
        self.completed_at = None
        
        # Multiprocessing primitives - use Manager for shared state
        self.manager = multiprocessing.Manager()
        self.shared_state = self.manager.dict({
            "status": JobStatus.PENDING.value,
            "progress": 0.0,
            "current_step": "",
            "results": None,
            "error": None,
            "completed_at": None
        })
        self.cancellation_event = multiprocessing.Event()
        self.progress_queue = multiprocessing.Queue()
        self.process: Optional[multiprocessing.Process] = None
        self.lock = multiprocessing.Lock()
    
    @property
    def status(self) -> JobStatus:
        """Get job status from shared state."""
        return JobStatus(self.shared_state["status"])
    
    @property
    def progress(self) -> float:
        """Get job progress from shared state."""
        return self.shared_state["progress"]
    
    @property
    def current_step(self) -> str:
        """Get current step from shared state."""
        return self.shared_state["current_step"]
    
    @property
    def results(self):
        """Get results from shared state."""
        return self.shared_state["results"]
    
    @property
    def error(self) -> Optional[str]:
        """Get error from shared state."""
        return self.shared_state["error"]
    
    def cancel(self):
        """Cancel the generation job."""
        with self.lock:
            current_status = JobStatus(self.shared_state["status"])
            if current_status in (JobStatus.PENDING, JobStatus.PROCESSING):
                self.cancellation_event.set()
                self.shared_state["status"] = JobStatus.CANCELLED.value
                logger.info(f"Job {self.job_id} cancelled")
                # Terminate process if it's running
                if self.process and self.process.is_alive():
                    self.process.terminate()
                    self.process.join(timeout=5.0)
                    if self.process.is_alive():
                        self.process.kill()
                return True
        return False
    
    def cleanup(self):
        """Clean up multiprocessing resources to prevent file descriptor leaks."""
        try:
            # Close the progress queue
            if hasattr(self, 'progress_queue'):
                try:
                    self.progress_queue.close()
                    self.progress_queue.join_thread()
                except Exception as e:
                    logger.warning(f"Error closing progress queue for job {self.job_id}: {e}")
            
            # Shutdown the manager to close pipes
            if hasattr(self, 'manager'):
                try:
                    self.manager.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down manager for job {self.job_id}: {e}")
            
            # Ensure process is terminated
            if self.process and self.process.is_alive():
                self.process.terminate()
                self.process.join(timeout=2.0)
                if self.process.is_alive():
                    self.process.kill()
            
            logger.debug(f"Cleaned up resources for job {self.job_id}")
        except Exception as e:
            logger.error(f"Error during cleanup of job {self.job_id}: {e}")
    
    def is_cancelled(self) -> bool:
        """Check if the job has been cancelled."""
        return self.cancellation_event.is_set()
    
    def update_progress(self, progress: float, step: str = ""):
        """
        Update job progress in shared state.
        
        Args:
            progress: Progress percentage (0-100)
            step: Current step description
        """
        with self.lock:
            self.shared_state["progress"] = max(0.0, min(100.0, progress))
            if step:
                self.shared_state["current_step"] = step
    
    def set_status(self, status: JobStatus):
        """Set job status in shared state."""
        with self.lock:
            self.shared_state["status"] = status.value
            if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                self.shared_state["completed_at"] = datetime.now().isoformat()
                self.completed_at = datetime.now()
    
    def _poll_progress_queue(self):
        """Poll progress queue and update shared state. Should be called periodically."""
        try:
            while not self.progress_queue.empty():
                update = self.progress_queue.get_nowait()
                if isinstance(update, dict):
                    if "progress" in update:
                        self.shared_state["progress"] = max(0.0, min(100.0, update["progress"]))
                    if "step" in update:
                        self.shared_state["current_step"] = update["step"]
                    if "status" in update:
                        self.shared_state["status"] = update["status"]
                    if "results" in update:
                        self.shared_state["results"] = update["results"]
                    if "error" in update:
                        self.shared_state["error"] = update["error"]
        except Exception as e:
            logger.warning(f"Error polling progress queue for job {self.job_id}: {e}")
    
    def to_dict(self) -> Dict:
        """Convert job to dictionary for API responses."""
        # Poll progress queue before returning
        self._poll_progress_queue()
        
        with self.lock:
            return {
                "job_id": self.job_id,
                "status": self.shared_state["status"],
                "progress": self.shared_state["progress"],
                "current_step": self.shared_state["current_step"],
                "prompt": self.prompt,
                "duration": self.duration,
                "lyrics": self.lyrics,
                "num_versions": self.num_versions,
                "format": self.format,
                "manual_seeds": self.manual_seeds,
                "results": self.shared_state["results"],
                "error": self.shared_state["error"],
                "created_at": self.created_at.isoformat(),
                "completed_at": self.shared_state.get("completed_at"),
            }


class GenerationJobManager:
    """Manages background generation jobs."""
    
    def __init__(self):
        """Initialize the job manager."""
        self.jobs: Dict[str, GenerationJob] = {}
        self.lock = threading.Lock()  # Use threading.Lock since we're in the main process
    
    def create_job(
        self,
        prompt: str,
        duration: float,
        lyrics: Optional[str] = None,
        num_versions: int = 1,
        format: str = "mp3",
        manual_seeds: Optional[int] = None,
        job_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a new generation job.
        
        Args:
            prompt: Text prompt for generation
            duration: Target duration in seconds
            lyrics: Optional lyrics
            num_versions: Number of versions to generate
            format: Output format
            manual_seeds: Optional seed
            job_id: Optional job ID (generated if not provided)
            **kwargs: Additional generation parameters
            
        Returns:
            Job ID
        """
        # Periodically clean up old jobs to prevent resource leaks
        # Clean up jobs older than 1 hour
        try:
            self.cleanup_old_jobs(max_age_seconds=3600)
        except Exception as e:
            logger.warning(f"Error during automatic cleanup: {e}")
        
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        job = GenerationJob(
            job_id=job_id,
            prompt=prompt,
            duration=duration,
            lyrics=lyrics,
            num_versions=num_versions,
            format=format,
            manual_seeds=manual_seeds,
            **kwargs
        )
        
        with self.lock:
            self.jobs[job_id] = job
        
        logger.info(f"Created generation job {job_id}")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Get a job by ID."""
        with self.lock:
            return self.jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if job was cancelled, False if not found or already completed
        """
        job = self.get_job(job_id)
        if job:
            return job.cancel()
        return False
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from memory.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                # Clean up resources before deleting
                job.cleanup()
                del self.jobs[job_id]
                logger.info(f"Deleted job {job_id}")
                return True
        return False
    
    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """
        Clean up completed jobs older than max_age_seconds.
        
        Args:
            max_age_seconds: Maximum age in seconds for completed jobs (default: 1 hour)
            
        Returns:
            Number of jobs cleaned up
        """
        cleaned_count = 0
        now = datetime.now()
        
        with self.lock:
            jobs_to_delete = []
            for job_id, job in list(self.jobs.items()):
                # Only clean up completed, failed, or cancelled jobs
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    if job.completed_at:
                        age_seconds = (now - job.completed_at).total_seconds()
                        if age_seconds > max_age_seconds:
                            jobs_to_delete.append(job_id)
            
            # Delete outside the iteration
            for job_id in jobs_to_delete:
                job = self.jobs[job_id]
                job.cleanup()
                del self.jobs[job_id]
                cleaned_count += 1
                logger.info(f"Cleaned up old job {job_id}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old job(s)")
        
        return cleaned_count


# Global job manager instance
job_manager = GenerationJobManager()

