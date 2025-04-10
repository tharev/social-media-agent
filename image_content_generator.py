"""
Image Content Generator specialized class.

This module implements specialized functionality for generating image content
for social media platforms, building on the base ContentGenerator.
"""

import logging
import datetime
import os
import random
import requests
from typing import Dict, List, Optional, Any

from .content_generator import ContentGenerator
from ..llm_integration.base_image_generator import BaseImageGenerator
from ..llm_integration.base_text_llm import BaseTextLLM

logger = logging.getLogger("content_generation.image_content_generator")

class ImageContentGenerator:
    """
    Image Content Generator for creating image-based social media content.
    
    This class specializes in:
    - Platform-specific image content generation
    - Image styles and formats
    - Image optimization for different platforms
    - Image variations
    """
    
    def __init__(self, image_generator: BaseImageGenerator = None, text_llm: BaseTextLLM = None, config: Dict = None):
        """
        Initialize the Image Content Generator.
        
        Args:
            image_generator: Image generation provider
            text_llm: Text LLM for generating image prompts
            config: Configuration dictionary
        """
        self.image_generator = image_generator
        self.text_llm = text_llm
        self.config = config or {}
        
        # Image generation settings
        self.default_style = self.config.get("default_style", "professional")
        self.image_output_dir = self.config.get("image_output_dir", "generated_images")
        
        # Platform-specific settings
        self.platform_settings = {
            "facebook": {
                "optimal_size": "1200x630",
                "style": "professional",
                "aspect_ratio": "1.91:1"
            },
            "twitter": {
                "optimal_size": "1200x675",
                "style": "vibrant",
                "aspect_ratio": "16:9"
            },
            "instagram": {
                "optimal_size": "1080x1080",
                "style": "artistic",
                "aspect_ratio": "1:1"
            },
            "tiktok": {
                "optimal_size": "1080x1920",
                "style": "trendy",
                "aspect_ratio": "9:16"
            }
        }
        
        # Image styles
        self.image_styles = {
            "professional": "Clean, corporate, polished professional look with neutral colors",
            "vibrant": "Bright, colorful, eye-catching with high contrast",
            "artistic": "Creative, aesthetic, visually pleasing with artistic elements",
            "minimalist": "Simple, clean, with lots of white space and minimal elements",
            "trendy": "Modern, following current visual trends, appealing to younger audiences",
            "vintage": "Retro, nostalgic feel with filters that mimic older photography",
            "natural": "Authentic, realistic imagery with natural lighting",
            "abstract": "Conceptual, symbolic representation using shapes, colors, and patterns"
        }
        
        # Content history for tracking generated content
        self.content_history = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.image_output_dir, exist_ok=True)
        
        logger.info("Image Content Generator initialized")
    
    def generate_image(self, platform: str, topic: str, style: str = None, 
                     prompt: str = None, save_locally: bool = True) -> Dict:
        """
        Generate an image for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the image
            style: Style of the image
            prompt: Custom prompt for image generation
            save_locally: Whether to save the image locally
            
        Returns:
            Dict containing the generated image data
        """
        if not self.image_generator:
            logger.error("No image generator configured")
            return {"success": False, "error": "No image generator configured"}
        
        # Get platform-specific settings
        platform_config = self.platform_settings.get(platform.lower(), {})
        
        # Use platform-specific defaults if not specified
        style = style or platform_config.get("style", self.default_style)
        
        try:
            # Generate or use custom prompt
            if not prompt and self.text_llm:
                # Generate a detailed prompt using the text LLM
                style_description = self.image_styles.get(style, style)
                prompt_request = f"""
                Create a detailed image generation prompt for a {platform} post about {topic}.
                The image should be {style_description}.
                Focus on visual elements, composition, colors, and mood.
                The prompt should be detailed enough for an AI image generator to create a compelling image.
                Return only the prompt text without any explanations or additional text.
                """
                
                prompt = self.text_llm.generate_text(prompt_request, max_tokens=200, temperature=0.7)
                
                # Clean up the prompt
                prompt = prompt.strip().strip('"\'')
            elif not prompt:
                # Create a basic prompt if no text LLM is available
                style_description = self.image_styles.get(style, style)
                prompt = f"A {style_description} image about {topic} for {platform}"
            
            # Generate the image
            if platform.lower() in self.platform_settings:
                # Use platform-specific generation
                image_result = self.image_generator.generate_social_media_image(
                    platform=platform,
                    topic=topic,
                    style=style
                )
            else:
                # Use generic image generation
                image_result = self.image_generator.generate_image(
                    prompt=prompt,
                    style=style,
                    format="url"
                )
            
            # Add metadata
            image_result["platform"] = platform
            image_result["topic"] = topic
            image_result["style"] = style
            image_result["prompt"] = prompt
            image_result["generated_at"] = datetime.datetime.now().isoformat()
            
            # Save image locally if requested
            if save_locally and image_result.get("success", False) and "data" in image_result:
                image_url = image_result["data"]
                if image_url and image_url.startswith("http"):
                    try:
                        # Create a filename
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{platform}_{topic.replace(' ', '_')}_{timestamp}.jpg"
                        filepath = os.path.join(self.image_output_dir, filename)
                        
                        # Download the image
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(response.content)
                            
                            image_result["local_path"] = filepath
                            logger.info(f"Saved image to {filepath}")
                    except Exception as e:
                        logger.error(f"Error saving image locally: {e}")
            
            # Add to history
            self.content_history.append({
                "type": "image",
                "platform": platform,
                "topic": topic,
                "style": style,
                "generated_at": image_result["generated_at"],
                "content": image_result
            })
            
            return image_result
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_image_series(self, platform: str, topic: str, count: int = 3, 
                            style: str = None, consistent: bool = True) -> List[Dict]:
        """
        Generate a series of related images.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the images
            count: Number of images to generate
            style: Style of the images
            consistent: Whether to maintain consistent style across images
            
        Returns:
            List of generated image data
        """
        if not self.image_generator:
            logger.error("No image generator configured")
            return [{"success": False, "error": "No image generator configured"}]
        
        try:
            # Generate a base prompt if we have a text LLM
            base_prompt = None
            if self.text_llm:
                prompt_request = f"""
                Create a detailed image generation prompt for a series of {count} related images about {topic} for {platform}.
                The images should tell a visual story or show different aspects of the topic.
                Return only the base prompt that can be modified for each image in the series.
                """
                
                base_prompt = self.text_llm.generate_text(prompt_request, max_tokens=200, temperature=0.7)
                base_prompt = base_prompt.strip().strip('"\'')
            
            # Generate the image series
            image_series = []
            for i in range(count):
                # Create a variation of the prompt for each image
                if base_prompt and self.text_llm:
                    variation_request = f"""
                    Create a variation of this base prompt for image {i+1} in a series of {count} related images:
                    Base prompt: "{base_prompt}"
                    
                    This should be part {i+1} of the visual story or a different aspect of {topic}.
                    Return only the modified prompt without any explanations.
                    """
                    
                    prompt = self.text_llm.generate_text(variation_request, max_tokens=200, temperature=0.7)
                    prompt = prompt.strip().strip('"\'')
                else:
                    # Create a basic prompt if no text LLM is available
                    prompt = f"Part {i+1} of a series about {topic} for {platform}"
                
                # Generate the image
                image_result = self.generate_image(
                    platform=platform,
                    topic=topic,
                    style=style,
                    prompt=prompt
                )
                
                # Add series metadata
                image_result["series_position"] = i + 1
                image_result["series_total"] = count
                
                image_series.append(image_result)
            
            return image_series
        except Exception as e:
            logger.error(f"Error generating image series: {e}")
            return [{"success": False, "error": str(e)}]
    
    def optimize_image_for_platform(self, image_path: str, target_platform: str) -> Dict:
        """
        Optimize an existing image for a specific platform.
        
        Args:
            image_path: Path to the original image
            target_platform: Target platform
            
        Returns:
            Dict containing the optimized image data
        """
        if not self.image_generator:
            logger.error("No image generator configured")
            return {"success": False, "error": "No image generator configured"}
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {"success": False, "error": f"Image file not found: {image_path}"}
        
        try:
            # Optimize the image
            result = self.image_generator.optimize_for_platform(
                image_path=image_path,
                platform=target_platform
            )
            
            # Save optimized image locally
            if result.get("success", False) and "data" in result:
                image_url = result["data"]
                if image_url and image_url.startswith("http"):
                    try:
                        # Create a filename
                        original_filename = os.path.basename(image_path)
                        filename = f"{target_platform}_optimized_{original_filename}"
                        filepath = os.path.join(self.image_output_dir, filename)
                        
                        # Download the image
                        response = requests.get(image_url)
                        if response.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(response.content)
                            
                            result["local_path"] = filepath
                            logger.info(f"Saved optimized image to {filepath}")
                    except Exception as e:
                        logger.error(f"Error saving optimized image locally: {e}")
            
            return result
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_image_variations(self, image_path: str, variations: int = 3) -> List[Dict]:
        """
        Generate variations of an existing image.
        
        Args:
            image_path: Path to the original image
            variations: Number of variations to generate
            
        Returns:
            List of dictionaries containing the generated image variations
        """
        if not self.image_generator:
            logger.error("No image generator configured")
            return [{"success": False, "error": "No image generator configured"}]
        
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return [{"success": False, "error": f"Image file not found: {image_path}"}]
        
        try:
            # Generate variations
            results = self.image_generator.generate_variations(
                image_path=image_path,
                variations=variations
            )
            
            # Save variations locally
            for i, result in enumerate(results):
                if result.get("success", False) and "data" in result:
                    image_url = result["data"]
                    if image_url and image_url.startswith("http"):
                        try:
                            # Create a filename
                            original_filename = os.path.basename(image_path)
                            base_name, ext = os.path.splitext(original_filename)
                            filename = f"{base_name}_variation_{i+1}{ext}"
                            filepath = os.path.join(self.image_output_dir, filename)
                            
                            # Download the image
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                with open(filepath, "wb") as f:
                                    f.write(response.content)
                                
                                result["local_path"] = filepath
                                logger.info(f"Saved image variation to {filepath}")
                        except Exception as e:
                            logger.error(f"<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>