"""
OpenAI LLM Provider implementation for text generation.

This module implements the OpenAI-specific functionality for text generation
using the OpenAI API (GPT models).
"""

import logging
import json
import os
import requests
from typing import Dict, List, Optional, Any

from .base_text_llm import BaseTextLLM

logger = logging.getLogger("llm_integration.openai_llm")

class OpenAILLM(BaseTextLLM):
    """
    OpenAI LLM Provider for text generation.
    
    This class implements the BaseTextLLM interface for OpenAI's GPT models.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the OpenAI LLM provider.
        
        Args:
            config: Configuration dictionary with OpenAI-specific settings
        """
        super().__init__(config)
        self.provider_name = "openai"
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "gpt-4")
        self.api_base = self.config.get("api_base", "https://api.openai.com/v1")
        
        logger.info(f"OpenAI LLM initialized with model: {self.model}")
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Generate text using OpenAI's GPT models.
        
        Args:
            prompt: Input prompt for text generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)
            
        Returns:
            str: Generated text
        """
        if not self.validate_api_key():
            return "Error: Invalid API key"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"].strip()
                return generated_text
            else:
                logger.error(f"OpenAI API error: {response.text}")
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            return f"Error: {str(e)}"
    
    def generate_social_media_post(self, platform: str, topic: str, tone: str = "professional", 
                                  hashtags: int = 3, emojis: bool = True) -> Dict:
        """
        Generate a social media post for a specific platform using OpenAI.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the post
            tone: Tone of the post (professional, casual, humorous, etc.)
            hashtags: Number of hashtags to include
            emojis: Whether to include emojis
            
        Returns:
            Dict containing the generated post content
        """
        # Create a platform-specific prompt
        emoji_instruction = "Include appropriate emojis" if emojis else "Do not include emojis"
        
        platform_specifics = {
            "facebook": "longer form content with engaging questions",
            "twitter": "concise content under 280 characters",
            "instagram": "visually descriptive content with multiple hashtags",
            "tiktok": "trendy, attention-grabbing content with popular hashtags"
        }
        
        platform_specific = platform_specifics.get(platform.lower(), "")
        
        prompt = f"""
        Create a {tone} social media post for {platform} about {topic}.
        {platform_specific}
        Include {hashtags} relevant hashtags.
        {emoji_instruction}.
        Format the response as JSON with 'text' and 'hashtags' fields.
        """
        
        # Generate the post
        response = self.generate_text(prompt, max_tokens=300, temperature=0.7)
        
        # Parse the response as JSON
        try:
            # Check if the response is wrapped in ```json and ``` markers
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            post_data = json.loads(json_str)
            
            # Ensure required fields are present
            if "text" not in post_data:
                post_data["text"] = response
            
            if "hashtags" not in post_data:
                # Extract hashtags from text
                words = post_data["text"].split()
                post_data["hashtags"] = [word for word in words if word.startswith("#")]
            
            return post_data
        except Exception as e:
            logger.error(f"Error parsing generated post as JSON: {e}")
            
            # Return a structured response even if JSON parsing fails
            return {
                "text": response,
                "hashtags": []
            }
    
    def generate_content_variations(self, content: str, variations: int = 3) -> List[str]:
        """
        Generate variations of existing content using OpenAI.
        
        Args:
            content: Original content
            variations: Number of variations to generate
            
        Returns:
            List of content variations
        """
        prompt = f"""
        Create {variations} different variations of the following content while maintaining the same message and tone:
        
        "{content}"
        
        Format the response as a JSON array of strings, with each string being a variation.
        """
        
        # Generate variations
        response = self.generate_text(prompt, max_tokens=1000, temperature=0.8)
        
        # Parse the response as JSON
        try:
            # Check if the response is wrapped in ```json and ``` markers
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            variations_list = json.loads(json_str)
            
            # Ensure we have the requested number of variations
            while len(variations_list) < variations:
                variations_list.append(content)
            
            return variations_list[:variations]
        except Exception as e:
            logger.error(f"Error parsing generated variations as JSON: {e}")
            
            # Return a list with the original content if parsing fails
            return [content] * variations
    
    def optimize_for_platform(self, content: str, platform: str) -> str:
        """
        Optimize content for a specific platform using OpenAI.
        
        Args:
            content: Original content
            platform: Target platform
            
        Returns:
            str: Optimized content
        """
        platform_specifics = {
            "facebook": "longer form content with engaging questions, 1-2 hashtags maximum",
            "twitter": "concise content under 280 characters, 2-3 relevant hashtags",
            "instagram": "visually descriptive content with 5-10 relevant hashtags at the end",
            "tiktok": "trendy, attention-grabbing content with popular hashtags like #fyp, #foryou"
        }
        
        platform_specific = platform_specifics.get(platform.lower(), "")
        
        prompt = f"""
        Optimize the following content for {platform}. {platform_specific}
        
        Original content: "{content}"
        
        Return only the optimized content without any explanations or additional text.
        """
        
        # Generate optimized content
        optimized = self.generate_text(prompt, max_tokens=500, temperature=0.4)
        
        # Remove any quotation marks that might be included
        optimized = optimized.strip('"\'')
        
        return optimized
    
    def validate_api_key(self) -> bool:
        """
        Validate the OpenAI API key.
        
        Returns:
            bool: Whether the API key is valid
        """
        if not self.api_key:
            logger.error("No OpenAI API key provided")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}/models",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("OpenAI API key is valid")
                return True
            else:
                logger.error(f"Invalid OpenAI API key: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error validating OpenAI API key: {e}")
            return False
