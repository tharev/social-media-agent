"""
Instagram Platform Agent implementation.

This module implements the Instagram-specific functionality for posting content,
retrieving metrics, and managing the Instagram social media presence.
"""

import datetime
import logging
import json
import os
import requests
from typing import Dict, List, Optional, Any

from .base_agent import BasePlatformAgent

logger = logging.getLogger("platform_agents.instagram")

class InstagramAgent(BasePlatformAgent):
    """
    Instagram Platform Agent for managing Instagram content and analytics.
    
    This agent handles:
    - Authentication with Instagram Graph API
    - Posting photos, videos, and stories
    - Retrieving engagement and performance metrics
    - Optimizing content for Instagram's algorithm
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Instagram agent.
        
        Args:
            config: Configuration dictionary with Instagram-specific settings
        """
        super().__init__(config)
        self.platform_name = "instagram"
        self.api_base_url = "https://graph.facebook.com/v18.0"
        self.access_token = self.config.get("access_token")
        self.instagram_account_id = self.config.get("instagram_account_id")
        
        logger.info("Instagram Agent initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Instagram Graph API.
        
        Returns:
            bool: Success status
        """
        if not self.access_token:
            logger.error("Instagram access token not provided")
            return False
        
        if not self.instagram_account_id:
            logger.error("Instagram account ID not provided")
            return False
        
        try:
            # Test authentication by getting account info
            response = requests.get(
                f"{self.api_base_url}/{self.instagram_account_id}",
                params={"access_token": self.access_token, "fields": "name,username"}
            )
            
            if response.status_code == 200:
                account_info = response.json()
                logger.info(f"Successfully authenticated with Instagram account: {account_info.get('username')}")
                return True
            else:
                logger.error(f"Instagram authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error authenticating with Instagram: {e}")
            return False
    
    def post_content(self, content_type: str, content: Dict) -> Dict:
        """
        Post content to Instagram.
        
        Args:
            content_type: Type of content (image, video, carousel, story)
            content: Content data
            
        Returns:
            Dict containing post result information
        """
        if not self.authenticate():
            return {"success": False, "error": "Authentication failed"}
        
        # Validate content
        validation = self.validate_content(content_type, content)
        if not validation["valid"]:
            return {"success": False, "error": f"Content validation failed: {validation['errors']}"}
        
        # Format and optimize content
        formatted_content = self.format_content(content)
        optimized_content = self.optimize_content(formatted_content)
        
        try:
            if content_type == "image":
                return self._post_image(optimized_content)
            elif content_type == "video":
                return self._post_video(optimized_content)
            elif content_type == "carousel":
                return self._post_carousel(optimized_content)
            elif content_type == "story":
                return self._post_story(optimized_content)
            else:
                return {"success": False, "error": f"Unsupported content type: {content_type}"}
        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
            return {"success": False, "error": str(e)}
    
    def _post_image(self, content: Dict) -> Dict:
        """
        Post image content to Instagram.
        
        Args:
            content: Image content data
            
        Returns:
            Dict containing post result
        """
        caption = content.get("caption", "")
        image_url = content.get("image_url")
        image_path = content.get("image_path")
        
        if not image_url and not image_path:
            return {"success": False, "error": "No image URL or path provided"}
        
        # Step 1: Create a container
        container_params = {
            "access_token": self.access_token,
            "caption": caption,
            "image_url": image_url
        }
        
        # If using local image, upload it first
        if not image_url and image_path:
            if not os.path.exists(image_path):
                return {"success": False, "error": f"Image file not found: {image_path}"}
            
            # Upload image to Facebook/Instagram servers
            with open(image_path, "rb") as image_file:
                files = {"source": image_file}
                upload_params = {
                    "access_token": self.access_token,
                    "published": "false"
                }
                
                upload_response = requests.post(
                    f"{self.api_base_url}/{self.instagram_account_id}/media",
                    params=upload_params,
                    files=files
                )
                
                if upload_response.status_code != 200:
                    logger.error(f"Failed to upload image to Instagram: {upload_response.text}")
                    return {"success": False, "error": upload_response.text}
                
                upload_result = upload_response.json()
                creation_id = upload_result.get("id")
                
                # Use creation ID for publishing
                publish_params = {
                    "access_token": self.access_token,
                    "creation_id": creation_id
                }
                
                publish_response = requests.post(
                    f"{self.api_base_url}/{self.instagram_account_id}/media_publish",
                    params=publish_params
                )
                
                if publish_response.status_code == 200:
                    result = publish_response.json()
                    post_id = result.get("id")
                    logger.info(f"Successfully posted image to Instagram, post ID: {post_id}")
                    return {"success": True, "post_id": post_id, "platform": "instagram"}
                else:
                    logger.error(f"Failed to publish image to Instagram: {publish_response.text}")
                    return {"success": False, "error": publish_response.text}
        else:
            # Using image URL
            container_response = requests.post(
                f"{self.api_base_url}/{self.instagram_account_id}/media",
                params=container_params
            )
            
            if container_response.status_code != 200:
                logger.error(f"Failed to create Instagram container: {container_response.text}")
                return {"success": False, "error": container_response.text}
            
            container_result = container_response.json()
            creation_id = container_result.get("id")
            
            # Step 2: Publish the container
            publish_params = {
                "access_token": self.access_token,
                "creation_id": creation_id
            }
            
            publish_response = requests.post(
                f"{self.api_base_url}/{self.instagram_account_id}/media_publish",
                params=publish_params
            )
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get("id")
                logger.info(f"Successfully posted image to Instagram, post ID: {post_id}")
                return {"success": True, "post_id": post_id, "platform": "instagram"}
            else:
                logger.error(f"Failed to publish image to Instagram: {publish_response.text}")
                return {"success": False, "error": publish_response.text}
    
    def _post_video(self, content: Dict) -> Dict:
        """
        Post video content to Instagram.
        
        Args:
            content: Video content data
            
        Returns:
            Dict containing post result
        """
        caption = content.get("caption", "")
        video_url = content.get("video_url")
        video_path = content.get("video_path")
        thumbnail_url = content.get("thumbnail_url")
        thumbnail_path = content.get("thumbnail_path")
        
        if not video_url and not video_path:
            return {"success": False, "error": "No video URL or path provided"}
        
        # Step 1: Create a container
        container_params = {
            "access_token": self.access_token,
            "caption": caption,
            "media_type": "VIDEO"
        }
        
        if video_url:
            container_params["video_url"] = video_url
            
            # Add thumbnail if provided
            if thumbnail_url:
                container_params["thumbnail_url"] = thumbnail_url
            
            container_response = requests.post(
                f"{self.api_base_url}/{self.instagram_account_id}/media",
                params=container_params
            )
            
            if container_response.status_code != 200:
                logger.error(f"Failed to create Instagram video container: {container_response.text}")
                return {"success": False, "error": container_response.text}
            
            container_result = container_response.json()
            creation_id = container_result.get("id")
            
            # Step 2: Publish the container
            publish_params = {
                "access_token": self.access_token,
                "creation_id": creation_id
            }
            
            publish_response = requests.post(
                f"{self.api_base_url}/{self.instagram_account_id}/media_publish",
                params=publish_params
            )
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get("id")
                logger.info(f"Successfully posted video to Instagram, post ID: {post_id}")
                return {"success": True, "post_id": post_id, "platform": "instagram"}
            else:
                logger.error(f"Failed to publish video to Instagram: {publish_response.text}")
                return {"success": False, "error": publish_response.text}
        else:
            # Using local video file
            if not os.path.exists(video_path):
                return {"success": False, "error": f"Video file not found: {video_path}"}
            
            # Upload video to Facebook/Instagram servers
            with open(video_path, "rb") as video_file:
                files = {"source": video_file}
                upload_params = {
                    "access_token": self.access_token,
                    "media_type": "VIDEO",
                    "caption": caption,
                    "published": "false"
                }
                
                # Add thumbnail if provided
                if thumbnail_path and os.path.exists(thumbnail_path):
                    with open(thumbnail_path, "rb") as thumb_file:
                        files["thumb"] = thumb_file
                
                upload_response = requests.post(
                    f"{self.api_base_url}/{self.instagram_account_id}/media",
                    params=upload_params,
                    files=files
                )
                
                if upload_response.status_code != 200:
                    logger.error(f"Failed to upload video to Instagram: {upload_response.text}")
                    return {"success": False, "error": upload_response.text}
                
                upload_result = upload_response.json()
                creation_id = upload_result.get("id")
                
                # Use creation ID for publishing
                publish_params = {
                    "access_token": self.access_token,
                    "creation_id": creation_id
                }
                
                publish_response = requests.post(
                    f"{self.api_base_url}/{self.instagram_account_id}/media_publish",
                    params=publish_params
                )
                
                if publish_response.status_code == 200:
                    result = publish_response.json()
                    post_id = result.get("id")
                    logger.info(f"Successfully posted video to Instagram, post ID: {post_id}")
                    return {"success": True, "post_id": post_id, "platform": "instagram"}
                else:
                    logger.error(f"Failed to publish video to Instagram: {publish_response.text}")
                    return {"success": False, "error": publish_response.text}
    
    def _post_carousel(self, content: Dict) -> Dict:
        """
        Post carousel content to Instagram.
        
        Args:
            content: Carousel content data
            
        Returns:
            Dict containing post result
        """
        caption = content.get("caption", "")
        media_items = content.get("media", [])
        
        if not media_items:
            return {"success": False, "error": "No media items provided for carousel"}
        
        # Step 1: Create containers for each media item
        children = []
        
        for item in media_items:
            media_type = item.get("type", "image")
            
            if media_type == "image":
                image_url = item.get("url")
                
                if not image_url:
                    logger.error("Missing URL for carousel image item")
                    continue
                
                container_params = {
                    "access_token": self.access_token,
                    "image_url": image_url,
                    "is_carousel_item": "true"
                }
                
                container_response = requests.post(
                    f"{self.api_base_url}/{self.instagram_account_id}/media",
                    params=container_params
                )
                
                if container_response.status_code != 200:
                    logger.error(f"Failed to create carousel image container: {container_response.text}")
                    continue
                
                container_result = container_response.json()
                children.append(container_result.get("id"))
            
            elif media_type == "video":
                video_url = item.get("url")
                thumbnail_url = item.get("thumbnail_url")
                
                if not video_url:
                    logger.error("Missing URL for carousel video item")
                    continue
                
                container_params = {
                    "access_token": self.access_token,
                    "media_type": "VIDEO",
                    "video_url": video_url,
                    "is_carousel_item": "true"
                }
                
                if thumbnail_url:
                    container_params["thumbnail_url"] = thumbnail_url
                
                container_response = requests.post(
                    f"{self.api_base_url}/{self.instagram_account_id}/media",
                    params=container_params
 <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>