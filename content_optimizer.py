"""
Content Optimizer specialized class.

This module implements specialized functionality for optimizing content
for different social media platforms.
"""

import logging
import datetime
from typing import Dict, List, Optional, Any

from .content_generator import ContentGenerator
from ..llm_integration.base_text_llm import BaseTextLLM
from ..llm_integration.base_image_generator import BaseImageGenerator

logger = logging.getLogger("content_generation.content_optimizer")

class ContentOptimizer:
    """
    Content Optimizer for optimizing content for different social media platforms.
    
    This class specializes in:
    - Platform-specific content optimization
    - Cross-platform content adaptation
    - Content performance analysis and improvement
    """
    
    def __init__(self, text_llm: BaseTextLLM = None, image_generator: BaseImageGenerator = None, config: Dict = None):
        """
        Initialize the Content Optimizer.
        
        Args:
            text_llm: Text LLM provider
            image_generator: Image generation provider
            config: Configuration dictionary
        """
        self.text_llm = text_llm
        self.image_generator = image_generator
        self.config = config or {}
        
        # Platform-specific settings
        self.platform_settings = {
            "facebook": {
                "text_length": {"min": 40, "optimal": 100, "max": 5000},
                "hashtags": {"min": 0, "optimal": 2, "max": 5},
                "emojis": True,
                "image_ratio": "1.91:1",
                "tone": "conversational"
            },
            "twitter": {
                "text_length": {"min": 10, "optimal": 100, "max": 280},
                "hashtags": {"min": 1, "optimal": 2, "max": 3},
                "emojis": True,
                "image_ratio": "16:9",
                "tone": "concise"
            },
            "instagram": {
                "text_length": {"min": 20, "optimal": 150, "max": 2200},
                "hashtags": {"min": 3, "optimal": 10, "max": 30},
                "emojis": True,
                "image_ratio": "1:1",
                "tone": "visual"
            },
            "tiktok": {
                "text_length": {"min": 10, "optimal": 80, "max": 150},
                "hashtags": {"min": 2, "optimal": 4, "max": 7},
                "emojis": True,
                "image_ratio": "9:16",
                "tone": "trendy"
            }
        }
        
        # Optimization history
        self.optimization_history = []
        
        logger.info("Content Optimizer initialized")
    
    def optimize_text_for_platform(self, text: str, source_platform: str, target_platform: str) -> Dict:
        """
        Optimize text content for a specific platform.
        
        Args:
            text: Original text content
            source_platform: Original platform
            target_platform: Target platform
            
        Returns:
            Dict containing the optimized text
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return {"success": False, "error": "No text LLM provider configured"}
        
        # Get platform-specific settings
        source_settings = self.platform_settings.get(source_platform.lower(), {})
        target_settings = self.platform_settings.get(target_platform.lower(), {})
        
        try:
            # Create an optimization prompt
            prompt = f"""
            Optimize this {source_platform} post for {target_platform}:
            
            Original content: "{text}"
            
            Target platform guidelines:
            - Text length: optimal {target_settings.get('text_length', {}).get('optimal', 'appropriate')} characters, max {target_settings.get('text_length', {}).get('max', 'platform limit')}
            - Hashtags: optimal {target_settings.get('hashtags', {}).get('optimal', 'appropriate')} hashtags
            - Tone: {target_settings.get('tone', 'appropriate for platform')}
            - Emojis: {"include appropriate emojis" if target_settings.get('emojis', True) else "minimize emoji use"}
            
            Return only the optimized content without any explanations or additional text.
            """
            
            # Generate optimized content
            optimized_text = self.text_llm.generate_text(prompt, max_tokens=500, temperature=0.4)
            
            # Remove any quotation marks that might be included
            optimized_text = optimized_text.strip('"\'')
            
            result = {
                "original_text": text,
                "optimized_text": optimized_text,
                "source_platform": source_platform,
                "target_platform": target_platform,
                "optimized_at": datetime.datetime.now().isoformat(),
                "success": True
            }
            
            # Add to history
            self.optimization_history.append({
                "type": "text_optimization",
                "source_platform": source_platform,
                "target_platform": target_platform,
                "optimized_at": result["optimized_at"],
                "content": result
            })
            
            return result
        except Exception as e:
            logger.error(f"Error optimizing text content: {e}")
            return {"success": False, "error": str(e)}
    
    def optimize_image_for_platform(self, image_path: str, source_platform: str, target_platform: str) -> Dict:
        """
        Optimize image content for a specific platform.
        
        Args:
            image_path: Path to the original image
            source_platform: Original platform
            target_platform: Target platform
            
        Returns:
            Dict containing the optimized image data
        """
        if not self.image_generator:
            logger.error("No image generator configured")
            return {"success": False, "error": "No image generator configured"}
        
        try:
            # Use the image generator to optimize the image
            result = self.image_generator.optimize_for_platform(
                image_path=image_path,
                platform=target_platform
            )
            
            # Add metadata
            result["source_platform"] = source_platform
            result["target_platform"] = target_platform
            result["optimized_at"] = datetime.datetime.now().isoformat()
            
            # Add to history
            self.optimization_history.append({
                "type": "image_optimization",
                "source_platform": source_platform,
                "target_platform": target_platform,
                "optimized_at": result["optimized_at"],
                "content": result
            })
            
            return result
        except Exception as e:
            logger.error(f"Error optimizing image content: {e}")
            return {"success": False, "error": str(e)}
    
    def optimize_combined_content(self, content: Dict, source_platform: str, target_platform: str) -> Dict:
        """
        Optimize combined text and image content for a specific platform.
        
        Args:
            content: Original content dictionary with text and image
            source_platform: Original platform
            target_platform: Target platform
            
        Returns:
            Dict containing the optimized content
        """
        result = {
            "source_platform": source_platform,
            "target_platform": target_platform,
            "optimized_at": datetime.datetime.now().isoformat(),
            "success": True
        }
        
        # Optimize text if present
        if "text" in content:
            if isinstance(content["text"], str):
                text_result = self.optimize_text_for_platform(
                    text=content["text"],
                    source_platform=source_platform,
                    target_platform=target_platform
                )
                result["text"] = text_result.get("optimized_text", content["text"])
                result["text_optimization"] = text_result
            elif isinstance(content["text"], dict) and "text" in content["text"]:
                text_result = self.optimize_text_for_platform(
                    text=content["text"]["text"],
                    source_platform=source_platform,
                    target_platform=target_platform
                )
                result["text"] = content["text"].copy()
                result["text"]["text"] = text_result.get("optimized_text", content["text"]["text"])
                result["text_optimization"] = text_result
        
        # Optimize image if present
        if "image" in content and isinstance(content["image"], dict) and "local_path" in content["image"]:
            image_result = self.optimize_image_for_platform(
                image_path=content["image"]["local_path"],
                source_platform=source_platform,
                target_platform=target_platform
            )
            result["image"] = image_result
        elif "image_path" in content:
            image_result = self.optimize_image_for_platform(
                image_path=content["image_path"],
                source_platform=source_platform,
                target_platform=target_platform
            )
            result["image"] = image_result
        
        # Add to history
        self.optimization_history.append({
            "type": "combined_optimization",
            "source_platform": source_platform,
            "target_platform": target_platform,
            "optimized_at": result["optimized_at"],
            "content": result
        })
        
        return result
    
    def get_platform_recommendations(self, content: str) -> Dict:
        """
        Get recommendations for which platforms content is best suited for.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dict containing platform recommendations
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return {"success": False, "error": "No text LLM provider configured"}
        
        try:
            # Create an analysis prompt
            prompt = f"""
            Analyze this content and recommend which social media platforms it would perform best on.
            Rate each platform (Facebook, Twitter, Instagram, TikTok) on a scale of 1-10 for this content.
            
            Content: "{content}"
            
            Format the response as JSON with platform names as keys and scores as values.
            Include a brief explanation for each platform's score.
            """
            
            # Generate analysis
            analysis = self.text_llm.generate_text(prompt, max_tokens=500, temperature=0.3)
            
            # Parse the response
            try:
                # Check if the response is wrapped in ```json and ``` markers
                if "```json" in analysis:
                    json_str = analysis.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis:
                    json_str = analysis.split("```")[1].strip()
                else:
                    json_str = analysis.strip()
                
                import json
                recommendations = json.loads(json_str)
                
                result = {
                    "content": content,
                    "recommendations": recommendations,
                    "analyzed_at": datetime.datetime.now().isoformat(),
                    "success": True
                }
                
                return result
            except Exception as e:
                logger.error(f"Error parsing platform recommendations: {e}")
                return {
                    "success": False,
                    "error": f"Error parsing recommendations: {e}",
                    "raw_response": analysis
                }
        except Exception as e:
            logger.error(f"Error getting platform recommendations: {e}")
            return {"success": False, "error": str(e)}
    
    def get_content_improvement_suggestions(self, content: str, platform: str) -> Dict:
        """
        Get suggestions for improving content for a specific platform.
        
        Args:
            content: Content to analyze
            platform: Target platform
            
        Returns:
            Dict containing improvement suggestions
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return {"success": False, "error": "No text LLM provider configured"}
        
        # Get platform-specific settings
        platform_settings = self.platform_settings.get(platform.lower(), {})
        
        try:
            # Create an analysis prompt
            prompt = f"""
            Analyze this {platform} content and provide specific suggestions for improvement:
            
            Content: "{content}"
            
            Platform guidelines:
            - Text length: optimal {platform_settings.get('text_length', {}).get('optimal', 'appropriate')} characters
            - Hashtags: optimal {platform_settings.get('hashtags', {}).get('optimal', 'appropriate')} hashtags
            - Tone: {platform_settings.get('tone', 'appropriate for platform')}
            - Emojis: {"include appropriate emojis" if platform_settings.get('emojis', True) else "minimize emoji use"}
            
            Format the response as JSON with these fields:
            - overall_score: 1-10 rating of the content
            - strengths: array of content strengths
            - weaknesses: array of content weaknesses
            - suggestions: array of specific improvement suggestions
            - improved_version: an improved version of the content
            """
            
            # Generate analysis
            analysis = self.text_llm.generate_text(prompt, max_tokens=800, temperature=0.4)
            
            # Parse the response
            try:
                # Check if the response is wrapped in ```json and ``` markers
                if "```json" in analysis:
                    json_str = analysis.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis:
                    json_str = analysis.split("```")[1].strip()
                else:
                    json_str = analysis.strip()
                
                import json
                suggestions = json.loads(json_str)
                
                result = {
                    "content": content,
                    "platform": platform,
                    "suggestions": suggestions,
                    "analyzed_at": datetime.datetime.now().isoformat(),
                    "success": True
                }
                
                return result
            except Exception as e:
                logger.error(f"Error parsing improvement suggestions: {e}")
                return {
                    "success": False,
                    "error": f"Error parsing suggestions: {e}",
                    "raw_response": analysis
                }
        except Exception as e:
            logger.error(f"Error getting improvement suggestions: {e}")
            return {"success": False, "error": str(e)}
    
    def get_optimization_history(self, platform: str = None, limit: int = 10) -> List[Dict]:
        """
        Get optimization history.
        
        Args:
            platform: Filter by platform
            limit: Maximum number of items to return
            
        Returns:
            List of optimization history items
        """
        filtered_history = self.optimization_history
        
   <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>