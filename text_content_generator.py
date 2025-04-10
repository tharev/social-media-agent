"""
Text Content Generator specialized class.

This module implements specialized functionality for generating text content
for social media platforms, building on the base ContentGenerator.
"""

import logging
import datetime
import random
from typing import Dict, List, Optional, Any

from .content_generator import ContentGenerator
from ..llm_integration.base_text_llm import BaseTextLLM

logger = logging.getLogger("content_generation.text_content_generator")

class TextContentGenerator:
    """
    Text Content Generator for creating text-based social media content.
    
    This class specializes in:
    - Platform-specific text content generation
    - Content templates and formats
    - Content personalization
    - Trending topics integration
    """
    
    def __init__(self, text_llm: BaseTextLLM = None, config: Dict = None):
        """
        Initialize the Text Content Generator.
        
        Args:
            text_llm: Text LLM provider
            config: Configuration dictionary
        """
        self.text_llm = text_llm
        self.config = config or {}
        
        # Content generation settings
        self.default_tone = self.config.get("default_tone", "professional")
        self.default_hashtags = self.config.get("default_hashtags", 3)
        self.default_emojis = self.config.get("default_emojis", True)
        
        # Platform-specific settings
        self.platform_settings = {
            "facebook": {
                "max_length": 5000,
                "optimal_length": 100,
                "hashtags": 2,
                "emojis": True
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": 100,
                "hashtags": 3,
                "emojis": True
            },
            "instagram": {
                "max_length": 2200,
                "optimal_length": 150,
                "hashtags": 10,
                "emojis": True
            },
            "tiktok": {
                "max_length": 150,
                "optimal_length": 80,
                "hashtags": 5,
                "emojis": True
            }
        }
        
        # Content templates
        self.content_templates = {
            "question": "Have you ever wondered about {topic}? {content}",
            "list": "Top {number} things about {topic}: {content}",
            "announcement": "Exciting news! {content} #announcement",
            "tip": "Pro tip: {content} #tip",
            "quote": ""{content}" #quote #inspiration",
            "behind_the_scenes": "Behind the scenes: {content} #behindthescenes",
            "poll": "What do you think about {topic}? {option1} or {option2}? Let us know in the comments!",
            "challenge": "Try this challenge: {content} #challenge",
            "story": "Let me tell you a story about {topic}. {content}",
            "comparison": "{topic1} vs {topic2}: {content}"
        }
        
        # Content history for tracking generated content
        self.content_history = []
        
        logger.info("Text Content Generator initialized")
    
    def generate_content(self, platform: str, topic: str, tone: str = None, 
                        hashtags: int = None, emojis: bool = None, 
                        template: str = None) -> Dict:
        """
        Generate text content for a specific platform.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the content
            tone: Tone of the content
            hashtags: Number of hashtags to include
            emojis: Whether to include emojis
            template: Content template to use
            
        Returns:
            Dict containing the generated content
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return {"success": False, "error": "No text LLM provider configured"}
        
        # Get platform-specific settings
        platform_config = self.platform_settings.get(platform.lower(), {})
        
        # Use platform-specific defaults if not specified
        tone = tone or self.default_tone
        hashtags = hashtags if hashtags is not None else platform_config.get("hashtags", self.default_hashtags)
        emojis = emojis if emojis is not None else platform_config.get("emojis", self.default_emojis)
        
        try:
            # Apply template if specified
            prompt_template = None
            if template and template in self.content_templates:
                prompt_template = self.content_templates[template]
            
            # Generate content using the text LLM
            if prompt_template:
                # Create a template-specific prompt
                template_prompt = f"""
                Create a {tone} social media post for {platform} about {topic}.
                Use this template: "{prompt_template}"
                Include {hashtags} relevant hashtags.
                {"Include appropriate emojis" if emojis else "Do not include emojis"}.
                Keep the content within {platform_config.get("max_length", 1000)} characters.
                Format the response as JSON with 'text' and 'hashtags' fields.
                """
                
                content = self.text_llm.generate_text(template_prompt, max_tokens=500, temperature=0.7)
                
                # Parse the response
                try:
                    # Check if the response is wrapped in ```json and ``` markers
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        json_str = content.split("```")[1].strip()
                    else:
                        json_str = content.strip()
                    
                    import json
                    content_data = json.loads(json_str)
                except Exception as e:
                    logger.error(f"Error parsing generated content as JSON: {e}")
                    content_data = {"text": content, "hashtags": []}
            else:
                # Use standard social media post generation
                content_data = self.text_llm.generate_social_media_post(
                    platform=platform,
                    topic=topic,
                    tone=tone,
                    hashtags=hashtags,
                    emojis=emojis
                )
            
            # Add metadata
            content_data["platform"] = platform
            content_data["topic"] = topic
            content_data["tone"] = tone
            content_data["template"] = template
            content_data["generated_at"] = datetime.datetime.now().isoformat()
            content_data["success"] = True
            
            # Add to history
            self.content_history.append({
                "type": "text",
                "platform": platform,
                "topic": topic,
                "generated_at": content_data["generated_at"],
                "content": content_data
            })
            
            return content_data
        except Exception as e:
            logger.error(f"Error generating text content: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_content_series(self, platform: str, topic: str, count: int = 5, 
                              tone: str = None, hashtags: int = None, 
                              emojis: bool = None) -> List[Dict]:
        """
        Generate a series of related content posts.
        
        Args:
            platform: Target social media platform
            topic: Topic or subject of the content
            count: Number of posts to generate
            tone: Tone of the content
            hashtags: Number of hashtags to include
            emojis: Whether to include emojis
            
        Returns:
            List of generated content posts
        """
        if not self.text_llm:
            logger.error("No text LLM provider configured")
            return [{"success": False, "error": "No text LLM provider configured"}]
        
        try:
            # Create a series prompt
            series_prompt = f"""
            Create a series of {count} related but distinct social media posts for {platform} about {topic}.
            Each post should build on the previous one to tell a cohesive story or cover different aspects of the topic.
            Make each post {tone} in tone.
            Include {hashtags} relevant hashtags in each post.
            {"Include appropriate emojis" if emojis else "Do not include emojis"}.
            Format the response as a JSON array, where each item has 'text' and 'hashtags' fields.
            """
            
            # Generate the series
            response = self.text_llm.generate_text(series_prompt, max_tokens=1000, temperature=0.7)
            
            # Parse the response
            try:
                # Check if the response is wrapped in ```json and ``` markers
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    json_str = response.split("```")[1].strip()
                else:
                    json_str = response.strip()
                
                import json
                series_data = json.loads(json_str)
                
                # Ensure it's a list
                if not isinstance(series_data, list):
                    series_data = [series_data]
                
                # Add metadata to each post
                for i, post in enumerate(series_data):
                    post["platform"] = platform
                    post["topic"] = topic
                    post["tone"] = tone
                    post["series_position"] = i + 1
                    post["series_total"] = len(series_data)
                    post["generated_at"] = datetime.datetime.now().isoformat()
                    post["success"] = True
                    
                    # Add to history
                    self.content_history.append({
                        "type": "text_series",
                        "platform": platform,
                        "topic": topic,
                        "series_position": i + 1,
                        "generated_at": post["generated_at"],
                        "content": post
                    })
                
                return series_data
            except Exception as e:
                logger.error(f"Error parsing generated series as JSON: {e}")
                return [{"success": False, "error": f"Error parsing generated series: {e}"}]
        except Exception as e:
            logger.error(f"Error generating content series: {e}")
            return [{"success": False, "error": str(e)}]
    
    def generate_from_template(self, platform: str, template: str, 
                             template_vars: Dict, tone: str = None) -> Dict:
        """
        Generate content from a specific template.
        
        Args:
            platform: Target social media platform
            template: Template name
            template_vars: Variables to fill in the template
            tone: Tone of the content
            
        Returns:
            Dict containing the generated content
        """
        if template not in self.content_templates:
            logger.error(f"Template not found: {template}")
            return {"success": False, "error": f"Template not found: {template}"}
        
        # Get the template
        template_text = self.content_templates[template]
        
        # Fill in template variables
        try:
            filled_template = template_text.format(**template_vars)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return {"success": False, "error": f"Missing template variable: {e}"}
        
        # Generate content based on the filled template
        return self.generate_content(
            platform=platform,
            topic=template_vars.get("topic", ""),
            tone=tone,
            template=template
        )
    
    def get_random_template(self) -> str:
        """
        Get a random content template.
        
        Returns:
            str: Template name
        """
        return random.choice(list(self.content_templates.keys()))
    
    def add_template(self, name: str, template: str) -> bool:
        """
        Add a new content template.
        
        Args:
            name: Template name
            template: Template text
            
        Returns:
            bool: Success status
        """
        if not name or not template:
            logger.error("Template name and text are required")
            return False
        
        self.content_templates[name] = template
        logger.info(f"Added template: {name}")
        return True
    
    def get_content_history(self, platform: str = None, limit: int = 10) -> List[Dict]:
        """
        Get content generation history.
        
        Args:
            platform: Filter by platform
            limit: Maximum number of items to return
            
        Returns:
            List of content history items
        """
        filtered_history = self.content_history
        
        # Filter by platform
        if platform:
            filtered_history = [item for item in filtered_history if item["platform"] == platform]
        
        # Sort by generation time (newest first)
        filtered_history.sort(key=lambda x: x["generated_at"], reverse=True)
        
        # Limit the number of items
        return filtered_history[:limit]
