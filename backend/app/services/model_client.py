"""Client for communicating with the model service."""

import httpx
import logging
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
        self.timeout = 300.0  # 5 minutes timeout for generation
    
    async def generate(
        self,
        prompt: str,
        duration: float,
        num_versions: int = 1,
        lyrics: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Request music generation from the model service.
        
        Args:
            prompt: Text prompt for generation
            duration: Target duration in seconds
            num_versions: Number of versions to generate
            lyrics: Optional lyrics for the music
            
        Returns:
            List of generated versions with audio paths
        """
        url = f"{self.base_url}/model/v1/generate"
        
        payload = {
            "prompt": prompt,
            "duration": duration,
            "num_versions": num_versions
        }
        
        if lyrics is not None:
            payload["lyrics"] = lyrics
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Requesting generation from {url}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("versions", [])
        
        except httpx.TimeoutException:
            logger.error("Model service request timed out")
            raise Exception("Generation request timed out. Please try again.")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Model service error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Model service error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Failed to communicate with model service: {e}")
            raise Exception(f"Failed to communicate with model service: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if the model service is healthy."""
        try:
            url = f"{self.base_url}/health"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

