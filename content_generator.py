"""
Content Generator base class.

This module defines the base content generator class that handles
the generation of content for social media platforms.
"""

import logging
import datetime
from typing import Dict, List, Optional, Any

from ..llm_integration.base_text_llm import BaseTextLLM
from ..llm_integration.base_image_generator import BaseImageGenerator

logger = logging.getLogger("content_generation.content_generator")

class ContentGenerator:
    """
    Content Generator for creating social media content.
    
    This class handles:
    - Text content generation
    - Image content generation
    - Content optimization for different platforms
    - Content scheduling
    """
    
    def __init__(self, text_llm: BaseTextLLM = None, image_generator: BaseImageGenerator = None, config: Dict = None):
        """
        Initialize the Content Generator.
        
        Args:
            text_llm: Text LLM provider
            image_generator: Image generation provider
            config: Configuration dictionary
        """
        self.text_llm = text_llm
        self.image_generator = image_generator
        self.config = config or {}
        
        # Content generation settings
        self.default_tone = self.config.get("default_tone", "professional")
        self.default_hashtags = self.config.get("default_hashtags", 3)
        self.default_emojis = self.config.get("default_emojis", True)
        
        # Content history for tracking generated content
        self.content_history = []
        
        logger.info("Content Generator initialized")
    
    def generate_text_content(self, platform: str, topic: str, tone: str = None, 
                             hashtags: int = None, emojis: bool = None) -> Dict:
        """
        Generate text content for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the content
            tone: Tone of the content
            hashtags: Number of hashtags to include
            emojis: Whether to include emojis
            
        Returns:
            Dict containing the generated content
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return {"success": False, "error": "No text LLM provider configured"}
        
        # Use default values if not specified
        tone = tone or self.default_tone
        hashtags = hashtags if hashtags is not None else self.default_hashtags
        emojis = emojis if emojis is not None else self.default_emojis
        
        try:
            # Generate content using the text LLM
            content = self.text_llm.generate_social_media_post(
                platform=platform,
                topic=topic,
                tone=tone,
                hashtags=hashtags,
                emojis=emojis
            )
            
            # Add metadata
            content["platform"] = platform
            content["topic"] = topic
            content["tone"] = tone
            content["generated_at"] = datetime.datetime.now().isoformat()
            content["success"] = True
            
            # Add to history
            self.content_history.append({
                "type": "text",
                "platform": platform,
                "topic": topic,
                "generated_at": content["generated_at"],
                "content": content
            })
            
            return content
        except Exception as e:
            logger.error(f"Error generating text content: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_image_content(self, platform: str, topic: str, style: str = "professional") -> Dict:
        """
        Generate image content for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the content
            style: Style of the image
            
        Returns:
            Dict containing the generated content
        """
        if not self.image_generator:
            logger.error("No image generator configured")
            return {"success": False, "error": "No image generator configured"}
        
        try:
            # Generate image using the image generator
            image_result = self.image_generator.generate_social_media_image(
                platform=platform,
                topic=topic,
                style=style
            )
            
            # Add metadata
            image_result["platform"] = platform
            image_result["topic"] = topic
            image_result["style"] = style
            image_result["generated_at"] = datetime.datetime.now().isoformat()
            
            # Add to history
            self.content_history.append({
                "type": "image",
                "platform": platform,
                "topic": topic,
                "generated_at": image_result["generated_at"],
                "content": image_result
            })
            
            return image_result
        except Exception as e:
            logger.error(f"Error generating image content: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_combined_content(self, platform: str, topic: str, tone: str = None, 
                                style: str = "professional", hashtags: int = None, 
                                emojis: bool = None) -> Dict:
        """
        Generate combined text and image content for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the content
            tone: Tone of the text content
            style: Style of the image
            hashtags: Number of hashtags to include
            emojis: Whether to include emojis
            
        Returns:
            Dict containing the generated content
        """
        # Generate text content
        text_content = self.generate_text_content(
            platform=platform,
            topic=topic,
            tone=tone,
            hashtags=hashtags,
            emojis=emojis
        )
        
        # Generate image content
        image_content = self.generate_image_content(
            platform=platform,
            topic=topic,
            style=style
        )
        
        # Combine results
        combined_content = {
            "platform": platform,
            "topic": topic,
            "generated_at": datetime.datetime.now().isoformat(),
            "text": text_content,
            "image": image_content,
            "success": text_content.get("success", False) and image_content.get("success", False)
        }
        
        # Add to history
        self.content_history.append({
            "type": "combined",
            "platform": platform,
            "topic": topic,
            "generated_at": combined_content["generated_at"],
            "content": combined_content
        })
        
        return combined_content
    
    def optimize_content(self, content: Dict, target_platform: str) -> Dict:
        """
        Optimize content for a specific platform.
        
        Args:
            content: Original content
            target_platform: Target platform
            
        Returns:
            Dict containing the optimized content
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return {"success": False, "error": "No text LLM provider configured"}
        
        try:
            optimized_content = content.copy()
            
            # Optimize text content if present
            if "text" in content and isinstance(content["text"], str):
                optimized_text = self.text_llm.optimize_for_platform(
                    content=content["text"],
                    platform=target_platform
                )
                optimized_content["text"] = optimized_text
            elif "text" in content and isinstance(content["text"], dict) and "text" in content["text"]:
                optimized_text = self.text_llm.optimize_for_platform(
                    content=content["text"]["text"],
                    platform=target_platform
                )
                optimized_content["text"]["text"] = optimized_text
            
            # Optimize image content if present and image generator is available
            if self.image_generator and "image" in content and isinstance(content["image"], dict) and "data" in content["image"]:
                # For this to work, we'd need to download the image first
                # This is a placeholder for the actual implementation
                optimized_content["image"]["optimized"] = True
            
            optimized_content["platform"] = target_platform
            optimized_content["optimized"] = True
            optimized_content["optimized_at"] = datetime.datetime.now().isoformat()
            optimized_content["success"] = True
            
            return optimized_content
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_content_variations(self, content: Dict, variations: int = 3) -> List[Dict]:
        """
        Generate variations of existing content.
        
        Args:
            content: Original content
            variations: Number of variations to generate
            
        Returns:
            List of content variations
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return [{"success": False, "error": "No text LLM provider configured"}]
        
        try:
            content_variations = []
            
            # Generate text variations if text content is present
            if "text" in content and isinstance(content["text"], str):
                text_variations = self.text_llm.generate_content_variations(
                    content=content["text"],
                    variations=variations
                )
                
                # Create a variation for each text
                for i, text_var in enumerate(text_variations):
                    variation = content.copy()
                    variation["text"] = text_var
                    variation["variation_number"] = i + 1
                    variation["generated_at"] = datetime.datetime.now().isoformat()
                    content_variations.append(variation)
            elif "text" in content and isinstance(content["text"], dict) and "text" in content["text"]:
                text_variations = self.text_llm.generate_content_variations(
                    content=content["text"]["text"],
                    variations=variations
                )
                
                # Create a variation for each text
                for i, text_var in enumerate(text_variations):
                    variation = content.copy()
                    variation["text"] = variation["text"].copy()
                    variation["text"]["text"] = text_var
                    variation["variation_number"] = i + 1
                    variation["generated_at"] = datetime.datetime.now().isoformat()
                    content_variations.append(variation)
            else:
                logger.warning("No text content found to generate variations")
                return [{"success": False, "error": "No text content found to generate variations"}]
            
            return content_variations
        except Exception as e:
            logger.error(f"Error generating content variations: {e}")
            return [{"success": False, "error": str(e)}]
    
    def get_content_history(self, platform: str = None, content_type: str = None, 
                          limit: int = 10) -> List[Dict]:
        """
        Get content generation history.
        
        Args:
            platform: Filter by platform
            content_type: Filter by content type
            limit: Maximum number of items to return
            
        Returns:
            List of content history items
        """
        filtered_history = self.content_history
        
        # Filter by platform
        if platform:
            filtered_history = [item for item in filtered_history if item["platform"] == platform]
        
        # Filter by content type
        if content_type:
            filtered_history = [item for item in filtered_history if item["type"] == content_type]
        
        # Sort by generation time (newest first)
        filtered_history.sort(key=lambda x: x["generated_at"], reverse=True)
        
        # Limit the number of items
        return filtered_history[:limit]
