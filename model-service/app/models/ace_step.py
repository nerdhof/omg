"""ACE-Step model implementation using the GitHub repository directly."""

import os
import uuid
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
import logging
import torch
import threading
import multiprocessing

from .base import BaseMusicModel

logger = logging.getLogger(__name__)


class CancelledError(Exception):
    """Exception raised when generation is cancelled."""
    pass


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
        progress_callback: Optional[Callable[[float, str], None]] = None,
        cancellation_event: Optional[Union[threading.Event, multiprocessing.Event]] = None,
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
            progress_callback: Optional callback function(progress: float, step: str) for progress updates
            cancellation_event: Optional threading.Event or multiprocessing.Event to check for cancellation
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated audio files with metadata
            
        Raises:
            RuntimeError: If generation fails
            CancelledError: If generation is cancelled
        """
        if not self.is_available():
            raise RuntimeError("ACE-Step model is not available")
        
        self._initialize_model()
        
        # Default lyrics if not provided
        if lyrics is None:
            lyrics = ""

        # Check for cancellation before starting
        if cancellation_event and cancellation_event.is_set():
            raise CancelledError("Generation was cancelled before starting")

        results = []
        infer_step = kwargs.get("infer_step", 60)
        
        for i in range(num_versions):
            # Check for cancellation before each version
            if cancellation_event and cancellation_event.is_set():
                raise CancelledError(f"Generation was cancelled during version {i+1}/{num_versions}")
            
            version_id = str(uuid.uuid4())
            output_path = self.output_dir / f"{version_id}.{format}"
            
            try:
                logger.info(
                    f"Generating version {i+1}/{num_versions} with prompt: {prompt[:50]}... "
                    f"and lyrics: {lyrics[:50] if lyrics else ''}..."
                )
                
                # Calculate base progress for completed versions
                base_progress = (i / num_versions) * 100
                
                # Update progress: starting version
                if progress_callback:
                    progress_callback(base_progress, f"Starting version {i+1}/{num_versions}")
                
                # Generate audio using ACEStepPipeline with progress tracking
                # We monkeypatch tqdm to intercept progress from the diffusion loops
                with torch.no_grad():
                    # Check cancellation before model call
                    if cancellation_event and cancellation_event.is_set():
                        raise CancelledError(f"Generation was cancelled during version {i+1}/{num_versions}")
                    
                    # Setup progress tracking by monkeypatching tqdm
                    import acestep.pipeline_ace_step as ace_pipeline_module
                    original_tqdm = ace_pipeline_module.tqdm
                    
                    # Track which phase we're in (diffusion vs decoding)
                    progress_state = {
                        'phase': 'diffusion',  # 'diffusion' or 'decoding'
                        'diffusion_steps': 0,
                        'diffusion_total': 0,
                    }
                    
                    class ProgressTqdm:
                        """Wrapper for tqdm that intercepts progress and calls our callback."""
                        
                        def __init__(self, iterable=None, total=None, desc=None, **kwargs):
                            self.iterable = iterable
                            self.total = total
                            self.desc = desc or ""
                            self.n = 0
                            
                            # Detect phase based on description or total
                            # Diffusion loops have larger totals (infer_steps), decoding is smaller (batch_size)
                            if self.total and self.total > 10:
                                progress_state['phase'] = 'diffusion'
                                progress_state['diffusion_total'] = self.total
                            else:
                                progress_state['phase'] = 'decoding'
                        
                        def __iter__(self):
                            """Iterate and update progress on each step."""
                            if self.iterable is None:
                                return iter([])
                            
                            for idx, item in enumerate(self.iterable):
                                self.n = idx + 1
                                
                                if progress_callback:
                                    if progress_state['phase'] == 'diffusion':
                                        # Diffusion takes 90% of version progress
                                        step_progress = (self.n / self.total * 90.0) if self.total else 0
                                        overall_progress = base_progress + (step_progress / num_versions)
                                        progress_callback(
                                            overall_progress,
                                            f"Version {i+1}/{num_versions}: Diffusion step {self.n}/{self.total}"
                                        )
                                        progress_state['diffusion_steps'] = self.n
                                    elif progress_state['phase'] == 'decoding':
                                        # Decoding takes the remaining 10% of version progress
                                        decode_progress = 90.0 + (self.n / self.total * 10.0) if self.total else 90.0
                                        overall_progress = base_progress + (decode_progress / num_versions)
                                        progress_callback(
                                            overall_progress,
                                            f"Version {i+1}/{num_versions}: Decoding {self.n}/{self.total}"
                                        )
                                
                                # Check for cancellation
                                if cancellation_event and cancellation_event.is_set():
                                    raise CancelledError(f"Generation cancelled at version {i+1}/{num_versions}")
                                
                                yield item
                        
                        def __call__(self, iterable=None, total=None, desc=None, **kwargs):
                            """Support being called as a function like tqdm(iterable)."""
                            return ProgressTqdm(iterable=iterable, total=total, desc=desc, **kwargs)
                        
                        def update(self, n=1):
                            """Support manual updates (for compatibility)."""
                            self.n += n
                        
                        def close(self):
                            """Support close() calls (for compatibility)."""
                            pass
                    
                    # Monkeypatch tqdm in the pipeline module
                    ace_pipeline_module.tqdm = ProgressTqdm
                    
                    try:
                        # Initial progress update
                        if progress_callback:
                            progress_callback(
                                base_progress,
                                f"Starting version {i+1}/{num_versions}..."
                            )
                        
                        self.model(
                        audio_duration=duration,
                        prompt=prompt,
                        lyrics=lyrics,
                        format=format,
                        save_path=str(output_path),
                        manual_seeds=manual_seeds,
                        # Parameters from Modal example
                        infer_step=infer_step,
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
                    
                    finally:
                        # Restore original tqdm
                        ace_pipeline_module.tqdm = original_tqdm
                    
                    # Update progress: version complete
                    if progress_callback:
                        version_progress = 100.0
                        progress_callback(
                            base_progress + (version_progress / num_versions),
                            f"Completed version {i+1}/{num_versions}"
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
                        "infer_step": infer_step,
                        "guidance_scale": kwargs.get("guidance_scale", 15),
                    }
                })
                
            except CancelledError:
                # Re-raise cancellation errors
                raise
            except Exception as e:
                logger.error(f"Failed to generate version {i+1}: {e}", exc_info=True)
                raise RuntimeError(f"Failed to generate version {i+1}: {e}")
        
        # Final progress update
        if progress_callback:
            progress_callback(100.0, "All versions completed")
        
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
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model is not None:
            logger.info("Cleaning up ACE-Step model resources")
            del self.model
            self.model = None
            
            # Clear GPU cache if CUDA is available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("Cleared CUDA cache")
            
            self._initialized = False
            logger.info("ACE-Step model resources cleaned up")