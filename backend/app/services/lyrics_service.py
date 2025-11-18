"""Service for generating and refining lyrics using the model-service."""

import httpx
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class LyricsService:
    """Service for generating and refining lyrics using the model-service."""
    
    def __init__(self, model_service_url: str = None):
        """
        Initialize the lyrics service.
        
        Args:
            model_service_url: Base URL for model service (defaults to env var or localhost:8001)
        """
        self.model_service_url = model_service_url or os.getenv(
            "MODEL_SERVICE_URL",
            "http://localhost:8001"
        )
        self.timeout = 120.0  # 2 minutes timeout for generation
    
    async def generate_lyrics(
        self,
        topic: str,
        song_prompt: str,
        duration: float,
        current_lyrics: Optional[str] = None
    ) -> str:
        """
        Generate or refine lyrics using the model-service.
        
        Args:
            topic: Topic for the lyrics
            song_prompt: Description of the song/music
            duration: Duration of the song in seconds
            current_lyrics: Existing lyrics if refining (None for new generation)
            
        Returns:
            Generated or refined lyrics
            
        Raises:
            Exception: If generation fails
        """
        url = f"{self.model_service_url}/model/v1/lyrics/generate"
        
        payload = {
            "topic": topic,
            "prompt": song_prompt,
            "duration": duration,
            "current_lyrics": current_lyrics
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Requesting lyrics generation from model-service at {url}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                lyrics = data.get("lyrics", "").strip()
                
                if not lyrics:
                    raise Exception("Received empty response from model-service")
                
                logger.info("Successfully generated lyrics")
                return lyrics
        
        except httpx.TimeoutException:
            logger.error("Model-service request timed out")
            raise Exception("Lyrics generation timed out. Please try again.")
        
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to model-service at {self.model_service_url}: {e}")
            raise Exception(
                f"Cannot connect to model-service at {self.model_service_url}. "
                f"Please ensure the model-service is running and Mistral model is available."
            )
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Model-service API error: {e.response.status_code} - {e.response.text}")
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e.response.text))
            except:
                error_detail = str(e.response.text)
            raise Exception(f"Failed to generate lyrics: {error_detail}")
        
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "connect" in error_msg.lower():
                logger.error(f"Connection error to model-service at {self.model_service_url}: {e}")
                raise Exception(
                    f"Cannot connect to model-service at {self.model_service_url}. "
                    f"Please ensure the model-service is running and Mistral model is available."
                )
            logger.error(f"Failed to generate lyrics: {e}")
            raise Exception(f"Failed to generate lyrics: {str(e)}")

