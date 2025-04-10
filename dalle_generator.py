"""
DALL-E Image Generator implementation.

This module implements the DALL-E-specific functionality for image generation
using the OpenAI API (DALL-E models).
"""

import logging
import json
import os
import requests
import base64
from typing import Dict, List, Optional, Any

from .base_image_generator import BaseImageGenerator

logger = logging.getLogger("llm_integration.dalle_generator")

class DALLEGenerator(BaseImageGenerator):
    """
    DALL-E Image Generator for creating images.
    
    This class implements the BaseImageGenerator interface for OpenAI's DALL-E models.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the DALL-E image generator.
        
        Args:
            config: Configuration dictionary with DALL-E-specific settings
        """
        super().__init__(config)
        self.provider_name = "dalle"
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "dall-e-3")
        self.api_base = self.config.get("api_base", "https://api.openai.com/v1")
        
        logger.info(f"DALL-E Generator initialized with model: {self.model}")
    
    def generate_image(self, prompt: str, size: str = "1024x1024", 
                      style: str = "natural", format: str = "url") -> Dict:
        """
        Generate an image using DALL-E.
        
        Args:
            prompt: Text description of the desired image
            size: Size of the image (e.g., "1024x1024")
            style: Style of the image (e.g., "natural", "vivid")
            format: Output format ("url" or "b64_json")
            
        Returns:
            Dict containing the generated image data
        """
        if not self.validate_api_key():
            return {"success": False, "error": "Invalid API key"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Map style to DALL-E style parameter
            dalle_style = "natural"
            if style.lower() in ["vivid", "artistic"]:
                dalle_style = "vivid"
            
            # Map size to DALL-E size parameter
            dalle_size = "1024x1024"
            if size in ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]:
                dalle_size = size
            
            # Map format to DALL-E response_format parameter
            response_format = "url"
            if format.lower() in ["b64_json", "base64"]:
                response_format = "b64_json"
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "n": 1,
                "size": dalle_size,
                "style": dalle_style,
                "response_format": response_format
            }
            
            response = requests.post(
                f"{self.api_base}/images/generations",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                image_data = result["data"][0]
                
                return {
                    "success": True,
                    "format": response_format,
                    "data": image_data.get("url") if response_format == "url" else image_data.get("b64_json"),
                    "prompt": prompt
                }
            else:
                logger.error(f"DALL-E API error: {response.text}")
                return {
                    "success": False,
                    "error": f"Error {response.status_code}: {response.text}"
                }
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_social_media_image(self, platform: str, topic: str, 
                                   style: str = "professional") -> Dict:
        """
        Generate a social media image for a specific platform using DALL-E.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the image
            style: Style of the image
            
        Returns:
            Dict containing the generated image data
        """
        # Define platform-specific image requirements
        platform_specs = {
            "facebook": {
                "size": "1200x630",
                "description": "Facebook post image with clear focal point and minimal text"
            },
            "twitter": {
                "size": "1200x675",
                "description": "Twitter post image with bold colors and clear subject"
            },
            "instagram": {
                "size": "1080x1080",
                "description": "Instagram square image with vibrant colors and aesthetic composition"
            },
            "tiktok": {
                "size": "1080x1920",
                "description": "TikTok vertical image with attention-grabbing visuals"
            }
        }
        
        # Get platform specifications
        platform_info = platform_specs.get(platform.lower(), {
            "size": "1024x1024",
            "description": "Social media image"
        })
        
        # Create a detailed prompt for the image
        prompt = f"""
        Create a {style} {platform_info['description']} about {topic}.
        The image should be optimized for {platform} and be visually engaging.
        Do not include any text in the image.
        """
        
        # Map platform size to DALL-E supported sizes
        size_mapping = {
            "1200x630": "1024x1024",  # Facebook
            "1200x675": "1024x1024",  # Twitter
            "1080x1080": "1024x1024",  # Instagram
            "1080x1920": "1024x1792"   # TikTok
        }
        
        dalle_size = size_mapping.get(platform_info["size"], "1024x1024")
        
        # Generate the image
        result = self.generate_image(
            prompt=prompt,
            size=dalle_size,
            style=style,
            format="url"
        )
        
        # Add platform-specific metadata
        if result["success"]:
            result["platform"] = platform
            result["topic"] = topic
            result["recommended_size"] = platform_info["size"]
        
        return result
    
    def generate_variations(self, image_path: str, variations: int = 3) -> List[Dict]:
        """
        Generate variations of an existing image using DALL-E.
        
        Args:
            image_path: Path to the original image
            variations: Number of variations to generate
            
        Returns:
            List of dictionaries containing the generated image variations
        """
        if not self.validate_api_key():
            return [{"success": False, "error": "Invalid API key"}]
        
        if not os.path.exists(image_path):
            return [{"success": False, "error": f"Image file not found: {image_path}"}]
        
        try:
            # DALL-E 3 doesn't support direct image variations
            # Instead, we'll analyze the image and create a detailed prompt
            
            # First, let's create a description of the image using GPT-4 Vision
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Request image description from GPT-4 Vision
            vision_data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail so it could be recreated by an image generation AI. Focus on subject, composition, colors, style, and mood."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }
            
            vision_response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=vision_data
            )
            
            if vision_response.status_code != 200:
                logger.error(f"Error getting image description: {vision_response.text}")
                return [{"success": False, "error": f"Error analyzing image: {vision_response.text}"}]
            
            # Extract the image description
            description = vision_response.json()["choices"][0]["message"]["content"]
            
            # Generate variations based on the description
            results = []
            for i in range(variations):
                # Add slight variations to the prompt for each iteration
                variation_prompts = [
                    f"Create a variation of this image: {description}",
                    f"Generate an alternative version of this image: {description}",
                    f"Create a similar image with different details: {description}",
                    f"Reimagine this image with a different perspective: {description}"
                ]
                
                prompt = variation_prompts[i % len(variation_prompts)]
                
                # Generate the variation
                result = self.generate_image(
                    prompt=prompt,
                    size="1024x1024",
                    style="natural",
                    format="url"
                )
                
                result["variation_number"] = i + 1
                result["original_image"] = image_path
                
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error generating image variations with DALL-E: {e}")
            return [{"success": False, "error": str(e)}]
    
    def optimize_for_platform(self, image_path: str, platform: str) -> Dict:
        """
        Optimize an image for a specific platform using DALL-E.
        
        Args:
            image_path: Path to the original image
            platform: Target platform
            
        Returns:
            Dict containing the optimized image data
        """
        if not self.validate_api_key():
            return {"success": False, "error": "Invalid API key"}
        
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}
        
        try:
            # Define platform-specific image requirements
            platform_specs = {
                "facebook": {
                    "size": "1200x630",
                    "description": "optimized for Facebook with clear focal point and minimal text"
                },
                "twitter": {
                    "size": "1200x675",
                    "description": "optimized for Twitter with bold colors and clear subject"
                },
                "instagram": {
                    "size": "1080x1080",
                    "description": "optimized for Instagram with vibrant colors and aesthetic composition"
                },
                "tiktok": {
                    "size": "1080x1920",
                    "description": "optimized for TikTok with attention-grabbing visuals"
                }
            }
            
            # Get platform specifications
            platform_info = platform_specs.get(platform.lower(), {
                "size": "1024x1024",
                "description": f"optimized for {platform}"
            })
            
            # First, analyze the image to get a description
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Request image description from GPT-4 Vision
            vision_data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image briefly focusing on the main subject and style."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
            
            vision_response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=vision_data
            )
            
            if vision_response.status_code != 200:
                logger.error(f"Error getting image description: {vision_response.text}")
                return {"success": False, "error": f"Error analyzing image: {vision_response.text}"}
            
            # Extract the image description
            description = vision_response.json()["choices"][0]["message"]["content"]
            
            # Create a prompt for the optimized image
            prompt = f"Recreate this image {platform_info['description']}: {description}"
            
            # Map platform size to DALL-E supported sizes
            size_mapping = {
                "1200x630": "1024x1024",  # Facebook
                "1200x675": "1024x1024",  # Twitter
                "1080x1080": "1024x1024",  # Instagram
                "1080x1920": "1024x1792"   # TikTok
            }
            
            dalle_size = size_mapping.get(platform_info["size"], "1024x1024")
            
            # Generate the optimized image
            result = self.generate_image(
                prompt=prompt,
                size=dalle_size,
                style="natural",
                format="url"
            )
            
            # Add platform-specific metadata
            if result["success"]:
                result["platform"] = platform
                result["original_image"] = image_path
                result["recommended_size"] = platform_info["size"]
            
            return result
        except Exception as e:
            logger.error(f"Error optimizing image with DALL-E: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_api_key(self) -> bool:
        """
        Validate the DALL-E API key.
        
        Returns:
            bool: Whether the API key is valid
        """
        if not self.api_key:
            logger.error("No DALL-E API key provided")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}/models",
               <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>