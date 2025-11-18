"""Client for communicating with the model service."""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class ModelServiceClient:
    """Client for the model microservice."""
    
    def __init__(self, base_url: str = None):
        """
        Initialize the model service client.
        
        Args:
            base_url: Base URL of the model service (defaults to env var)
        """
        self.base_url = base_url or os.getenv(
            "MODEL_SERVICE_URL",
            "http://localhost:8001"
        )
        self.timeout = 14400.0  # 4 hours timeout for generation
    
    async def start_generation(
        self,
        prompt: str,
        duration: float,
        num_versions: int = 1,
        lyrics: Optional[str] = None,
        seed: Optional[int] = None,
        provider: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> str:
        """
        Start a background generation job on the model service.
        
        Args:
            prompt: Text prompt for generation
            duration: Target duration in seconds
            num_versions: Number of versions to generate
            lyrics: Optional lyrics for the music
            seed: Optional seed for reproducible generation
            job_id: Optional job ID (generated if not provided)
            
        Returns:
            Job ID
        """
        url = f"{self.base_url}/model/v1/generate"
        
        payload = {
            "prompt": prompt,
            "duration": duration,
            "num_versions": num_versions,
            "format": "mp3"  # Default format
        }
        
        if lyrics is not None:
            payload["lyrics"] = lyrics
        
        if seed is not None:
            payload["manual_seeds"] = seed
        
        if provider is not None:
            payload["provider"] = provider
        
        if job_id is not None:
            payload["job_id"] = job_id
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Starting generation job at {url}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("job_id")
        
        except httpx.TimeoutException:
            logger.error("Model service request timed out")
            raise Exception("Generation request timed out. Please try again.")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Model service error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Model service error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to communicate with model service: {e}")
            raise Exception(f"Failed to communicate with model service: {str(e)}")
    
    async def get_generation_progress(self, job_id: str) -> Dict[str, Any]:
        """
        Get the progress of a generation job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Progress information (progress, current_step, status)
        """
        url = f"{self.base_url}/model/v1/generate/{job_id}/progress"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"Job {job_id} not found")
            logger.error(f"Model service error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Model service error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to get generation progress: {e}")
            raise Exception(f"Failed to get generation progress: {str(e)}")
    
    async def get_generation_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status and results of a generation job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status with results if completed
        """
        url = f"{self.base_url}/model/v1/generate/{job_id}/status"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise Exception(f"Job {job_id} not found")
            logger.error(f"Model service error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Model service error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to get generation status: {e}")
            raise Exception(f"Failed to get generation status: {str(e)}")
    
    async def cancel_generation(self, job_id: str) -> bool:
        """
        Cancel a generation job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        url = f"{self.base_url}/model/v1/generate/{job_id}/cancel"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(url)
                response.raise_for_status()
                logger.info(f"Cancelled generation job {job_id}")
                return True
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Job {job_id} not found for cancellation")
                return False
            if e.response.status_code == 400:
                logger.warning(f"Job {job_id} cannot be cancelled: {e.response.text}")
                return False
            logger.error(f"Model service error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Model service error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to cancel generation: {e}")
            raise Exception(f"Failed to cancel generation: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        duration: float,
        num_versions: int = 1,
        lyrics: Optional[str] = None,
        seed: Optional[int] = None,
        provider: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Request music generation from the model service (legacy synchronous method).
        This method starts a job and waits for completion.
        
        Args:
            prompt: Text prompt for generation
            duration: Target duration in seconds
            num_versions: Number of versions to generate
            lyrics: Optional lyrics for the music
            seed: Optional seed for reproducible generation
            job_id: Optional job ID (generated if not provided)
            
        Returns:
            List of generated versions with audio paths
        """
        # Start the job
        model_job_id = await self.start_generation(
            prompt=prompt,
            duration=duration,
            num_versions=num_versions,
            lyrics=lyrics,
            seed=seed,
            provider=provider,
            job_id=job_id
        )
        
        # Poll for completion
        while True:
            await asyncio.sleep(1.0)  # Poll every second
            
            status_data = await self.get_generation_status(model_job_id)
            status = status_data.get("status")
            
            if status == "completed":
                versions = status_data.get("versions", [])
                return versions
            elif status in ("failed", "cancelled"):
                error = status_data.get("error", f"Generation {status}")
                raise Exception(error)
            # Continue polling if status is "pending" or "processing"
    
    async def health_check(self) -> bool:
        """Check if the model service is healthy."""
        try:
            url = f"{self.base_url}/health"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

