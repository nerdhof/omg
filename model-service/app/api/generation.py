"""Generation API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import multiprocessing
import os

from ..models.ace_step import ACEStepModel, CancelledError
from ..models.song_generation import SongGenerationModel, CancelledError as SongGenerationCancelledError
from ..core import (
    get_model, 
    switch_provider, 
    get_current_provider, 
    get_provider_status
)
from ..services.generation_job import job_manager, JobStatus

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerationRequest(BaseModel):
    """Request model for music generation."""
    prompt: str = Field(..., description="Text prompt describing the music to generate")
    duration: float = Field(..., gt=0, le=300, description="Target duration in seconds (max 300)")
    lyrics: Optional[str] = Field(None, description="Optional lyrics for the music (default: '[inst]' for instrumental)")
    num_versions: int = Field(1, ge=1, le=5, description="Number of versions to generate (1-5)")
    format: str = Field("wav", description="Output format ('wav' or 'mp3')")
    manual_seeds: Optional[int] = Field(None, description="Optional seed for reproducibility")
    job_id: Optional[str] = Field(None, description="Optional job ID (generated if not provided)")
    provider: Optional[str] = Field(None, description="Optional provider override ('ace-step' or 'song-generation'). Uses default from MUSIC_PROVIDER env var if not specified.")


class VersionResponse(BaseModel):
    """Response model for a single generated version."""
    id: str
    audio_path: str
    metadata: Dict[str, Any]


class GenerationResponse(BaseModel):
    """Response model for generation request (synchronous)."""
    versions: List[VersionResponse]


class GenerationJobResponse(BaseModel):
    """Response model for background generation job submission."""
    job_id: str
    status: str
    message: str = "Generation started in background"


class ProgressResponse(BaseModel):
    """Response model for job progress."""
    job_id: str
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str
    status: str


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    progress: float = Field(..., ge=0, le=100)
    current_step: str
    versions: Optional[List[VersionResponse]] = None
    error: Optional[str] = None


def _run_generation(
    job_id: str,
    prompt: str,
    duration: float,
    lyrics: Optional[str],
    num_versions: int,
    format: str,
    manual_seeds: Optional[int],
    cancellation_event: multiprocessing.Event,
    progress_queue: multiprocessing.Queue,
    shared_state: Dict[str, Any],
    **kwargs
):
    """
    Run generation in background process.
    
    This function runs in a separate process and cannot access the job object directly.
    It communicates via shared state and progress queue.
    """
    # Get provider from shared state (set by the API endpoint)
    provider = shared_state.get("provider", None)
    
    # Initialize model in worker process (models can't be shared across processes)
    model = get_model(provider=provider)
    
    try:
        # Update status to processing
        shared_state["status"] = JobStatus.PROCESSING.value
        progress_queue.put({"status": JobStatus.PROCESSING.value, "progress": 0.0, "step": "Starting generation"})
        
        # Progress callback that sends updates via queue
        def progress_callback(progress: float, step: str):
            progress_queue.put({"progress": progress, "step": step})
        
        # Run generation with progress and cancellation support
        results = model.generate(
            prompt=prompt,
            duration=duration,
            lyrics=lyrics,
            num_versions=num_versions,
            format=format,
            manual_seeds=manual_seeds,
            progress_callback=progress_callback,
            cancellation_event=cancellation_event,
            **kwargs
        )
        
        # Convert results to response format
        results_list = [
            {
                "id": r["id"],
                "audio_path": r["audio_path"],
                "metadata": r["metadata"]
            }
            for r in results
        ]
        
        # Update shared state with results
        shared_state["status"] = JobStatus.COMPLETED.value
        shared_state["results"] = results_list
        shared_state["progress"] = 100.0
        shared_state["current_step"] = "Completed"
        progress_queue.put({"status": JobStatus.COMPLETED.value, "progress": 100.0, "step": "Completed", "results": results_list})
        
        logger.info(f"Job {job_id} completed successfully")
        
    except (CancelledError, SongGenerationCancelledError):
        shared_state["status"] = JobStatus.CANCELLED.value
        current_progress = shared_state.get("progress", 0.0)
        shared_state["current_step"] = "Cancelled"
        progress_queue.put({"status": JobStatus.CANCELLED.value, "progress": current_progress, "step": "Cancelled"})
        logger.info(f"Job {job_id} was cancelled")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        shared_state["status"] = JobStatus.FAILED.value
        shared_state["error"] = str(e)
        progress_queue.put({"status": JobStatus.FAILED.value, "error": str(e)})


@router.post("/generate", response_model=GenerationJobResponse)
async def generate_music(request: GenerationRequest):
    """
    Start music generation in the background.
    
    Args:
        request: Generation request with prompt, duration, and num_versions
        
    Returns:
        Job ID and status
    """
    try:
        # Get provider (from request or use default)
        provider = request.provider.lower() if request.provider else None
        
        # Validate provider if specified
        if provider and provider not in ["ace-step", "song-generation"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {provider}. Supported providers: 'ace-step', 'song-generation'"
            )
        
        # Get model for the specified provider
        model = get_model(provider=provider)
        
        if not model.is_available():
            provider_name = provider or "default"
            raise HTTPException(
                status_code=503,
                detail=f"Model is not available for provider '{provider_name}'. Please check model service configuration."
            )
        
        # Create job
        job_id = job_manager.create_job(
            prompt=request.prompt,
            duration=request.duration,
            lyrics=request.lyrics,
            num_versions=request.num_versions,
            format=request.format,
            manual_seeds=request.manual_seeds,
            job_id=request.job_id
        )
        
        job = job_manager.get_job(job_id)
        
        # Store provider in shared state for the background process
        job.shared_state["provider"] = provider
        
        logger.info(
            f"Starting background generation job {job_id} with {request.num_versions} version(s) "
            f"using provider '{provider or 'default'}' and prompt: {request.prompt[:50]}..."
        )
        
        # Start generation in background process
        process = multiprocessing.Process(
            target=_run_generation,
            args=(
                job.job_id,
                job.prompt,
                job.duration,
                job.lyrics,
                job.num_versions,
                job.format,
                job.manual_seeds,
                job.cancellation_event,
                job.progress_queue,
                job.shared_state,
            ),
            kwargs=job.kwargs,
            daemon=False  # Don't use daemon to allow proper cleanup
        )
        process.start()
        job.process = process
        
        return GenerationJobResponse(
            job_id=job_id,
            status="pending",
            message="Generation started in background"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid provider: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to start generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start generation: {str(e)}"
        )


@router.get("/generate/{job_id}/progress", response_model=ProgressResponse)
async def get_generation_progress(job_id: str):
    """
    Get the progress of a generation job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Current progress and status
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Poll progress queue to get latest updates
    job._poll_progress_queue()
    
    return ProgressResponse(
        job_id=job_id,
        progress=job.progress,
        current_step=job.current_step,
        status=job.status.value
    )


@router.delete("/generate/{job_id}/cancel")
async def cancel_generation(job_id: str):
    """
    Cancel a generation job.
    
    Args:
        job_id: Job ID to cancel
        
    Returns:
        Success message
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} cannot be cancelled (status: {job.status.value})"
        )
    
    success = job.cancel()
    
    if success:
        return {"message": f"Job {job_id} cancelled", "job_id": job_id}
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel job {job_id}"
        )


@router.get("/generate/{job_id}/status", response_model=JobStatusResponse)
async def get_generation_status(job_id: str):
    """
    Get the status and results of a generation job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job status, progress, and results (if completed)
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Poll progress queue to get latest updates
    job._poll_progress_queue()
    
    versions = None
    if job.results:
        versions = [
            VersionResponse(
                id=r["id"],
                audio_path=r["audio_path"],
                metadata=r["metadata"]
            )
            for r in job.results
        ]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job.status.value,
        progress=job.progress,
        current_step=job.current_step,
        versions=versions,
        error=job.error
    )


class LyricsGenerationRequest(BaseModel):
    """Request model for lyrics generation/refinement."""
    current_lyrics: Optional[str] = Field(None, description="Existing lyrics for refinement")
    prompt: str = Field(..., description="Song prompt describing the music")
    duration: float = Field(..., gt=0, le=300, description="Target duration in seconds")
    topic: str = Field(..., description="Topic for the lyrics")


class LyricsGenerationResponse(BaseModel):
    """Response model for lyrics generation."""
    lyrics: str = Field(..., description="Generated or refined lyrics")


class ProviderSwitchRequest(BaseModel):
    """Request model for switching providers."""
    provider: str = Field(..., description="Provider name ('ace-step' or 'song-generation')")


class ProviderResponse(BaseModel):
    """Response model for provider information."""
    current_provider: Optional[str]
    available_providers: List[str]


class ProviderStatusResponse(BaseModel):
    """Response model for provider status."""
    providers: Dict[str, Any]


@router.get("/provider", response_model=ProviderResponse)
async def get_provider():
    """
    Get current provider and list of available providers.
    
    Returns:
        Current provider and available providers list
    """
    current = get_current_provider()
    available = ["ace-step", "song-generation"]
    
    return ProviderResponse(
        current_provider=current,
        available_providers=available
    )


@router.post("/provider/switch", response_model=Dict[str, Any])
async def switch_provider_endpoint(request: ProviderSwitchRequest):
    """
    Switch to a different music generation provider.
    
    This will clean up the current provider's resources and load the new provider.
    
    Args:
        request: Provider switch request with provider name
        
    Returns:
        Success message and new provider info
    """
    try:
        provider = request.provider.lower()
        
        if provider not in ["ace-step", "song-generation"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {provider}. Supported providers: 'ace-step', 'song-generation'"
            )
        
        # Switch provider (this will clean up the previous one)
        model = switch_provider(provider)
        
        # Get model info
        model_info = model.get_model_info()
        
        return {
            "message": f"Switched to provider: {provider}",
            "provider": provider,
            "model_info": model_info
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to switch provider: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to switch provider: {str(e)}"
        )


@router.get("/provider/status", response_model=ProviderStatusResponse)
async def get_provider_status_endpoint():
    """
    Get status information for all providers.
    
    Returns:
        Status information for each provider including availability and initialization state
    """
    try:
        status = get_provider_status()
        return ProviderStatusResponse(providers=status)
    except Exception as e:
        logger.error(f"Failed to get provider status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provider status: {str(e)}"
        )


def _run_mistral_generation(
    user_prompt: str,
    system_prompt: Optional[str],
    max_length: int,
    temperature: float,
    top_p: float,
    do_sample: bool,
    result_queue: multiprocessing.Queue,
    error_queue: multiprocessing.Queue
):
    """
    Run Mistral generation in a subprocess.
    
    This function runs in a separate process, loads the model, generates text,
    and then exits, ensuring cleanup of model resources.
    """
    try:
        # Import here to ensure it's in the subprocess context
        from ..models.mistral_lyrics import MistralLyricsModel
        
        # Get configuration from environment
        model_name = os.getenv("MISTRAL_MODEL_NAME", None)
        device = os.getenv("DEVICE", "cpu")
        
        logger.info(f"Loading Mistral model in subprocess (device: {device})")
        
        # Create and initialize model in this subprocess
        mistral_model = MistralLyricsModel(model_name=model_name, device=device)
        
        if not mistral_model.is_available():
            error_queue.put("Mistral model is not available. Please check model service configuration.")
            return
        
        logger.info("Generating lyrics with Mistral model...")
        
        # Generate lyrics
        lyrics = mistral_model.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample
        )
        
        # Clean up model resources explicitly
        if hasattr(mistral_model, 'model') and mistral_model.model is not None:
            del mistral_model.model
        if hasattr(mistral_model, 'tokenizer') and mistral_model.tokenizer is not None:
            del mistral_model.tokenizer
        del mistral_model
        
        # Clear GPU cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        # Put result in queue
        result_queue.put(lyrics)
        logger.info("Mistral generation completed, subprocess exiting")
        
    except Exception as e:
        logger.error(f"Mistral generation failed in subprocess: {e}", exc_info=True)
        error_queue.put(str(e))


@router.post("/lyrics/generate", response_model=LyricsGenerationResponse)
async def generate_lyrics(request: LyricsGenerationRequest):
    """
    Generate or refine lyrics using Mistral model.
    
    Accepts song context (prompt, duration, topic) and optionally existing lyrics
    for refinement. Returns generated or refined lyrics.
    
    The Mistral model runs in a separate subprocess that is cleaned up after each request.
    """
    try:
        # Build system and user prompts for lyrics generation
        if request.current_lyrics:
            # Refinement mode
            system_prompt = "You are a professional songwriter. Refine and improve lyrics for songs."
            user_prompt = f"""Refine and improve the following lyrics for a song.

IMPORTANT CONTEXT:
- Music style/description: {request.prompt}
- Target duration: {request.duration} seconds (lyrics must fit this timeframe)
- Topic/theme: {request.topic} (CRITICAL: All lyrics must stay strictly focused on this topic)

Current lyrics to refine:
{request.current_lyrics}

REQUIREMENTS:
1. Stay STRICTLY on the topic "{request.topic}"
2. Format lyrics using ACE lyrics sections: [verse], [chorus], [bridge]
3. Match the music style: {request.prompt}
4. Ensure lyrics fit within {request.duration} seconds of music
5. Build upon and improve the existing lyrics structure while maintaining their core message
6. Make lyrics more poetic, engaging, and suitable for the described music style"""
        else:
            # Generation mode
            system_prompt = "You are a professional songwriter. Write original lyrics for songs."
            user_prompt = f"""Write original lyrics for a song.

IMPORTANT CONTEXT:
- Music style/description: {request.prompt}
- Target duration: {request.duration} seconds (lyrics must fit this timeframe)
- Topic/theme: {request.topic} (CRITICAL: All lyrics must stay strictly focused on this topic)

REQUIREMENTS:
1. Stay STRICTLY on the topic "{request.topic}" - every line must relate to this theme. Do not deviate from this topic.
2. Format lyrics using ACE lyrics sections: [verse], [chorus], [bridge]
3. Match the music style: {request.prompt} - write lyrics that suit this musical style
4. Ensure lyrics fit within {request.duration} seconds of music - adjust length accordingly
5. Make lyrics poetic, memorable, and engaging"""
        
        logger.info(f"Generating lyrics with topic: {request.topic[:50]}...")
        
        # Create queues for communication with subprocess
        result_queue = multiprocessing.Queue()
        error_queue = multiprocessing.Queue()
        
        # Start Mistral generation in subprocess
        process = multiprocessing.Process(
            target=_run_mistral_generation,
            args=(
                user_prompt,
                system_prompt,
                1024,  # max_length
                0.9,   # temperature
                0.9,   # top_p
                True,  # do_sample
                result_queue,
                error_queue
            ),
            daemon=False  # Don't use daemon to allow proper cleanup
        )
        
        process.start()
        process.join()  # Wait for the process to complete
        
        # Check for errors
        if not error_queue.empty():
            error_msg = error_queue.get()
            raise HTTPException(
                status_code=503 if "not available" in error_msg else 500,
                detail=error_msg
            )
        
        # Get result
        if result_queue.empty():
            raise HTTPException(
                status_code=500,
                detail="Mistral generation completed but no result was returned"
            )
        
        lyrics = result_queue.get()
        
        if not lyrics:
            raise HTTPException(
                status_code=500,
                detail="Generated lyrics are empty"
            )
        
        return LyricsGenerationResponse(lyrics=lyrics)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lyrics generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lyrics generation failed: {str(e)}"
        )

