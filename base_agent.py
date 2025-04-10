"""
Base Platform Agent class that defines the interface for all social media platform agents.

This module provides the abstract base class that all platform-specific agents
must implement to ensure consistent functionality across different platforms.
"""

import abc
import datetime
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("platform_agents.base")

class BasePlatformAgent(abc.ABC):
    """
    Abstract base class for all social media platform agents.
    
    This class defines the interface that all platform-specific agents must implement
    to ensure consistent functionality across different platforms.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the platform agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.platform_name = "base"
        self.api_client = None
        self.metrics_cache = {}
        
        logger.info(f"Base Platform Agent initialized")
    
    @abc.abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform API.
        
        Returns:
            bool: Success status
        """
        pass
    
    @abc.abstractmethod
    def post_content(self, content_type: str, content: Dict) -> Dict:
        """
        Post content to the platform.
        
        Args:
            content_type: Type of content (text, image, video)
            content: Content data
            
        Returns:
            Dict containing post result information
        """
        pass
    
    @abc.abstractmethod
    def get_metrics(self, date: datetime.date) -> Dict:
        """
        Get metrics for a specific date.
        
        Args:
            date: Date to get metrics for
            
        Returns:
            Dict containing metrics
        """
        pass
    
    @abc.abstractmethod
    def get_post_metrics(self, post_id: str) -> Dict:
        """
        Get metrics for a specific post.
        
        Args:
            post_id: ID of the post
            
        Returns:
            Dict containing post metrics
        """
        pass
    
    def format_content(self, content: Dict) -> Dict:
        """
        Format content for the platform.
        
        Args:
            content: Generic content data
            
        Returns:
            Dict containing platform-specific formatted content
        """
        # Default implementation returns content unchanged
        return content
    
    def optimize_content(self, content: Dict) -> Dict:
        """
        Optimize content for the platform based on best practices.
        
        Args:
            content: Content data
            
        Returns:
            Dict containing optimized content
        """
        # Default implementation returns content unchanged
        return content
    
    def validate_content(self, content_type: str, content: Dict) -> Dict:
        """
        Validate content for the platform.
        
        Args:
            content_type: Type of content
            content: Content data
            
        Returns:
            Dict containing validation result
        """
        # Default implementation assumes content is valid
        return {"valid": True, "errors": []}
    
    def get_platform_limits(self) -> Dict:
        """
        Get platform-specific limits.
        
        Returns:
            Dict containing platform limits
        """
        # Default implementation with common limits
        return {
            "text_length": 280,  # Default to Twitter-like limit
            "image_size": 5 * 1024 * 1024,  # 5MB
            "video_length": 60,  # 60 seconds
            "daily_post_limit": 50
        }
    
    def get_best_posting_times(self) -> List[str]:
        """
        Get the best times to post on this platform.
        
        Returns:
            List of time strings in HH:MM format
        """
        # Default implementation with generic best times
        return ["09:00", "12:00", "15:00", "18:00"]
    
    def get_account_info(self) -> Dict:
        """
        Get information about the connected account.
        
        Returns:
            Dict containing account information
        """
        # Default implementation returns empty dict
        return {}
    
    def clear_metrics_cache(self) -> None:
        """
        Clear the metrics cache.
        """
        self.metrics_cache = {}
        logger.info(f"Cleared metrics cache for {self.platform_name}")
