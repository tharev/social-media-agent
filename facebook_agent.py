"""
Facebook Platform Agent implementation.

This module implements the Facebook-specific functionality for posting content,
retrieving metrics, and managing the Facebook social media presence.
"""

import datetime
import logging
import json
import os
import requests
from typing import Dict, List, Optional, Any

from .base_agent import BasePlatformAgent

logger = logging.getLogger("platform_agents.facebook")

class FacebookAgent(BasePlatformAgent):
    """
    Facebook Platform Agent for managing Facebook page content and analytics.
    
    This agent handles:
    - Authentication with Facebook Graph API
    - Posting content to Facebook pages
    - Retrieving engagement and performance metrics
    - Optimizing content for Facebook's algorithm
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Facebook agent.
        
        Args:
            config: Configuration dictionary with Facebook-specific settings
        """
        super().__init__(config)
        self.platform_name = "facebook"
        self.api_base_url = "https://graph.facebook.com/v18.0"
        self.access_token = self.config.get("access_token")
        self.page_id = self.config.get("page_id")
        
        logger.info("Facebook Agent initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Facebook Graph API.
        
        Returns:
            bool: Success status
        """
        if not self.access_token:
            logger.error("Facebook access token not provided")
            return False
        
        if not self.page_id:
            logger.error("Facebook page ID not provided")
            return False
        
        try:
            # Test authentication by getting page info
            response = requests.get(
                f"{self.api_base_url}/{self.page_id}",
                params={"access_token": self.access_token, "fields": "name,id"}
            )
            
            if response.status_code == 200:
                page_info = response.json()
                logger.info(f"Successfully authenticated with Facebook page: {page_info.get('name')}")
                return True
            else:
                logger.error(f"Facebook authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error authenticating with Facebook: {e}")
            return False
    
    def post_content(self, content_type: str, content: Dict) -> Dict:
        """
        Post content to Facebook.
        
        Args:
            content_type: Type of content (text, image, video)
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
            if content_type == "text":
                return self._post_text(optimized_content)
            elif content_type == "image":
                return self._post_image(optimized_content)
            elif content_type == "video":
                return self._post_video(optimized_content)
            else:
                return {"success": False, "error": f"Unsupported content type: {content_type}"}
        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
            return {"success": False, "error": str(e)}
    
    def _post_text(self, content: Dict) -> Dict:
        """
        Post text content to Facebook.
        
        Args:
            content: Text content data
            
        Returns:
            Dict containing post result
        """
        message = content.get("text", "")
        link = content.get("link")
        
        params = {
            "access_token": self.access_token,
            "message": message
        }
        
        # Add link if provided
        if link:
            params["link"] = link
        
        response = requests.post(
            f"{self.api_base_url}/{self.page_id}/feed",
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get("id")
            logger.info(f"Successfully posted text to Facebook, post ID: {post_id}")
            return {"success": True, "post_id": post_id, "platform": "facebook"}
        else:
            logger.error(f"Failed to post text to Facebook: {response.text}")
            return {"success": False, "error": response.text}
    
    def _post_image(self, content: Dict) -> Dict:
        """
        Post image content to Facebook.
        
        Args:
            content: Image content data
            
        Returns:
            Dict containing post result
        """
        message = content.get("text", "")
        image_url = content.get("image_url")
        image_path = content.get("image_path")
        
        if not image_url and not image_path:
            return {"success": False, "error": "No image URL or path provided"}
        
        if image_url:
            # Post image from URL
            params = {
                "access_token": self.access_token,
                "message": message,
                "url": image_url
            }
            
            response = requests.post(
                f"{self.api_base_url}/{self.page_id}/photos",
                params=params
            )
        else:
            # Post image from file
            with open(image_path, "rb") as image_file:
                files = {"source": image_file}
                params = {
                    "access_token": self.access_token,
                    "message": message
                }
                
                response = requests.post(
                    f"{self.api_base_url}/{self.page_id}/photos",
                    params=params,
                    files=files
                )
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get("id")
            logger.info(f"Successfully posted image to Facebook, post ID: {post_id}")
            return {"success": True, "post_id": post_id, "platform": "facebook"}
        else:
            logger.error(f"Failed to post image to Facebook: {response.text}")
            return {"success": False, "error": response.text}
    
    def _post_video(self, content: Dict) -> Dict:
        """
        Post video content to Facebook.
        
        Args:
            content: Video content data
            
        Returns:
            Dict containing post result
        """
        message = content.get("text", "")
        video_url = content.get("video_url")
        video_path = content.get("video_path")
        title = content.get("title", "")
        description = content.get("description", "")
        
        if not video_url and not video_path:
            return {"success": False, "error": "No video URL or path provided"}
        
        if video_url:
            # Post video from URL
            params = {
                "access_token": self.access_token,
                "file_url": video_url,
                "description": message,
                "title": title
            }
            
            response = requests.post(
                f"{self.api_base_url}/{self.page_id}/videos",
                params=params
            )
        else:
            # Post video from file
            with open(video_path, "rb") as video_file:
                files = {"source": video_file}
                params = {
                    "access_token": self.access_token,
                    "description": message,
                    "title": title
                }
                
                response = requests.post(
                    f"{self.api_base_url}/{self.page_id}/videos",
                    params=params,
                    files=files
                )
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get("id")
            logger.info(f"Successfully posted video to Facebook, post ID: {post_id}")
            return {"success": True, "post_id": post_id, "platform": "facebook"}
        else:
            logger.error(f"Failed to post video to Facebook: {response.text}")
            return {"success": False, "error": response.text}
    
    def get_metrics(self, date: datetime.date) -> Dict:
        """
        Get metrics for a specific date.
        
        Args:
            date: Date to get metrics for
            
        Returns:
            Dict containing metrics
        """
        date_str = date.strftime("%Y-%m-%d")
        
        # Check cache first
        if date_str in self.metrics_cache:
            return self.metrics_cache[date_str]
        
        if not self.authenticate():
            return {}
        
        try:
            # Get page insights for the date
            since = int(datetime.datetime.combine(date, datetime.time.min).timestamp())
            until = int(datetime.datetime.combine(date, datetime.time.max).timestamp())
            
            # Get page impressions
            response = requests.get(
                f"{self.api_base_url}/{self.page_id}/insights",
                params={
                    "access_token": self.access_token,
                    "metric": "page_impressions,page_engaged_users,page_post_engagements,page_fans",
                    "period": "day",
                    "since": since,
                    "until": until
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get Facebook metrics: {response.text}")
                return {}
            
            insights = response.json().get("data", [])
            
            # Process insights data
            metrics = {
                "date": date_str,
                "platform": "facebook",
                "posts": 0,
                "engagement": 0,
                "impressions": 0,
                "followers": 0,
                "hourly_engagement": {}
            }
            
            for insight in insights:
                metric_name = insight.get("name")
                values = insight.get("values", [])
                
                if not values:
                    continue
                
                value = values[0].get("value", 0)
                
                if metric_name == "page_impressions":
                    metrics["impressions"] = value
                elif metric_name == "page_engaged_users":
                    metrics["engagement"] = value
                elif metric_name == "page_fans":
                    metrics["followers"] = value
            
            # Get posts for the date
            posts_response = requests.get(
                f"{self.api_base_url}/{self.page_id}/posts",
                params={
                    "access_token": self.access_token,
                    "fields": "id,created_time",
                    "since": since,
                    "until": until
                }
            )
            
            if posts_response.status_code == 200:
                posts = posts_response.json().get("data", [])
                metrics["posts"] = len(posts)
                
                # Get post IDs for the date
                post_ids = [post.get("id") for post in posts]
                metrics["post_ids"] = post_ids
            
            # Cache metrics
            self.metrics_cache[date_str] = metrics
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting Facebook metrics: {e}")
            return {}
    
    def get_post_metrics(self, post_id: str) -> Dict:
        """
        Get metrics for a specific post.
        
        Args:
            post_id: ID of the post
            
        Returns:
            Dict containing post metrics
        """
        if not self.authenticate():
            return {}
        
        try:
            # Get post insights
            response = requests.get(
                f"{self.api_base_url}/{post_id}/insights",
                params={
                    "access_token": self.access_token,
                    "metric": "post_impressions,post_engagements,post_reactions_by_type_total"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get Facebook post metrics: {response.text}")
                return {}
            
            insights = response.json().get("data", [])
            
            # Process insights data
            metrics = {
                "post_id": post_id,
                "platform": "facebook",
                "engagement": 0,
                "impressions": 0,
                "reactions": {
                    "like": 0,
                    "love": 0,
                    "wow": 0,
                    "haha": 0,
                    "sad": 0,
                    "angry": 0
                },
                "shares": 0,
                "comments": 0
            }
            
            for insight in insights:
                metric_name = insight.get("name")
                values = insight.get("values", [])
                
                if not values:
                    continue
                
                value = values[0].get("value", 0)
                
                if metric_name == "post_impressions":
                    metrics["impressions"] = value
                elif metric_name == "post_engagements":
                    metrics["engagement"] = value
                elif metric_name == "post_reactions_by_type_total":
                    if isinstance(value, dict):
                        metrics["reactions"] = {
                            "like": value.get("like", 0),
                            "love": value.get("love", 0),
                            "wow": value.get("wow", 0),
                            "haha": value.get("haha", 0),
                            "sad": value.get("sad", 0),
                            "angry": value.get("angry", 0)
                        }
            
            # Get comments and shares
            response = requests.get(
                f"{self.api_base_url}/{post_id}",
                params={
                    "access_token": self.access_token,
                    "fields": "shares,comments.summary(true)"
                }
            )
            
            if response.status_code == 200:
                post_data = response.json()
                
                # Get shares count
                shares = post_data.get("shares", {})
                metrics["shares"] = shares.get("count", 0)
                
                # Get comments count
                comments = post_data.get("comments", {}).get("summary", {})
                metrics["comments"] = comments.get("total_count", 0)
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting Facebook post metrics: {e}")
            return {}
    
    def format_content(self, content: Dict) -> Dict:
        """
        Format content for Facebook.
        
        Args:
            content: Generic content data
            
        Returns:
            Dict containing Facebook-specific formatted content
        """
        formatted_content = content.copy()
        
        # F<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>