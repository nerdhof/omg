"""Core model management functionality."""

import logging
import os
from .models.ace_step import ACEStepModel

logger = logging.getLogger(__name__)

# Global model instance
_model_instance = None


def get_model() -> ACEStepModel:
    """Get or create the model instance."""
    global _model_instance
    
    if _model_instance is None:
        model_path = os.getenv("ACE_STEP_MODEL_PATH", None)
        device = os.getenv("DEVICE", "cpu")
        
        logger.info(f"Initializing ACE-Step model (device: {device})")
        _model_instance = ACEStepModel(model_path=model_path, device=device)
    
    return _model_instance

