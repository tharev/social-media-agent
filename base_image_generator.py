"""
Base Image Generation Provider interface.

This module defines the abstract base class that all image generation providers
must implement to ensure consistent functionality across different providers.
"""

import abc
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("llm_integration.base_image_generator")

class BaseImageGenerator(abc.ABC):
    """
    Abstract base class for image generation providers.
    
    This class defines the interface that all image generation providers must implement
    to ensure consistent functionality across different providers.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the image generation provider.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.provider_name = "base"
        self.api_key = self.config.get("api_key")
        
        logger.info(f"Base Image Generator initialized")
    
    @abc.abstractmethod
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                      style: str = "natural", format: str = "url") -> Dict:
        """
        Generate an image based on a prompt.
        
        Args:
            prompt: Text description of the desired image
            size: Size of the image (e.g., "1024x1024")
            style: Style of the image (e.g., "natural", "artistic")
            format: Output format ("url" or "base64")
            
        Returns:
            Dict containing the generated image data
        """
        pass
    
    @abc.abstractmethod
    def generate_social_media_image(self, platform: str, topic: str, 
                                   style: str = "professional") -> Dict:
        """
        Generate a social media image for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the image
            style: Style of the image
            
        Returns:
            Dict containing the generated image data
        """
        pass
    
    @abc.abstractmethod
    def generate_variations(self, image_path: str, variations: int = 3) -> List[Dict]:
        """
        Generate variations of an existing image.
        
        Args:
            image_path: Path to the original image
            variations: Number of variations to generate
            
        Returns:
            List of dictionaries containing the generated image variations
        """
        pass
    
    @abc.abstractmethod
    def optimize_for_platform(self, image_path: str, platform: str) -> Dict:
        """
        Optimize an image for a specific platform.
        
        Args:
            image_path: Path to the original image
            platform: Target platform
            
        Returns:
            Dict containing the optimized image data
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
