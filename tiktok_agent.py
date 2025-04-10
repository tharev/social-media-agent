"""
TikTok Platform Agent implementation.

This module implements the TikTok-specific functionality for posting content,
retrieving metrics, and managing the TikTok social media presence.
"""

import datetime
import logging
import json
import os
import requests
from typing import Dict, List, Optional, Any

from .base_agent import BasePlatformAgent

logger = logging.getLogger("platform_agents.tiktok")

class TikTokAgent(BasePlatformAgent):
    """
    TikTok Platform Agent for managing TikTok content and analytics.
    
    This agent handles:
    - Authentication with TikTok API
    - Posting videos to TikTok
    - Retrieving engagement and performance metrics
    - Optimizing content for TikTok's algorithm
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the TikTok agent.
        
        Args:
            config: Configuration dictionary with TikTok-specific settings
        """
        super().__init__(config)
        self.platform_name = "tiktok"
        self.api_base_url = "https://open.tiktokapis.com/v2"
        self.access_token = self.config.get("access_token")
        self.client_key = self.config.get("client_key")
        self.client_secret = self.config.get("client_secret")
        self.open_id = self.config.get("open_id")
        
        logger.info("TikTok Agent initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with the TikTok API.
        
        Returns:
            bool: Success status
        """
        if not self.access_token:
            logger.error("TikTok access token not provided")
            return False
        
        if not self.open_id:
            logger.error("TikTok open ID not provided")
            return False
        
        try:
            # Test authentication by getting user info
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base_url}/user/info/",
                headers=headers,
                params={"fields": "open_id,union_id,avatar_url,display_name"}
            )
            
            if response.status_code == 200:
                user_data = response.json().get("data", {})
                logger.info(f"Successfully authenticated with TikTok as user: {user_data.get('display_name')}")
                return True
            else:
                logger.error(f"TikTok authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error authenticating with TikTok: {e}")
            return False
    
    def refresh_token(self) -> bool:
        """
        Refresh the TikTok access token.
        
        Returns:
            bool: Success status
        """
        if not self.client_key or not self.client_secret:
            logger.error("TikTok client credentials not provided")
            return False
        
        try:
            refresh_token = self.config.get("refresh_token")
            if not refresh_token:
                logger.error("TikTok refresh token not provided")
                return False
            
            data = {
                "client_key": self.client_key,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = requests.post(
                "https://open-api.tiktok.com/oauth/refresh_token/",
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json().get("data", {})
                self.access_token = token_data.get("access_token")
                new_refresh_token = token_data.get("refresh_token")
                
                # Update config with new tokens
                self.config["access_token"] = self.access_token
                self.config["refresh_token"] = new_refresh_token
                
                logger.info("Successfully refreshed TikTok access token")
                return True
            else:
                logger.error(f"Failed to refresh TikTok token: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error refreshing TikTok token: {e}")
            return False
    
    def post_content(self, content_type: str, content: Dict) -> Dict:
        """
        Post content to TikTok.
        
        Args:
            content_type: Type of content (video)
            content: Content data
            
        Returns:
            Dict containing post result information
        """
        if not self.authenticate():
            # Try to refresh token and authenticate again
            if not self.refresh_token() or not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        # Validate content
        validation = self.validate_content(content_type, content)
        if not validation["valid"]:
            return {"success": False, "error": f"Content validation failed: {validation['errors']}"}
        
        # Format and optimize content
        formatted_content = self.format_content(content)
        optimized_content = self.optimize_content(formatted_content)
        
        try:
            if content_type == "video":
                return self._post_video(optimized_content)
            else:
                return {"success": False, "error": f"Unsupported content type: {content_type}"}
        except Exception as e:
            logger.error(f"Error posting to TikTok: {e}")
            return {"success": False, "error": str(e)}
    
    def _post_video(self, content: Dict) -> Dict:
        """
        Post video content to TikTok.
        
        Args:
            content: Video content data
            
        Returns:
            Dict containing post result
        """
        video_path = content.get("video_path")
        caption = content.get("caption", "")
        
        if not video_path:
            return {"success": False, "error": "No video path provided"}
        
        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}"}
        
        # TikTok API requires a multi-step process for video upload
        
        # Step 1: Initialize upload
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        init_data = {
            "post_info": {
                "title": caption,
                "privacy_level": "PUBLIC",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            }
        }
        
        init_response = requests.post(
            f"{self.api_base_url}/video/init/",
            headers=headers,
            json=init_data
        )
        
        if init_response.status_code != 200:
            logger.error(f"Failed to initialize TikTok video upload: {init_response.text}")
            return {"success": False, "error": init_response.text}
        
        init_result = init_response.json().get("data", {})
        upload_url = init_result.get("upload_url")
        publish_id = init_result.get("publish_id")
        
        if not upload_url or not publish_id:
            logger.error("Missing upload URL or publish ID from TikTok")
            return {"success": False, "error": "Missing upload URL or publish ID"}
        
        # Step 2: Upload video
        with open(video_path, "rb") as video_file:
            upload_headers = {
                "Content-Type": "video/mp4"
            }
            
            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=video_file
            )
            
            if upload_response.status_code not in [200, 204]:
                logger.error(f"Failed to upload video to TikTok: {upload_response.text}")
                return {"success": False, "error": upload_response.text}
        
        # Step 3: Publish video
        publish_data = {
            "publish_id": publish_id
        }
        
        publish_response = requests.post(
            f"{self.api_base_url}/video/publish/",
            headers=headers,
            json=publish_data
        )
        
        if publish_response.status_code != 200:
            logger.error(f"Failed to publish video to TikTok: {publish_response.text}")
            return {"success": False, "error": publish_response.text}
        
        publish_result = publish_response.json().get("data", {})
        video_id = publish_result.get("video_id")
        
        logger.info(f"Successfully posted video to TikTok, video ID: {video_id}")
        return {"success": True, "post_id": video_id, "platform": "tiktok"}
    
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
            # Try to refresh token and authenticate again
            if not self.refresh_token() or not self.authenticate():
                return {}
        
        try:
            # Get metrics for the date
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Format date range
            start_date = date.strftime("%Y-%m-%d")
            end_date = (date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Get account metrics
            metrics_response = requests.get(
                f"{self.api_base_url}/research/user/stats/",
                headers=headers,
                params={
                    "fields": "follower_count,follower_count_change,profile_view,profile_view_change,video_view,video_view_change,comment_count,comment_count_change,like_count,like_count_change,share_count,share_count_change",
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if metrics_response.status_code != 200:
                logger.error(f"Failed to get TikTok metrics: {metrics_response.text}")
                return {}
            
            metrics_data = metrics_response.json().get("data", {})
            
            # Get videos posted on the date
            videos_response = requests.get(
                f"{self.api_base_url}/video/list/",
                headers=headers,
                params={
                    "fields": "id,create_time,like_count,comment_count,share_count,view_count,title",
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            videos = []
            post_ids = []
            if videos_response.status_code == 200:
                videos_data = videos_response.json().get("data", {})
                videos = videos_data.get("videos", [])
                post_ids = [video.get("id") for video in videos]
            
            # Process metrics
            metrics = {
                "date": date_str,
                "platform": "tiktok",
                "posts": len(videos),
                "engagement": 0,
                "impressions": metrics_data.get("video_view", 0),
                "followers": metrics_data.get("follower_count", 0),
                "followers_change": metrics_data.get("follower_count_change", 0),
                "profile_views": metrics_data.get("profile_view", 0),
                "likes": metrics_data.get("like_count", 0),
                "comments": metrics_data.get("comment_count", 0),
                "shares": metrics_data.get("share_count", 0),
                "post_ids": post_ids,
                "hourly_engagement": {}
            }
            
            # Calculate total engagement from likes, comments, and shares
            metrics["engagement"] = metrics["likes"] + metrics["comments"] + metrics["shares"]
            
            # Process hourly engagement if available
            for video in videos:
                create_time = video.get("create_time")
                if create_time:
                    try:
                        dt = datetime.datetime.fromisoformat(create_time.replace("Z", "+00:00"))
                        hour = dt.hour
                        
                        # Calculate video engagement
                        video_likes = video.get("like_count", 0)
                        video_comments = video.get("comment_count", 0)
                        video_shares = video.get("share_count", 0)
                        video_engagement = video_likes + video_comments + video_shares
                        
                        if hour not in metrics["hourly_engagement"]:
                            metrics["hourly_engagement"][hour] = 0
                        
                        metrics["hourly_engagement"][hour] += video_engagement
                    except Exception as e:
                        logger.error(f"Error parsing video timestamp: {e}")
            
            # Cache metrics
            self.metrics_cache[date_str] = metrics
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting TikTok metrics: {e}")
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
            # Try to refresh token and authenticate again
            if not self.refresh_token() or not self.authenticate():
                return {}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base_url}/video/query/",
                headers=headers,
                params={
                    "fields": "id,create_time,like_count,comment_count,share_count,view_count,title",
                    "filters": json.dumps({"video_ids": [post_id]})
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get TikTok post metrics: {response.text}")
                return {}
            
            videos_data = response.json().get("data", {})
            videos = videos_data.get("videos", [])
            
            if not videos:
                logger.error(f"No video found with ID: {post_id}")
                return {}
            
            video = videos[0]
            
            # Process metrics
            metrics = {
                "post_id": post_id,
                "platform": "tiktok",
                "engagement": 0,
                "views": video.get("view_count", 0),
                "likes": video.get("like_count", 0),
                "comments": video.get("comment_count", 0),
                "shares": video.get("share_count", 0),
                "title": video.get("title", ""),
                "created_at": video.get("create_time", "")
            }
            
            # Calculate total engagement
            metrics["engagement"] = metri<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>