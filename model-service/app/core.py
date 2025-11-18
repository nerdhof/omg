"""Core model management functionality."""

import logging
import os
from .models.ace_step import ACEStepModel
from .models.mistral_lyrics import MistralLyricsModel

logger = logging.getLogger(__name__)

# Global model instances
_model_instance = None
_mistral_instance = None


def get_model() -> ACEStepModel:
    """Get or create the ACE-Step model instance."""
    global _model_instance
    
    if _model_instance is None:
        model_path = os.getenv("ACE_STEP_MODEL_PATH", None)
        device = os.getenv("DEVICE", "cpu")
        
        logger.info(f"Initializing ACE-Step model (device: {device})")
        _model_instance = ACEStepModel(model_path=model_path, device=device)
    
    return _model_instance


def get_mistral_model() -> MistralLyricsModel:
    """Get or create the Mistral lyrics model instance."""
    global _mistral_instance
    
    if _mistral_instance is None:
        model_name = os.getenv("MISTRAL_MODEL_NAME", None)
        device = os.getenv("DEVICE", "cpu")
        
        logger.info(f"Initializing Mistral lyrics model (device: {device})")
        _mistral_instance = MistralLyricsModel(model_name=model_name, device=device)
    
    return _mistral_instance

