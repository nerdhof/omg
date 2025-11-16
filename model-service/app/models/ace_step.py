"""ACE-Step model implementation using the GitHub repository directly."""

import os
import uuid
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import torch

from .base import BaseMusicModel

logger = logging.getLogger(__name__)


class ACEStepModel(BaseMusicModel):
    """ACE-Step music generation model wrapper using ACEStepPipeline."""
    
    def __init__(self, model_path: str = None, device: str = "cpu"):
        """
        Initialize ACE-Step model.
        
        Args:
            model_path: Path to the model checkpoint (optional, uses default from ACEStepPipeline)
            device: Device to run on ('cpu', 'cuda', or 'mps' for Apple devices)
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        self._initialized = False
        self.output_dir = Path(tempfile.gettempdir()) / "ace_step_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate device
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            self.device = "cpu"
        elif device == "mps":
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                logger.info("Using MPS (Apple Silicon) device")
            else:
                logger.warning("MPS requested but not available, falling back to CPU")
                self.device = "cpu"
    
    def _initialize_model(self):
        """Initialize the ACE-Step model using ACEStepPipeline from GitHub repo."""
        if self._initialized:
            return
        
        try:
            from acestep.pipeline_ace_step import ACEStepPipeline
            
            logger.info("Loading ACE-Step model using ACEStepPipeline")
            
            # Determine dtype based on device
            if self.device == "cuda":
                dtype = "bfloat16" if torch.cuda.is_bf16_supported() else "float16"
            else:
                dtype = "float32"
            
            logger.info(f"Initializing ACEStepPipeline with dtype={dtype}, device={self.device}")
            
            # Initialize the pipeline (matching Modal example)
            self.model = ACEStepPipeline(
                dtype=dtype,
                cpu_offload=False,
                overlapped_decode=True
            )
            
            # Move to device if needed (ACEStepPipeline handles this internally, but we can verify)
            if hasattr(self.model, "to") and self.device != "cpu":
                try:
                    self.model = self.model.to(self.device)
                except Exception as e:
                    logger.warning(f"Could not move model to {self.device}: {e}")
            
            self._initialized = True
            logger.info(f"ACE-Step model initialized successfully on {self.device}")
            
        except ImportError as e:
            logger.error(f"Required dependencies not installed: {e}")
            raise RuntimeError(
                f"Failed to import ACEStepPipeline. Please ensure ACE-Step is installed from GitHub. Error: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ACE-Step model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize ACE-Step model: {e}")
    
    def generate(
        self,
        prompt: str,
        duration: float,
        lyrics: Optional[str] = None,
        num_versions: int = 1,
        format: str = "mp3",
        manual_seeds: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate music using ACE-Step.
        
        Args:
            prompt: Text description of the music
            duration: Target duration in seconds
            lyrics: Optional lyrics for the music
            num_versions: Number of versions to generate
            format: Output format ("wav" or "mp3")
            manual_seeds: Optional seed for reproducibility
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated audio files with metadata
        """
        if not self.is_available():
            raise RuntimeError("ACE-Step model is not available")
        
        self._initialize_model()
        
        # Default lyrics if not provided
        if lyrics is None:
            lyrics = ""

        results = []
        
        for i in range(num_versions):
            version_id = str(uuid.uuid4())
            output_path = self.output_dir / f"{version_id}.{format}"
            
            try:
                logger.info(
                    f"Generating version {i+1}/{num_versions} with prompt: {prompt[:50]}... "
                    f"and lyrics: {lyrics[:50] if lyrics else ''}..."
                )
                
                # Generate audio using ACEStepPipeline (matching Modal example parameters)
                with torch.no_grad():
                    self.model(
                        audio_duration=duration,
                        prompt=prompt,
                        lyrics=lyrics,
                        format=format,
                        save_path=str(output_path),
                        manual_seeds=manual_seeds,
                        # Parameters from Modal example
                        infer_step=kwargs.get("infer_step", 45),
                        guidance_scale=kwargs.get("guidance_scale", 15),
                        scheduler_type=kwargs.get("scheduler_type", "euler"),
                        cfg_type=kwargs.get("cfg_type", "apg"),
                        omega_scale=kwargs.get("omega_scale", 10),
                        guidance_interval=kwargs.get("guidance_interval", 0.5),
                        guidance_interval_decay=kwargs.get("guidance_interval_decay", 0),
                        min_guidance_scale=kwargs.get("min_guidance_scale", 3),
                        use_erg_tag=kwargs.get("use_erg_tag", True),
                        use_erg_lyric=kwargs.get("use_erg_lyric", True),
                        use_erg_diffusion=kwargs.get("use_erg_diffusion", True),
                    )
                
                logger.info(f"Generated audio saved to: {output_path}")
                
                results.append({
                    "id": version_id,
                    "audio_path": str(output_path),
                    "metadata": {
                        "prompt": prompt,
                        "lyrics": lyrics,
                        "duration": duration,
                        "model": "ace-step",
                        "version": i + 1,
                        "format": format,
                        "seed": manual_seeds,
                        "infer_step": kwargs.get("infer_step", 60),
                        "guidance_scale": kwargs.get("guidance_scale", 15),
                    }
                })
                
            except Exception as e:
                logger.error(f"Failed to generate version {i+1}: {e}", exc_info=True)
                raise RuntimeError(f"Failed to generate version {i+1}: {e}")
        
        return results
    
    def is_available(self) -> bool:
        """Check if ACE-Step model is available."""
        try:
            # Check if required dependencies are installed
            from acestep.pipeline_ace_step import ACEStepPipeline
            import torch
            
            # Check if device is available if CUDA is requested
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available")
                return False
            
            # Check if MPS is available if MPS is requested
            if self.device == "mps":
                if not hasattr(torch.backends, "mps") or not torch.backends.mps.is_available():
                    logger.warning("MPS requested but not available")
                    return False
            
            return True
        except ImportError as e:
            logger.error(f"Required dependencies not installed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the ACE-Step model."""
        info = {
            "name": "ACE-Step",
            "type": "music_generation",
            "device": self.device,
            "initialized": self._initialized,
            "source": "github.com/ace-step/ACE-Step",
        }
        
        if self.model_path:
            info["model_path"] = self.model_path
        
        if self._initialized and self.model is not None:
            try:
                info["model_type"] = str(type(self.model))
            except Exception:
                pass
        
        return info
