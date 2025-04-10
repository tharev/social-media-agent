"""
X (Twitter) Platform Agent implementation.

This module implements the X (Twitter)-specific functionality for posting content,
retrieving metrics, and managing the X social media presence.
"""

import datetime
import logging
import json
import os
import requests
import base64
from typing import Dict, List, Optional, Any
import sys

from .base_agent import BasePlatformAgent

logger = logging.getLogger("platform_agents.twitter")

class TwitterAgent(BasePlatformAgent):
    """
    X (Twitter) Platform Agent for managing Twitter content and analytics.
    
    This agent handles:
    - Authentication with Twitter API v2
    - Posting tweets and media
    - Retrieving engagement and performance metrics
    - Optimizing content for Twitter's algorithm
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Twitter agent.
        
        Args:
            config: Configuration dictionary with Twitter-specific settings
        """
        super().__init__(config)
        self.platform_name = "twitter"
        self.api_base_url = "https://api.twitter.com/2"
        self.api_v1_url = "https://api.twitter.com/1.1"
        self.bearer_token = self.config.get("bearer_token")
        self.api_key = self.config.get("api_key")
        self.api_secret = self.config.get("api_secret")
        self.access_token = self.config.get("access_token")
        self.access_secret = self.config.get("access_secret")
        self.user_id = None
        
        logger.info("Twitter Agent initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Twitter API.
        
        Returns:
            bool: Success status
        """
        if not self.bearer_token:
            logger.error("Twitter bearer token not provided")
            return False
        
        try:
            # Test authentication by getting user info
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base_url}/users/me",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json().get("data", {})
                self.user_id = user_data.get("id")
                logger.info(f"Successfully authenticated with Twitter as user ID: {self.user_id}")
                return True
            else:
                logger.error(f"Twitter authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error authenticating with Twitter: {e}")
            return False
    
    def post_content(self, content_type: str, content: Dict) -> Dict:
        """
        Post content to Twitter.
        
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
            logger.error(f"Error posting to Twitter: {e}")
            return {"success": False, "error": str(e)}
    
    def _post_text(self, content: Dict) -> Dict:
        """
        Post text content to Twitter.
        
        Args:
            content: Text content data
            
        Returns:
            Dict containing post result
        """
        text = content.get("text", "")
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text
        }
        
        # Add reply settings if specified
        if "reply_settings" in content:
            payload["reply_settings"] = content["reply_settings"]
        
        response = requests.post(
            f"{self.api_base_url}/tweets",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            result = response.json().get("data", {})
            tweet_id = result.get("id")
            logger.info(f"Successfully posted tweet, ID: {tweet_id}")
            return {"success": True, "post_id": tweet_id, "platform": "twitter"}
        else:
            logger.error(f"Failed to post tweet: {response.text}")
            return {"success": False, "error": response.text}
    
    def _post_image(self, content: Dict) -> Dict:
        """
        Post image content to Twitter.
        
        Args:
            content: Image content data
            
        Returns:
            Dict containing post result
        """
        text = content.get("text", "")
        image_path = content.get("image_path")
        
        if not image_path:
            return {"success": False, "error": "No image path provided"}
        
        # First, upload the media
        media_id = self._upload_media(image_path)
        if not media_id:
            return {"success": False, "error": "Failed to upload image"}
        
        # Then create the tweet with the media
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "media": {
                "media_ids": [media_id]
            }
        }
        
        response = requests.post(
            f"{self.api_base_url}/tweets",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            result = response.json().get("data", {})
            tweet_id = result.get("id")
            logger.info(f"Successfully posted image tweet, ID: {tweet_id}")
            return {"success": True, "post_id": tweet_id, "platform": "twitter"}
        else:
            logger.error(f"Failed to post image tweet: {response.text}")
            return {"success": False, "error": response.text}
    
    def _post_video(self, content: Dict) -> Dict:
        """
        Post video content to Twitter.
        
        Args:
            content: Video content data
            
        Returns:
            Dict containing post result
        """
        text = content.get("text", "")
        video_path = content.get("video_path")
        
        if not video_path:
            return {"success": False, "error": "No video path provided"}
        
        # First, upload the media
        media_id = self._upload_media(video_path, media_type="video")
        if not media_id:
            return {"success": False, "error": "Failed to upload video"}
        
        # Then create the tweet with the media
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "media": {
                "media_ids": [media_id]
            }
        }
        
        response = requests.post(
            f"{self.api_base_url}/tweets",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            result = response.json().get("data", {})
            tweet_id = result.get("id")
            logger.info(f"Successfully posted video tweet, ID: {tweet_id}")
            return {"success": True, "post_id": tweet_id, "platform": "twitter"}
        else:
            logger.error(f"Failed to post video tweet: {response.text}")
            return {"success": False, "error": response.text}
    
    def _upload_media(self, media_path: str, media_type: str = "image") -> Optional[str]:
        """
        Upload media to Twitter.
        
        Args:
            media_path: Path to the media file
            media_type: Type of media (image, video)
            
        Returns:
            str: Media ID if successful, None otherwise
        """
        if not os.path.exists(media_path):
            logger.error(f"Media file not found: {media_path}")
            return None
        
        # For Twitter API v1.1 media upload, we need OAuth 1.0a
        import oauth2 as oauth
        
        consumer = oauth.Consumer(key=self.api_key, secret=self.api_secret)
        token = oauth.Token(key=self.access_token, secret=self.access_secret)
        client = oauth.Client(consumer, token)
        
        # Determine media category
        category = "tweet_image" if media_type == "image" else "tweet_video"
        
        # INIT phase
        with open(media_path, "rb") as media_file:
            file_size = os.path.getsize(media_path)
            
            init_url = "https://upload.twitter.com/1.1/media/upload.json"
            init_params = {
                "command": "INIT",
                "total_bytes": file_size,
                "media_type": "image/jpeg" if media_type == "image" else "video/mp4",
                "media_category": category
            }
            
            resp, content = client.request(
                init_url + "?" + "&".join([f"{k}={v}" for k, v in init_params.items()]),
                method="POST"
            )
            
            if resp.status != 202:
                logger.error(f"Failed to initialize media upload: {content}")
                return None
            
            init_data = json.loads(content.decode("utf-8"))
            media_id = init_data.get("media_id_string")
            
            # APPEND phase
            chunk_size = 4 * 1024 * 1024  # 4MB chunks
            segment_index = 0
            
            media_file.seek(0)
            while True:
                chunk = media_file.read(chunk_size)
                if not chunk:
                    break
                
                append_url = "https://upload.twitter.com/1.1/media/upload.json"
                append_params = {
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": segment_index
                }
                
                files = {"media": chunk}
                
                resp, content = client.request(
                    append_url + "?" + "&".join([f"{k}={v}" for k, v in append_params.items()]),
                    method="POST",
                    body=chunk,
                    headers={"Content-Type": "application/octet-stream"}
                )
                
                if resp.status != 204:
                    logger.error(f"Failed to append media chunk: {content}")
                    return None
                
                segment_index += 1
            
            # FINALIZE phase
            finalize_url = "https://upload.twitter.com/1.1/media/upload.json"
            finalize_params = {
                "command": "FINALIZE",
                "media_id": media_id
            }
            
            resp, content = client.request(
                finalize_url + "?" + "&".join([f"{k}={v}" for k, v in finalize_params.items()]),
                method="POST"
            )
            
            if resp.status != 201:
                logger.error(f"Failed to finalize media upload: {content}")
                return None
            
            return media_id
    
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
        
        if not self.authenticate() or not self.user_id:
            return {}
        
        try:
            # Get tweets for the date
            start_time = f"{date_str}T00:00:00Z"
            end_time = f"{date_str}T23:59:59Z"
            
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base_url}/users/{self.user_id}/tweets",
                headers=headers,
                params={
                    "start_time": start_time,
                    "end_time": end_time,
                    "max_results": 100,
                    "tweet.fields": "public_metrics,created_at"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get Twitter metrics: {response.text}")
                return {}
            
            tweets_data = response.json()
            tweets = tweets_data.get("data", [])
            
            # Process tweets data
            metrics = {
                "date": date_str,
                "platform": "twitter",
                "posts": len(tweets),
                "engagement": 0,
                "impressions": 0,
                "followers": 0,
                "post_ids": [],
                "hourly_engagement": {}
            }
            
            for tweet in tweets:
                tweet_id = tweet.get("id")
                metrics["post_ids"].append(tweet_id)
                
                # Get public metrics
                public_metrics = tweet.get("public_metrics", {})
                
                # Sum up engagement metrics
                likes = public_metrics.get("like_count", 0)
                retweets = public_metrics.get("retweet_count", 0)
                replies = public_metrics.get("reply_count", 0)
                quotes = public_metrics.get("quote_count", 0)
                
                tweet_engagement = likes + retweets + replies + quotes
                metrics["engagement"] += tweet_engagement
                
                # Track hourly engagement
                created_at = tweet.get("created_at")
                if created_at:
                    hour = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00")).hour
                    if hour not in metrics["hourly_engagement"]:
                        metrics["hourly_engagement"][hour] = 0
                    metrics["hourly_engagement"][hour] += tweet_engagement
            
            # Get follower count
            follower_response = requests.get(
                f"{self.api_base_url}/users/{self.user_id}",
                headers=headers,
                params={
                    "user.fields": "public_metrics"
                }
            )
            
            if follower_response.status_code == 200:
                user_data = follower_response.json().get("data", {})
                public_metrics = user_data.get("public_metrics", {})
                metrics["followers"] = public_metrics.get("followers_count", 0)
            
            # Cache metrics
            self.metrics_cache[date_str] = metrics
            
            return <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>