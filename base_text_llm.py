"""
Base LLM Provider interface for text generation.

This module defines the abstract base class that all text LLM providers
must implement to ensure consistent functionality across different providers.
"""

import abc
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("llm_integration.base_text_llm")

class BaseTextLLM(abc.ABC):
    """
    Abstract base class for text LLM providers.
    
    This class defines the interface that all text LLM providers must implement
    to ensure consistent functionality across different providers.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the text LLM provider.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.provider_name = "base"
        self.api_key = self.config.get("api_key")
        
        logger.info(f"Base Text LLM initialized")
    
    @abc.abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: Input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)
            
        Returns:
            str: Generated text
        """
        pass
    
    @abc.abstractmethod
    def generate_social_media_post(self, platform: str, topic: str, tone: str = "professional", 
                                  hashtags: int = 3, emojis: bool = True) -> Dict:
        """
        Generate a social media post for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the post
            tone: Tone of the post (professional, casual, humorous, etc.)
            hashtags: Number of hashtags to include
            emojis: Whether to include emojis
            
        Returns:
            Dict containing the generated post content
        """
        pass
    
    @abc.abstractmethod
    def generate_content_variations(self, content: str, variations: int = 3) -> List[str]:
        """
        Generate variations of existing content.
        
        Args:
            content: Original content
            variations: Number of variations to generate
            
        Returns:
            List of content variations
        """
        pass
    
    @abc.abstractmethod
    def optimize_for_platform(self, content: str, platform: str) -> str:
        """
        Optimize content for a specific platform.
        
        Args:
            content: Original content
            platform: Target platform
            
        Returns:
            str: Optimized content
        """
        pass
    
    def validate_api_key(self) -> bool:
        """
        Validate the API key.
        
        Returns:
            bool: Whether the API key is valid
        """
        if not self.api_key:
            logger.error(f"No API key provided for {self.provider_name}")
            return False
        
        return True
