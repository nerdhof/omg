"""Base model interface for music generation models."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path


class BaseMusicModel(ABC):
    """Abstract base class for music generation models."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        duration: float,
        num_versions: int = 1,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate music based on the given prompt.
        
        Args:
            prompt: Text description of the music to generate
            duration: Target duration in seconds
            num_versions: Number of versions to generate
            
        Returns:
            List of dictionaries containing:
            - id: Unique identifier for the version
            - audio_path: Path to the generated audio file
            - metadata: Additional metadata about the generation
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and ready to use."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        pass

