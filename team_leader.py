"""
Team Leader Agent - Core implementation.

This module implements the Team Leader Agent that coordinates activities
across all platform-specific agents, manages scheduling, collects analytics,
and generates reports.
"""

import datetime
import logging
from typing import Dict, List, Optional, Any
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("team_leader")

class TeamLeaderAgent:
    """
    Team Leader Agent that coordinates all social media platform agents.
    
    The Team Leader is responsible for:
    - Coordinating activities across platform-specific agents
    - Managing content scheduling
    - Collecting and analyzing performance metrics
    - Generating weekly progress reports
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Team Leader Agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.platform_agents = {}
        self.content_calendar = {}
        self.performance_metrics = {}
        self.config = self._load_config(config_path)
        self.last_report_date = None
        
        logger.info("Team Leader Agent initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        default_config = {
            "report_day": "Monday",
            "platforms": ["facebook", "twitter", "instagram", "tiktok"],
            "content_types": ["text", "image", "video"],
            "posts_per_day": {
                "facebook": 2,
                "twitter": 5,
                "instagram": 1,
                "tiktok": 1
            },
            "report_metrics": [
                "engagement_rate", 
                "impressions", 
                "clicks", 
                "followers_growth"
            ]
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            logger.info("Using default configuration")
            return default_config
    
    def register_platform_agent(self, platform: str, agent: Any) -> None:
        """
        Register a platform-specific agent with the Team Leader.
        
        Args:
            platform: Platform name (e.g., 'facebook', 'twitter')
            agent: Platform agent instance
        """
        self.platform_agents[platform] = agent
        self.performance_metrics[platform] = {}
        logger.info(f"Registered {platform} agent")
    
    def create_content_calendar(self, start_date: datetime.date, days: int = 7) -> Dict:
        """
        Create a content calendar for the specified period.
        
        Args:
            start_date: Start date for the calendar
            days: Number of days to schedule
            
        Returns:
            Dict containing the content calendar
        """
        calendar = {}
        current_date = start_date
        
        for _ in range(days):
            date_str = current_date.strftime("%Y-%m-%d")
            calendar[date_str] = {}
            
            for platform in self.config["platforms"]:
                posts_per_day = self.config["posts_per_day"].get(platform, 1)
                calendar[date_str][platform] = []
                
                for i in range(posts_per_day):
                    # Create empty slots for content
                    calendar[date_str][platform].append({
                        "id": f"{date_str}_{platform}_{i}",
                        "platform": platform,
                        "content_type": None,
                        "content": None,
                        "status": "planned",
                        "scheduled_time": None,
                        "metrics": {}
                    })
            
            current_date += datetime.timedelta(days=1)
        
        self.content_calendar.update(calendar)
        logger.info(f"Created content calendar from {start_date} for {days} days")
        return calendar
    
    def schedule_content(self, content_id: str, content_type: str, content: Dict, 
                         scheduled_time: datetime.datetime) -> bool:
        """
        Schedule content for posting.
        
        Args:
            content_id: ID of the content slot
            content_type: Type of content (text, image, video)
            content: Content data
            scheduled_time: Time to post the content
            
        Returns:
            bool: Success status
        """
        # Find the content slot
        for date, platforms in self.content_calendar.items():
            for platform, posts in platforms.items():
                for i, post in enumerate(posts):
                    if post["id"] == content_id:
                        self.content_calendar[date][platform][i].update({
                            "content_type": content_type,
                            "content": content,
                            "status": "scheduled",
                            "scheduled_time": scheduled_time.isoformat()
                        })
                        logger.info(f"Scheduled content {content_id} for {scheduled_time}")
                        return True
        
        logger.error(f"Content ID {content_id} not found in calendar")
        return False
    
    def update_metrics(self, platform: str, date: str, metrics: Dict) -> None:
        """
        Update performance metrics for a platform.
        
        Args:
            platform: Platform name
            date: Date string (YYYY-MM-DD)
            metrics: Dictionary of metrics
        """
        if platform not in self.performance_metrics:
            self.performance_metrics[platform] = {}
        
        if date not in self.performance_metrics[platform]:
            self.performance_metrics[platform][date] = {}
        
        self.performance_metrics[platform][date].update(metrics)
        logger.info(f"Updated metrics for {platform} on {date}")
    
    def generate_weekly_report(self, end_date: datetime.date = None) -> Dict:
        """
        Generate a weekly progress report.
        
        Args:
            end_date: End date for the report period (defaults to today)
            
        Returns:
            Dict containing the report data
        """
        if end_date is None:
            end_date = datetime.date.today()
        
        start_date = end_date - datetime.timedelta(days=7)
        
        report = {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "platforms": {},
            "summary": {
                "total_posts": 0,
                "total_engagement": 0,
                "followers_growth": {}
            },
            "recommendations": []
        }
        
        # Collect metrics for each platform
        for platform in self.config["platforms"]:
            report["platforms"][platform] = {
                "posts": 0,
                "engagement": 0,
                "impressions": 0,
                "clicks": 0,
                "followers_growth": 0,
                "top_performing_content": None,
                "metrics_by_day": {}
            }
            
            platform_total_engagement = 0
            max_engagement = 0
            top_content = None
            
            # Process each day in the report period
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Get metrics for this day if available
                daily_metrics = self.performance_metrics.get(platform, {}).get(date_str, {})
                
                # Get content posted on this day
                daily_posts = self.content_calendar.get(date_str, {}).get(platform, [])
                posted_count = sum(1 for post in daily_posts if post["status"] == "posted")
                
                # Update platform metrics
                report["platforms"][platform]["posts"] += posted_count
                report["summary"]["total_posts"] += posted_count
                
                # Process engagement for each post
                for post in daily_posts:
                    if post["status"] == "posted" and "metrics" in post:
                        engagement = post["metrics"].get("engagement", 0)
                        platform_total_engagement += engagement
                        
                        # Track top performing content
                        if engagement > max_engagement:
                            max_engagement = engagement
                            top_content = post
                
                # Store daily metrics
                report["platforms"][platform]["metrics_by_day"][date_str] = {
                    "posts": posted_count,
                    **daily_metrics
                }
                
                current_date += datetime.timedelta(days=1)
            
            # Update platform summary
            report["platforms"][platform]["engagement"] = platform_total_engagement
            report["summary"]["total_engagement"] += platform_total_engagement
            report["platforms"][platform]["top_performing_content"] = top_content
            
            # Add followers growth if available
            followers_start = self.performance_metrics.get(platform, {}).get(start_date.strftime("%Y-%m-%d"), {}).get("followers", 0)
            followers_end = self.performance_metrics.get(platform, {}).get(end_date.strftime("%Y-%m-%d"), {}).get("followers", 0)
            growth = followers_end - followers_start
            report["platforms"][platform]["followers_growth"] = growth
            report["summary"]["followers_growth"][platform] = growth
        
        # Generate recommendations based on performance
        self._generate_recommendations(report)
        
        # Save report
        self.last_report_date = end_date
        logger.info(f"Generated weekly report for period {start_date} to {end_date}")
        
        return report
    
    def _generate_recommendations(self, report: Dict) -> None:
        """
        Generate recommendations based on performance data.
        
        Args:
            report: Report data to analyze
        """
        recommendations = []
        
        # Find best performing platform
        best_platform = max(
            report["platforms"].items(),
            key=lambda x: x[1]["engagement"] / max(x[1]["posts"], 1)
        )[0]
        
        recommendations.append(f"The {best_platform} platform is showing the highest engagement rate. Consider allocating more resources to this platform.")
        
        # Find underperforming platforms
        for platform, data in report["platforms"].items():
            if data["posts"] > 0 and data["engagement"] / data["posts"] < 10:
                recommendations.append(f"The {platform} platform is showing low engagement. Consider revising content strategy for this platform.")
        
        # Check posting frequency
        for platform, data in report["platforms"].items():
            expected_posts = 7 * self.config["posts_per_day"].get(platform, 1)
            if data["posts"] < expected_posts * 0.8:
                recommendations.append(f"Posting frequency on {platform} is below target. Consider increasing content production for this platform.")
        
        # Add recommendations to report
        report["recommendations"] = recommendations
    
    def execute_daily_tasks(self) -> None:
        """
        Execute daily tasks for the Team Leader Agent.
        
        This includes:
        - Checking for scheduled content
        - Collecting metrics
        - Generating reports if it's the report day
        """
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        
        logger.info(f"Executing daily tasks for {today_str}")
        
        # Check for scheduled content
        self._process_scheduled_content(today)
        
        # Collect metrics from all platforms
        self._collect_platform_metrics(today)
        
        # Generate weekly report if it's the report day
        if today.strftime("%A") == self.config["report_day"]:
            report = self.generate_weekly_report(today)
            self._distribute_weekly_report(report)
    
    def _process_scheduled_content(self, date: datetime.date) -> None:
        """
        Process scheduled content for the given date.
        
        Args:
            date: Date to process
        """
        date_str = date.strftime("%Y-%m-%d")
        
        if date_str not in self.content_calendar:
            logger.warning(f"No content calendar entry for {date_str}")
            return
        
        for platform, posts in self.content_calendar[date_str].items():
            if platform not in self.platform_agents:
                logger.warning(f"No agent registered for platform {platform}")
                continue
            
            agent = self.platform_agents[platform]
            
            for post in posts:
                if post["status"] == "scheduled":
                    scheduled_time = datetime.datetime.fromisoformat(post["scheduled_time"])
                    
                    # Check if it's time to post
                    if scheduled_time.date() == date and scheduled_time.time() <= datetime.datetime.now().time():
                        try:
                            # Post content using platform agent
                            result = agent.post_content(post["content_type"], post["content"])
                            
                            if result.get("success", False):
                                post["status"] = "posted"
                                post["post_id"] = result.get("post_id")
                                logger.info(f"Posted content {post['id']} to {platform}")
                            else:
                                post["status"] = "failed"
                                post["error"] = result.get("error")
                                logger.error(f"Failed to post content {post['id']} to {platform}: {result.get('error')}")
                        except Exception as e:
                            post["status"] = "failed"
                            post["error"] = str(e)
                            logger.error(f"Exception posting content {post['id']} to {platform}: {e}")
    
    def _collect_platform_metrics(self, date: datetime.date) -> None:
        """
        Collect metrics from all platform agents.
        
        Args:
            date: Date to collect metrics for
        """
        date_str = date.strftime("%Y-%m-%d")
        
        for platform, agent in self.platform_agents.items():
            try:
                metrics = agent.get_metrics(date)
                self.update_metrics(platform, date_str, metrics)
                
                # Update metrics for individual posts
                if date_str in self.content_calendar:
                    for post in self.content_calendar[date_str]<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>