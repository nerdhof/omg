"""Core model management functionality."""

import logging
import os
import torch
from typing import Optional, Dict, Any
from .models.ace_step import ACEStepModel
from .models.song_generation import SongGenerationModel
from .models.base import BaseMusicModel

logger = logging.getLogger(__name__)

# Global model instances - only one music model loaded at a time
_model_instances: Dict[str, Optional[BaseMusicModel]] = {
    "ace-step": None,
    "song-generation": None
}
_current_provider: Optional[str] = None
# Note: Mistral model is no longer stored globally - it runs in subprocess per request


def _get_default_provider() -> str:
    """Get the default provider from environment variable."""
    return os.getenv("MUSIC_PROVIDER", "ace-step").lower()


def get_model(provider: Optional[str] = None) -> BaseMusicModel:
    """
    Get or create the music generation model instance for the specified provider.
    
    Args:
        provider: Provider name ("ace-step" or "song-generation"). 
                 If None, uses default from MUSIC_PROVIDER env var or "ace-step".
    
    Returns:
        Model instance for the specified provider
        
    Raises:
        ValueError: If provider is not supported
    """
    global _current_provider, _model_instances
    
    # Determine which provider to use
    if provider is None:
        provider = _get_default_provider()
    
    provider = provider.lower()
    
    # Validate provider
    if provider not in _model_instances:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: {list(_model_instances.keys())}"
        )
    
    # If switching providers, clean up the previous one
    if _current_provider is not None and _current_provider != provider:
        logger.info(f"Switching from {_current_provider} to {provider}")
        cleanup_model(_current_provider)
    
    # Get or create model instance
    if _model_instances[provider] is None:
        device = os.getenv("DEVICE", "cpu")
        
        if provider == "ace-step":
            model_path = os.getenv("ACE_STEP_MODEL_PATH", None)
            logger.info(f"Initializing ACE-Step model (device: {device})")
            _model_instances[provider] = ACEStepModel(model_path=model_path, device=device)
        elif provider == "song-generation":
            logger.info(f"Initializing SongGeneration model (device: {device})")
            _model_instances[provider] = SongGenerationModel(device=device)
    
    _current_provider = provider
    return _model_instances[provider]


def switch_provider(provider: str) -> BaseMusicModel:
    """
    Switch to a different provider, cleaning up the previous one.
    
    Args:
        provider: Provider name ("ace-step" or "song-generation")
        
    Returns:
        Model instance for the new provider
        
    Raises:
        ValueError: If provider is not supported
    """
    global _current_provider
    
    provider = provider.lower()
    
    if provider not in _model_instances:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: {list(_model_instances.keys())}"
        )
    
    # Clean up current provider if different
    if _current_provider is not None and _current_provider != provider:
        logger.info(f"Switching provider from {_current_provider} to {provider}")
        cleanup_model(_current_provider)
    
    # Get the new provider's model
    model = get_model(provider=provider)
    _current_provider = provider
    
    logger.info(f"Switched to provider: {provider}")
    return model


def cleanup_model(provider: str):
    """
    Clean up resources for a specific provider.
    
    Args:
        provider: Provider name ("ace-step" or "song-generation")
    """
    global _model_instances, _current_provider
    
    provider = provider.lower()
    
    if provider not in _model_instances:
        logger.warning(f"Attempted to cleanup unknown provider: {provider}")
        return
    
    model = _model_instances[provider]
    
    if model is not None:
        logger.info(f"Cleaning up {provider} model resources")
        
        # Call cleanup method if available
        if hasattr(model, "cleanup"):
            try:
                model.cleanup()
            except Exception as e:
                logger.warning(f"Error during model cleanup: {e}")
        
        # Delete model instance
        del model
        _model_instances[provider] = None
        
        # Clear GPU cache if CUDA is available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("Cleared CUDA cache")
        
        # Reset current provider if it was the one being cleaned
        if _current_provider == provider:
            _current_provider = None
        
        logger.info(f"Cleaned up {provider} model resources")


def get_current_provider() -> Optional[str]:
    """Get the current active provider."""
    return _current_provider


def get_provider_status() -> Dict[str, Any]:
    """
    Get status information for all providers.
    
    Returns:
        Dictionary with status for each provider
    """
    status = {}
    
    for provider_name in _model_instances.keys():
        model = _model_instances[provider_name]
        
        # Check availability - create a temporary instance if needed
        available = False
        if model is not None:
            try:
                available = model.is_available()
            except Exception:
                available = False
        else:
            # Try to check availability without initializing
            try:
                device = os.getenv("DEVICE", "cpu")
                if provider_name == "ace-step":
                    temp_model = ACEStepModel(device=device)
                    available = temp_model.is_available()
                elif provider_name == "song-generation":
                    temp_model = SongGenerationModel(device=device)
                    available = temp_model.is_available()
            except Exception:
                available = False
        
        status[provider_name] = {
            "available": available,
            "initialized": model is not None and (
                hasattr(model, "_initialized") and model._initialized
            ) if model is not None else False,
            "is_current": provider_name == _current_provider,
        }
        
        if model is not None:
            try:
                status[provider_name]["info"] = model.get_model_info()
            except Exception as e:
                logger.warning(f"Error getting model info for {provider_name}: {e}")
                status[provider_name]["info"] = None
    
    return status


# Note: get_mistral_model() has been removed.
# Mistral model now runs in a subprocess per request (see app/api/generation.py)
# This ensures proper cleanup after each request.

