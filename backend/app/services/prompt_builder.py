"""Service for building prompts from user inputs."""

from typing import Optional


class PromptBuilder:
    """Builds prompts for music generation from user inputs."""
    
    @staticmethod
    def build_prompt(
        style: str,
        topic: Optional[str] = None,
        refrain: Optional[str] = None,
        text: Optional[str] = None
    ) -> str:
        """
        Build a prompt from user inputs.
        
        Args:
            style: Style of music
            topic: Optional topic or theme
            refrain: Optional refrain line
            text: Optional complete text/lyrics
            
        Returns:
            Formatted prompt string
        """
        # If complete text is provided, use it as the primary prompt
        if text:
            prompt = text
            if style:
                prompt = f"{prompt} (Style: {style})"
            if topic:
                prompt = f"{prompt} (Topic: {topic})"
            return prompt
        
        # Otherwise, build from components
        parts = []
        
        # Style is always included
        parts.append(f"Style: {style}")
        
        if topic:
            parts.append(f"Topic: {topic}")
        
        if refrain:
            parts.append(f"Refrain: {refrain}")
        
        return ", ".join(parts)

