"""Mistral model for lyrics generation.

Model Options:
- ministral/Ministral-3b-instruct (default): 3B parameters, well-tested and stable
- ministral/Ministral-8B-Instruct-2410: Alternative 8B model version
- Quantized versions: Use MISTRAL_MODEL_NAME env var with quantized model names
  Example: "mistralai/Mistral-7B-Instruct-v0.2" with 4-bit quantization (requires bitsandbytes)

For quantized models, you can also set USE_QUANTIZATION=true and QUANTIZATION_BITS=4 or 8
to enable automatic quantization (requires bitsandbytes library).
"""

import logging
import os
from typing import Optional
import torch

logger = logging.getLogger(__name__)

# Try to import transformers, but make it optional
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers library not available. Lyrics generation will not work.")


class MistralLyricsModel:
    """Mistral model for generating and refining lyrics."""
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize the Mistral model.
        
        Args:
            model_name: HuggingFace model name (defaults to ministral/Ministral-3b-instruct)
            device: Device to run on ('cpu', 'cuda', 'mps', etc.)
        """
        self.model_name = model_name or os.getenv(
            "MISTRAL_MODEL_NAME",
            "ministral/Ministral-3b-instruct"
        )
        self.device = device or os.getenv("DEVICE", "cpu")
        self.tokenizer = None
        self.model = None
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization of the model."""
        if self._initialized:
            return
        
        if not TRANSFORMERS_AVAILABLE:
            logger.error("transformers library is not available")
            return
        
        try:
            logger.info(f"Loading Mistral model: {self.model_name} on device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
            elif self.device == "mps":
                # MPS (Metal Performance Shaders on macOS)
                # Use float32 for MPS as float16 can cause inf/nan issues in probability distributions
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    device_map=None,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model = self.model.to(self.device)
            else:
                # CPU or other devices
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    device_map=None,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model = self.model.to(self.device)
            
            self.model.eval()
            self._initialized = True
            logger.info("Mistral model loaded successfully")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to load Mistral model: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if the model is available."""
        if not TRANSFORMERS_AVAILABLE:
            return False
        
        try:
            self._initialize()
            return self._initialized and self.model is not None and self.tokenizer is not None
        except Exception:
            return False
    
    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
        prompt: Optional[str] = None  # Deprecated: for backward compatibility
    ) -> str:
        """
        Generate text using the Mistral model.
        
        Args:
            user_prompt: User prompt/query for generation
            system_prompt: Optional system prompt to set context and instructions
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            do_sample: Whether to use sampling
            prompt: Deprecated - use user_prompt instead. If provided, used as user_prompt.
            
        Returns:
            Generated text
        """
        if not self.is_available():
            raise RuntimeError("Mistral model is not available")
        
        # Backward compatibility: if prompt is provided, use it as user_prompt
        if prompt is not None:
            user_prompt = prompt
        
        try:
            # Build messages list for chat template
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add user prompt
            messages.append({"role": "user", "content": user_prompt})
            
            # Apply chat template to format the prompt correctly
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize with proper attention mask generation
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # Validate generation parameters to avoid invalid probability distributions
            if temperature <= 0:
                logger.warning(f"Invalid temperature {temperature}, using default 0.7")
                temperature = 0.7
            if top_p <= 0 or top_p > 1:
                logger.warning(f"Invalid top_p {top_p}, using default 0.9")
                top_p = 0.9
            
            # Get input length for extracting generated tokens later
            input_length = inputs["input_ids"].shape[1]
            
            # Generate
            with torch.no_grad():
                # For MPS, ensure we're using appropriate settings
                generation_kwargs = {
                    "max_new_tokens": max_length,
                    "pad_token_id": self.tokenizer.eos_token_id,
                    "eos_token_id": self.tokenizer.eos_token_id,
                }
                
                if do_sample:
                    generation_kwargs.update({
                        "temperature": max(temperature, 0.01),  # Ensure temperature > 0
                        "top_p": top_p,
                        "do_sample": True,
                    })
                else:
                    generation_kwargs["do_sample"] = False
                
                outputs = self.model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            # Extract only the newly generated tokens (skip the input tokens)
            generated_token_ids = outputs[0][input_length:]
            
            # Decode only the generated tokens
            generated_text = self.tokenizer.decode(
                generated_token_ids,
                skip_special_tokens=True
            )
            
            # Clean up any remaining special tokens that might have been missed
            # Common chat template tokens
            chat_tokens = [
                "<|im_start|>",
                "<|im_end|>",
                "<|user|>",
                "<|assistant|>",
                "<|system|>",
                "<|endoftext|>",
                "<|end|>",
                "<s>",
                "</s>",
            ]
            
            for token in chat_tokens:
                generated_text = generated_text.replace(token, "")
            
            # Clean up any extra whitespace but preserve line breaks
            lines = generated_text.split("\n")
            cleaned_lines = []
            for line in lines:
                cleaned_line = line.strip()
                if cleaned_line:  # Keep non-empty lines
                    cleaned_lines.append(cleaned_line)
            
            generated_text = "\n".join(cleaned_lines).strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise RuntimeError(f"Text generation failed: {str(e)}")
    
    def get_model_info(self) -> dict:
        """Get information about the model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "available": self.is_available(),
            "transformers_available": TRANSFORMERS_AVAILABLE
        }

