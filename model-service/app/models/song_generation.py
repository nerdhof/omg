"""
SongGeneration model implementation using Tencent's LeVo SongGeneration.

LeVo Song Generation requires:
1. The official repository: https://github.com/tencent-ailab/SongGeneration
2. Runtime files: lglg666/SongGeneration-Runtime from Hugging Face
3. Model checkpoints: lglg666/SongGeneration-base (or other variants)
4. Input format: JSONL files with idx, gt_lyric, descriptions fields

For setup instructions, see: https://github.com/tencent-ailab/SongGeneration
"""

import os
import uuid
import tempfile
import json
import subprocess
import shutil
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


class SongGenerationModel(BaseMusicModel):
    """Tencent SongGeneration music generation model wrapper."""
    
    def __init__(self, model_id: str = None, device: str = "cpu", songgeneration_repo_path: str = None):
        """
        Initialize SongGeneration model.
        
        Args:
            model_id: Hugging Face model ID or local checkpoint path
                     (defaults from SONG_GENERATION_MODEL_ID env var)
            device: Device to run on ('cpu', 'cuda', or 'mps' for Apple devices)
            songgeneration_repo_path: Path to cloned SongGeneration repository
                                     (defaults from SONG_GENERATION_REPO_PATH env var)
        """
        self.model_id = model_id or os.getenv(
            "SONG_GENERATION_MODEL_ID",
            "lglg666/SongGeneration-base"
        )
        self.device = device
        self.model = None
        self._initialized = False
        
        # Path to the SongGeneration repository
        self.repo_path = Path(songgeneration_repo_path or os.getenv(
            "SONG_GENERATION_REPO_PATH",
            ""
        ))
        
        # Path to model checkpoint (can be Hugging Face ID or local path)
        self.checkpoint_path = None
        
        # Path to runtime files (ckpt and third_party directories)
        self.runtime_path = None
        
        self.output_dir = Path(tempfile.gettempdir()) / "song_generation_output"
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
        """
        Initialize the LeVo SongGeneration model.
        
        This checks for the SongGeneration repository and sets up paths.
        The actual model loading happens when generate() is called via the shell script.
        """
        if self._initialized:
            return
        
        try:
            # Check if we have a local repository path
            if self.repo_path and self.repo_path.exists():
                logger.info(f"Using SongGeneration repository at: {self.repo_path}")
                # Check for required files
                generate_script = self.repo_path / "generate.sh"
                if not generate_script.exists():
                    raise RuntimeError(
                        f"SongGeneration repository found at {self.repo_path} but generate.sh not found.\n"
                        f"Please ensure you have cloned the official repository:\n"
                        f"  git clone https://github.com/tencent-ailab/SongGeneration.git"
                    )
                
                # Check for runtime files (ckpt and third_party directories)
                ckpt_dir = self.repo_path / "ckpt"
                third_party_dir = self.repo_path / "third_party"
                
                if not ckpt_dir.exists() or not third_party_dir.exists():
                    logger.warning(
                        f"Runtime files not found. You need to download them:\n"
                        f"  huggingface-cli download lglg666/SongGeneration-Runtime --local-dir ./runtime\n"
                        f"  mv runtime/ckpt {self.repo_path}/ckpt\n"
                        f"  mv runtime/third_party {self.repo_path}/third_party"
                    )
                else:
                    self.runtime_path = self.repo_path
                
                # Check for Git LFS pointer files
                tools_file = self.repo_path / "tools" / "new_prompt.pt"
                if tools_file.exists():
                    try:
                        with open(tools_file, "r", encoding="utf-8") as f:
                            first_line = f.readline()
                            if "version https://git-lfs.github.com" in first_line:
                                logger.warning(
                                    f"Detected Git LFS pointer file at {tools_file}. "
                                    f"The actual file needs to be downloaded.\n"
                                    f"Run: cd {self.repo_path} && git lfs install && git lfs pull"
                                )
                    except (UnicodeDecodeError, Exception):
                        # File is binary (good - it's the actual file, not a pointer)
                        pass
                
                # Determine checkpoint path
                checkpoint_name = self.model_id.split("/")[-1] if "/" in self.model_id else self.model_id
                # Check if it's a local path
                if Path(self.model_id).exists():
                    self.checkpoint_path = Path(self.model_id)
                else:
                    # Try to find it in the repo or assume it needs to be downloaded
                    checkpoint_dir = self.repo_path / checkpoint_name.replace("-", "_")
                    if checkpoint_dir.exists():
                        self.checkpoint_path = checkpoint_dir
                    else:
                        logger.warning(
                            f"Model checkpoint '{checkpoint_name}' not found locally.\n"
                            f"You may need to download it:\n"
                            f"  huggingface-cli download {self.model_id} --local-dir {checkpoint_dir}\n"
                            f"Or set SONG_GENERATION_MODEL_ID to a local path."
                        )
                        # Still mark as initialized - we'll try to use it anyway
                        self.checkpoint_path = checkpoint_dir
            else:
                # No repo path configured - provide helpful error
                raise RuntimeError(
                    "LeVo SongGeneration requires the official repository to be set up.\n\n"
                    "Setup steps:\n"
                    "1. Clone the repository:\n"
                    "   git clone https://github.com/tencent-ailab/SongGeneration.git\n"
                    "   cd SongGeneration\n\n"
                    "2. Install dependencies:\n"
                    "   pip install -r requirements.txt\n"
                    "   pip install -r requirements_nodeps.txt --no-deps\n\n"
                    "3. Download runtime files:\n"
                    "   huggingface-cli download lglg666/SongGeneration-Runtime --local-dir ./runtime\n"
                    "   mv runtime/ckpt ckpt\n"
                    "   mv runtime/third_party third_party\n\n"
                    "4. Download model checkpoint:\n"
                    "   huggingface-cli download lglg666/SongGeneration-base --local-dir ./songgeneration_base\n\n"
                    "5. Set the repository path:\n"
                    "   export SONG_GENERATION_REPO_PATH=/path/to/SongGeneration\n\n"
                    "For more details, see: https://github.com/tencent-ailab/SongGeneration"
                )
            
            self._initialized = True
            logger.info(f"SongGeneration model initialized (repo: {self.repo_path})")
            
        except RuntimeError:
            # Re-raise RuntimeErrors (they already have helpful messages)
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SongGeneration model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize SongGeneration model: {e}")
    
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
        Generate music using SongGeneration.
        
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
            raise RuntimeError("SongGeneration model is not available")
        
        self._initialize_model()
        
        # Default lyrics if not provided
        if lyrics is None:
            lyrics = ""
        
        # Check for cancellation before starting
        if cancellation_event and cancellation_event.is_set():
            raise CancelledError("Generation was cancelled before starting")
        
        results = []
        
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
                
                # Generate audio using LeVo SongGeneration
                # LeVo requires JSONL input format and uses a shell script
                    if progress_callback:
                        version_progress = 10.0
                        progress_callback(
                            base_progress + (version_progress / num_versions),
                        f"Preparing input for version {i+1}/{num_versions}..."
                        )
                    
                    # Check cancellation before model call
                    if cancellation_event and cancellation_event.is_set():
                        raise CancelledError(f"Generation was cancelled during version {i+1}/{num_versions}")
                    
                # Create temporary JSONL file for this version
                jsonl_file = self.output_dir / f"{version_id}_input.jsonl"
                
                # Format lyrics with structure tags if not already formatted
                formatted_lyrics = lyrics
                if lyrics and not any(tag in lyrics for tag in ["[Verse]", "[Chorus]", "[Bridge]", "[Intro]", "[Outro]"]):
                    # Try to format lyrics with basic structure
                    lines = lyrics.strip().split("\n")
                    if lines:
                        formatted_lyrics = "[Verse]\n" + "\n".join(lines[:4])
                        if len(lines) > 4:
                            formatted_lyrics += "\n[Chorus]\n" + "\n".join(lines[4:8])
                
                # Build descriptions from prompt
                descriptions = prompt
                if kwargs.get("genre"):
                    descriptions += f", {kwargs.get('genre')}"
                if kwargs.get("bpm"):
                    descriptions += f", the bpm is {kwargs.get('bpm')}"
                
                # Create JSONL entry
                jsonl_entry = {
                    "idx": version_id,
                    "gt_lyric": formatted_lyrics or "[Verse]\n" + prompt,
                    "descriptions": descriptions
                }
                
                # Add optional fields
                if kwargs.get("prompt_audio_path"):
                    jsonl_entry["prompt_audio_path"] = kwargs.get("prompt_audio_path")
                elif kwargs.get("auto_prompt_audio_type"):
                    jsonl_entry["auto_prompt_audio_type"] = kwargs.get("auto_prompt_audio_type")
                
                # Write JSONL file
                with open(jsonl_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")
                
                logger.info(f"Created JSONL input file: {jsonl_file}")
                
                if progress_callback:
                    version_progress = 30.0
                    progress_callback(
                        base_progress + (version_progress / num_versions),
                        f"Running SongGeneration for version {i+1}/{num_versions}..."
                    )
                
                # Check cancellation
                if cancellation_event and cancellation_event.is_set():
                    raise CancelledError(f"Generation was cancelled during version {i+1}/{num_versions}")
                
                # Prepare output directory for this version
                version_output_dir = self.output_dir / version_id
                version_output_dir.mkdir(parents=True, exist_ok=True)
                
                # Call generate.sh script
                generate_script = self.repo_path / "generate.sh"
                if not generate_script.exists():
                    raise RuntimeError(f"generate.sh not found at {generate_script}")
                
                # Build command
                cmd = [
                    "sh",
                    str(generate_script),
                    str(self.checkpoint_path),
                    str(jsonl_file),
                    str(version_output_dir)
                ]
                
                # Add optional flags
                if kwargs.get("low_mem"):
                    cmd.append("--low_mem")
                if kwargs.get("not_use_flash_attn"):
                    cmd.append("--not_use_flash_attn")
                if kwargs.get("separate"):
                    cmd.append("--separate")
                elif kwargs.get("bgm"):
                    cmd.append("--bgm")
                elif kwargs.get("vocal"):
                    cmd.append("--vocal")
                
                logger.info(f"Running command: {' '.join(cmd)}")
                
                # Run the generation script
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=str(self.repo_path),
                        text=True
                    )
                    
                    # Monitor process with cancellation support
                    while process.poll() is None:
                        if cancellation_event and cancellation_event.is_set():
                            process.terminate()
                            process.wait(timeout=5)
                            raise CancelledError(f"Generation was cancelled during version {i+1}/{num_versions}")
                        # Update progress periodically (this is approximate)
                        if progress_callback:
                            version_progress = min(version_progress + 5, 90.0)
                            progress_callback(
                                base_progress + (version_progress / num_versions),
                                f"Generating version {i+1}/{num_versions}..."
                            )
                        import time
                        time.sleep(1)
                    
                    # Check return code
                    if process.returncode != 0:
                        stderr_output = process.stderr.read() if process.stderr else "No error output"
                        stdout_output = process.stdout.read() if process.stdout else ""
                        
                        # Check for common issues
                        error_msg = f"SongGeneration script failed with return code {process.returncode}.\n"
                        
                        # Check for Git LFS pointer file issue
                        if "invalid load key" in stderr_output or "UnpicklingError" in stderr_output:
                            tools_file = self.repo_path / "tools" / "new_prompt.pt"
                            if tools_file.exists():
                                # Check if it's a Git LFS pointer
                                try:
                                    with open(tools_file, "r") as f:
                                        first_line = f.readline()
                                        if "version https://git-lfs.github.com" in first_line:
                                            error_msg += (
                                                "\n\nDetected Git LFS pointer file issue. "
                                                "The tools/new_prompt.pt file is a Git LFS pointer, not the actual file.\n"
                                                "To fix this, run:\n"
                                                f"  cd {self.repo_path}\n"
                                                "  git lfs install\n"
                                                "  git lfs pull\n"
                                                "\nOr download the file manually from the repository."
                                            )
                                except Exception:
                                    pass
                        
                        error_msg += f"\n\nError output:\n{stderr_output}"
                        if stdout_output:
                            error_msg += f"\n\nStandard output:\n{stdout_output}"
                        
                        raise RuntimeError(error_msg)
                    
                except subprocess.TimeoutExpired:
                    process.kill()
                    raise RuntimeError("SongGeneration script timed out")
                except FileNotFoundError:
                    raise RuntimeError(
                        f"Could not find generate.sh script. "
                        f"Please ensure SONG_GENERATION_REPO_PATH is set correctly."
                    )
                
                # Find the generated audio file
                # LeVo typically outputs files with the idx as part of the name
                generated_files = list(version_output_dir.glob(f"*{version_id}*"))
                if not generated_files:
                    # Try to find any audio files in the output directory
                    generated_files = list(version_output_dir.glob("*.wav")) + list(version_output_dir.glob("*.mp3"))
                
                if not generated_files:
                    raise RuntimeError(
                        f"No output files found in {version_output_dir}. "
                        f"Check the SongGeneration logs for errors."
                    )
                
                # Use the first generated file (or handle multiple files if --separate was used)
                generated_file = generated_files[0]
                
                # Copy to final output path if needed
                if generated_file != output_path:
                    shutil.copy2(generated_file, output_path)
                    logger.info(f"Copied generated file from {generated_file} to {output_path}")
                
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
                        "model": "song-generation",
                        "version": i + 1,
                        "format": format,
                        "seed": manual_seeds,
                        "model_id": self.model_id,
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
        """Check if SongGeneration model is available."""
        try:
            # Check if repository path is configured
            if not self.repo_path or not self.repo_path.exists():
                logger.warning("SongGeneration repository path not configured or doesn't exist")
                return False
            
            # Check if generate.sh exists
            generate_script = self.repo_path / "generate.sh"
            if not generate_script.exists():
                logger.warning(f"generate.sh not found at {generate_script}")
                return False
            
            # Check if runtime files exist (warn but don't fail)
            ckpt_dir = self.repo_path / "ckpt"
            third_party_dir = self.repo_path / "third_party"
            if not ckpt_dir.exists() or not third_party_dir.exists():
                logger.warning("Runtime files (ckpt/third_party) not found - generation may fail")
            
            # Check if checkpoint exists (warn but don't fail)
            if self.checkpoint_path and not self.checkpoint_path.exists():
                logger.warning(f"Model checkpoint not found at {self.checkpoint_path}")
            
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
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the SongGeneration model."""
        info = {
            "name": "SongGeneration",
            "type": "music_generation",
            "device": self.device,
            "initialized": self._initialized,
            "model_id": self.model_id,
            "source": "huggingface.co/tencent/SongGeneration",
        }
        
        if self._initialized and self.model is not None:
            try:
                info["model_type"] = str(type(self.model))
            except Exception:
                pass
        
        return info
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model is not None:
            logger.info("Cleaning up SongGeneration model resources")
            del self.model
            self.model = None
            
            # Clear GPU cache if CUDA is available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("Cleared CUDA cache")
            
            self._initialized = False
            logger.info("SongGeneration model resources cleaned up")

