"""
Scheduler component for the Team Leader Agent.

This module implements the scheduling functionality for content posting
across different social media platforms.
"""

import datetime
import logging
from typing import Dict, List, Optional, Any
import json
import os
import heapq

logger = logging.getLogger("team_leader.scheduler")

class ContentScheduler:
    """
    Scheduler for managing content posting across social media platforms.
    
    The ContentScheduler is responsible for:
    - Creating optimal posting schedules based on platform analytics
    - Managing the content calendar
    - Triggering content posting at scheduled times
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the ContentScheduler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.content_calendar = {}
        self.scheduled_queue = []  # Priority queue for scheduled content
        self.optimal_times = self._load_optimal_times()
        
        logger.info("ContentScheduler initialized")
    
    def _load_optimal_times(self) -> Dict:
        """
        Load optimal posting times for each platform.
        
        Returns:
            Dict containing optimal posting times
        """
        # Default optimal times based on general social media best practices
        default_times = {
            "facebook": ["09:00", "15:00", "19:00"],
            "twitter": ["08:00", "12:00", "15:00", "17:00", "20:00"],
            "instagram": ["11:00", "17:00", "21:00"],
            "tiktok": ["12:00", "19:00", "21:00"]
        }
        
        # Try to load from config if available
        optimal_times = self.config.get("optimal_posting_times", default_times)
        
        logger.info("Loaded optimal posting times")
        return optimal_times
    
    def create_schedule(self, start_date: datetime.date, days: int = 7) -> Dict:
        """
        Create a content posting schedule for the specified period.
        
        Args:
            start_date: Start date for the schedule
            days: Number of days to schedule
            
        Returns:
            Dict containing the content schedule
        """
        schedule = {}
        platforms = self.config.get("platforms", ["facebook", "twitter", "instagram", "tiktok"])
        
        current_date = start_date
        for _ in range(days):
            date_str = current_date.strftime("%Y-%m-%d")
            schedule[date_str] = {}
            
            for platform in platforms:
                posts_per_day = self.config.get("posts_per_day", {}).get(platform, 1)
                optimal_times = self.optimal_times.get(platform, ["12:00"])
                
                # Ensure we have enough time slots
                while len(optimal_times) < posts_per_day:
                    optimal_times.append("12:00")  # Default to noon if not enough optimal times
                
                # Select the best times for this platform based on posts_per_day
                selected_times = optimal_times[:posts_per_day]
                
                schedule[date_str][platform] = []
                for i, time_str in enumerate(selected_times):
                    # Create a datetime object for the scheduled time
                    hour, minute = map(int, time_str.split(":"))
                    scheduled_time = datetime.datetime.combine(
                        current_date, 
                        datetime.time(hour, minute)
                    )
                    
                    # Create content slot
                    content_slot = {
                        "id": f"{date_str}_{platform}_{i}",
                        "platform": platform,
                        "content_type": None,
                        "content": None,
                        "status": "planned",
                        "scheduled_time": scheduled_time.isoformat()
                    }
                    
                    schedule[date_str][platform].append(content_slot)
                    
                    # Add to priority queue
                    heapq.heappush(
                        self.scheduled_queue, 
                        (scheduled_time.timestamp(), content_slot["id"])
                    )
            
            current_date += datetime.timedelta(days=1)
        
        self.content_calendar.update(schedule)
        logger.info(f"Created content schedule from {start_date} for {days} days")
        return schedule
    
    def optimize_schedule(self, platform_metrics: Dict) -> None:
        """
        Optimize posting schedule based on platform metrics.
        
        Args:
            platform_metrics: Dictionary of platform metrics
        """
        # For each platform, analyze when engagement is highest
        for platform, metrics in platform_metrics.items():
            if platform not in self.optimal_times:
                continue
                
            # Extract hourly engagement data if available
            hourly_engagement = {}
            
            for date, daily_metrics in metrics.items():
                if "hourly_engagement" in daily_metrics:
                    for hour, engagement in daily_metrics["hourly_engagement"].items():
                        hour_int = int(hour)
                        if hour_int not in hourly_engagement:
                            hourly_engagement[hour_int] = 0
                        hourly_engagement[hour_int] += engagement
            
            # If we have enough data, update optimal times
            if hourly_engagement:
                # Sort hours by engagement
                sorted_hours = sorted(
                    hourly_engagement.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                # Take top hours based on posts_per_day
                posts_per_day = self.config.get("posts_per_day", {}).get(platform, 1)
                top_hours = sorted_hours[:posts_per_day]
                
                # Format as time strings
                new_optimal_times = [
                    f"{hour:02d}:00" for hour, _ in top_hours
                ]
                
                # Update optimal times
                self.optimal_times[platform] = new_optimal_times
                logger.info(f"Updated optimal posting times for {platform}: {new_optimal_times}")
    
    def get_next_scheduled_content(self) -> Optional[Dict]:
        """
        Get the next content that needs to be posted.
        
        Returns:
            Dict containing content information or None if no content is scheduled
        """
        now = datetime.datetime.now().timestamp()
        
        while self.scheduled_queue:
            # Peek at the next scheduled content
            scheduled_time, content_id = self.scheduled_queue[0]
            
            # If it's time to post, return the content
            if scheduled_time <= now:
                # Remove from queue
                heapq.heappop(self.scheduled_queue)
                
                # Find the content in the calendar
                content = self._find_content_by_id(content_id)
                if content and content["status"] == "scheduled":
                    return content
            else:
                # Not time to post yet
                break
        
        return None
    
    def _find_content_by_id(self, content_id: str) -> Optional[Dict]:
        """
        Find content in the calendar by ID.
        
        Args:
            content_id: ID of the content to find
            
        Returns:
            Dict containing content information or None if not found
        """
        for date, platforms in self.content_calendar.items():
            for platform, posts in platforms.items():
                for post in posts:
                    if post["id"] == content_id:
                        return post
        
        return None
    
    def schedule_content(self, content_id: str, content_type: str, content: Dict) -> bool:
        """
        Schedule content for posting.
        
        Args:
            content_id: ID of the content slot
            content_type: Type of content (text, image, video)
            content: Content data
            
        Returns:
            bool: Success status
        """
        content_slot = self._find_content_by_id(content_id)
        
        if not content_slot:
            logger.error(f"Content ID {content_id} not found in calendar")
            return False
        
        # Update content slot
        content_slot.update({
            "content_type": content_type,
            "content": content,
            "status": "scheduled"
        })
        
        logger.info(f"Scheduled content {content_id} for {content_slot['scheduled_time']}")
        return True
    
    def reschedule_content(self, content_id: str, new_time: datetime.datetime) -> bool:
        """
        Reschedule content to a new time.
        
        Args:
            content_id: ID of the content slot
            new_time: New scheduled time
            
        Returns:
            bool: Success status
        """
        content_slot = self._find_content_by_id(content_id)
        
        if not content_slot:
            logger.error(f"Content ID {content_id} not found in calendar")
            return False
        
        # Update scheduled time
        content_slot["scheduled_time"] = new_time.isoformat()
        
        # Update priority queue
        # (This is a simplification - in a real implementation, we would need to rebuild the queue)
        self.scheduled_queue = [(t, cid) for t, cid in self.scheduled_queue if cid != content_id]
        heapq.heappush(self.scheduled_queue, (new_time.timestamp(), content_id))
        heapq.heapify(self.scheduled_queue)
        
        logger.info(f"Rescheduled content {content_id} to {new_time}")
        return True
    
    def cancel_scheduled_content(self, content_id: str) -> bool:
        """
        Cancel scheduled content.
        
        Args:
            content_id: ID of the content slot
            
        Returns:
            bool: Success status
        """
        content_slot = self._find_content_by_id(content_id)
        
        if not content_slot:
            logger.error(f"Content ID {content_id} not found in calendar")
            return False
        
        # Update status
        content_slot["status"] = "cancelled"
        
        # Remove from priority queue
        self.scheduled_queue = [(t, cid) for t, cid in self.scheduled_queue if cid != content_id]
        heapq.heapify(self.scheduled_queue)
        
        logger.info(f"Cancelled scheduled content {content_id}")
        return True
    
    def get_daily_schedule(self, date: datetime.date) -> Dict:
        """
        Get the content schedule for a specific day.
        
        Args:
            date: Date to get schedule for
            
        Returns:
            Dict containing the day's schedule
        """
        date_str = date.strftime("%Y-%m-%d")
        return self.content_calendar.get(date_str, {})
    
    def save_calendar(self, file_path: str) -> bool:
        """
        Save the content calendar to a file.
        
        Args:
            file_path: Path to save the calendar to
            
        Returns:
            bool: Success status
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.content_calendar, f, indent=2)
            logger.info(f"Saved content calendar to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving content calendar: {e}")
            return False
    
    def load_calendar(self, file_path: str) -> bool:
        """
        Load the content calendar from a file.
        
        Args:
            file_path: Path to load the calendar from
            
        Returns:
            bool: Success status
        """
        if not os.path.exists(file_path):
            logger.error(f"Calendar file {file_path} does not exist")
            return False
        
        try:
            with open(file_path, 'r') as f:
                calendar = json.load(f)
            
            self.content_calendar = calendar
            
            # Rebuild priority queue
            self.scheduled_queue = []
            for date, platforms in calendar.items():
                for platform, posts in platforms.items():
                    for post in posts:
                        if post["status"] == "scheduled" and "scheduled_time" in post:
                            scheduled_time = datetime.datetime.fromisoformat(post["scheduled_time"])
                            heapq.heappush(
                                self.scheduled_queue, 
                                (scheduled_time.timestamp(), post["id"])
                            )
            
            logger.info(f"Loaded content calendar from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading content calendar: {e}")
            return False
