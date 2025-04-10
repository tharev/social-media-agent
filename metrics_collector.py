"""
Metrics Collector class for gathering performance data from social media platforms.

This module implements functionality for collecting metrics from various
social media platforms and storing them for analysis and reporting.
"""

import logging
import datetime
import json
import os
from typing import Dict, List, Optional, Any

from ..platform_agents.base_agent import BasePlatformAgent

logger = logging.getLogger("reporting.metrics_collector")

class MetricsCollector:
    """
    Metrics Collector for gathering performance data from social media platforms.
    
    This class handles:
    - Daily metrics collection from all platforms
    - Metrics storage and retrieval
    - Historical data management
    - Data aggregation for reporting
    """
    
    def __init__(self, platform_agents: Dict[str, BasePlatformAgent] = None, config: Dict = None):
        """
        Initialize the Metrics Collector.
        
        Args:
            platform_agents: Dictionary of platform agents keyed by platform name
            config: Configuration dictionary
        """
        self.platform_agents = platform_agents or {}
        self.config = config or {}
        
        # Metrics storage settings
        self.metrics_dir = self.config.get("metrics_dir", "metrics")
        self.metrics_cache = {}
        
        # Create metrics directory if it doesn't exist
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        logger.info("Metrics Collector initialized")
    
    def collect_daily_metrics(self, date: datetime.date = None) -> Dict:
        """
        Collect daily metrics from all platforms.
        
        Args:
            date: Date to collect metrics for (defaults to yesterday)
            
        Returns:
            Dict containing metrics for all platforms
        """
        # Default to yesterday if no date provided
        if date is None:
            date = datetime.date.today() - datetime.timedelta(days=1)
        
        date_str = date.strftime("%Y-%m-%d")
        
        # Check if metrics for this date are already cached
        if date_str in self.metrics_cache:
            logger.info(f"Using cached metrics for {date_str}")
            return self.metrics_cache[date_str]
        
        # Check if metrics for this date are already stored
        metrics_file = os.path.join(self.metrics_dir, f"daily_{date_str}.json")
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                
                logger.info(f"Loaded stored metrics for {date_str}")
                self.metrics_cache[date_str] = metrics
                return metrics
            except Exception as e:
                logger.error(f"Error loading stored metrics: {e}")
        
        # Collect metrics from each platform
        all_metrics = {
            "date": date_str,
            "collected_at": datetime.datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform_name, agent in self.platform_agents.items():
            try:
                logger.info(f"Collecting metrics for {platform_name} on {date_str}")
                platform_metrics = agent.get_metrics(date)
                
                if platform_metrics:
                    all_metrics["platforms"][platform_name] = platform_metrics
                else:
                    logger.warning(f"No metrics returned for {platform_name} on {date_str}")
                    all_metrics["platforms"][platform_name] = {
                        "date": date_str,
                        "platform": platform_name,
                        "error": "No metrics returned"
                    }
            except Exception as e:
                logger.error(f"Error collecting metrics for {platform_name}: {e}")
                all_metrics["platforms"][platform_name] = {
                    "date": date_str,
                    "platform": platform_name,
                    "error": str(e)
                }
        
        # Calculate aggregated metrics
        all_metrics["total_engagement"] = sum(
            platform.get("engagement", 0) 
            for platform in all_metrics["platforms"].values()
        )
        
        all_metrics["total_impressions"] = sum(
            platform.get("impressions", 0) 
            for platform in all_metrics["platforms"].values()
        )
        
        all_metrics["total_posts"] = sum(
            platform.get("posts", 0) 
            for platform in all_metrics["platforms"].values()
        )
        
        # Store metrics
        try:
            with open(metrics_file, 'w') as f:
                json.dump(all_metrics, f, indent=2)
            
            logger.info(f"Stored metrics for {date_str}")
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
        
        # Cache metrics
        self.metrics_cache[date_str] = all_metrics
        
        return all_metrics
    
    def collect_post_metrics(self, platform: str, post_id: str) -> Dict:
        """
        Collect metrics for a specific post.
        
        Args:
            platform: Platform name
            post_id: ID of the post
            
        Returns:
            Dict containing post metrics
        """
        if platform not in self.platform_agents:
            logger.error(f"Platform agent not found: {platform}")
            return {"success": False, "error": f"Platform agent not found: {platform}"}
        
        try:
            agent = self.platform_agents[platform]
            metrics = agent.get_post_metrics(post_id)
            
            if not metrics:
                logger.warning(f"No metrics returned for post {post_id} on {platform}")
                return {
                    "success": False,
                    "platform": platform,
                    "post_id": post_id,
                    "error": "No metrics returned"
                }
            
            # Add collection timestamp
            metrics["collected_at"] = datetime.datetime.now().isoformat()
            metrics["success"] = True
            
            # Store post metrics
            post_metrics_dir = os.path.join(self.metrics_dir, "posts")
            os.makedirs(post_metrics_dir, exist_ok=True)
            
            metrics_file = os.path.join(post_metrics_dir, f"{platform}_{post_id}.json")
            
            try:
                with open(metrics_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                logger.info(f"Stored post metrics for {platform} post {post_id}")
            except Exception as e:
                logger.error(f"Error storing post metrics: {e}")
            
            return metrics
        except Exception as e:
            logger.error(f"Error collecting post metrics: {e}")
            return {
                "success": False,
                "platform": platform,
                "post_id": post_id,
                "error": str(e)
            }
    
    def get_metrics_for_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
        """
        Get metrics for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily metrics dictionaries
        """
        metrics_list = []
        current_date = start_date
        
        while current_date <= end_date:
            metrics = self.collect_daily_metrics(current_date)
            metrics_list.append(metrics)
            current_date += datetime.timedelta(days=1)
        
        return metrics_list
    
    def get_weekly_metrics(self, week_end_date: datetime.date = None) -> Dict:
        """
        Get aggregated metrics for a week.
        
        Args:
            week_end_date: End date of the week (defaults to yesterday)
            
        Returns:
            Dict containing aggregated weekly metrics
        """
        # Default to yesterday if no date provided
        if week_end_date is None:
            week_end_date = datetime.date.today() - datetime.timedelta(days=1)
        
        # Calculate start date (7 days before end date)
        start_date = week_end_date - datetime.timedelta(days=6)
        
        # Get metrics for the date range
        daily_metrics = self.get_metrics_for_date_range(start_date, week_end_date)
        
        # Aggregate metrics
        weekly_metrics = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": week_end_date.strftime("%Y-%m-%d"),
            "collected_at": datetime.datetime.now().isoformat(),
            "platforms": {},
            "daily_metrics": daily_metrics
        }
        
        # Initialize platform aggregates
        platforms = set()
        for daily in daily_metrics:
            platforms.update(daily.get("platforms", {}).keys())
        
        for platform in platforms:
            weekly_metrics["platforms"][platform] = {
                "platform": platform,
                "total_engagement": 0,
                "total_impressions": 0,
                "total_posts": 0,
                "daily_engagement": {},
                "daily_impressions": {},
                "daily_posts": {}
            }
        
        # Aggregate daily metrics
        for daily in daily_metrics:
            date = daily.get("date")
            
            for platform, metrics in daily.get("platforms", {}).items():
                if platform in weekly_metrics["platforms"]:
                    platform_weekly = weekly_metrics["platforms"][platform]
                    
                    # Add to totals
                    platform_weekly["total_engagement"] += metrics.get("engagement", 0)
                    platform_weekly["total_impressions"] += metrics.get("impressions", 0)
                    platform_weekly["total_posts"] += metrics.get("posts", 0)
                    
                    # Add to daily tracking
                    platform_weekly["daily_engagement"][date] = metrics.get("engagement", 0)
                    platform_weekly["daily_impressions"][date] = metrics.get("impressions", 0)
                    platform_weekly["daily_posts"][date] = metrics.get("posts", 0)
        
        # Calculate overall totals
        weekly_metrics["total_engagement"] = sum(
            platform.get("total_engagement", 0) 
            for platform in weekly_metrics["platforms"].values()
        )
        
        weekly_metrics["total_impressions"] = sum(
            platform.get("total_impressions", 0) 
            for platform in weekly_metrics["platforms"].values()
        )
        
        weekly_metrics["total_posts"] = sum(
            platform.get("total_posts", 0) 
            for platform in weekly_metrics["platforms"].values()
        )
        
        # Store weekly metrics
        week_str = f"{start_date.strftime('%Y%m%d')}_to_{week_end_date.strftime('%Y%m%d')}"
        metrics_file = os.path.join(self.metrics_dir, f"weekly_{week_str}.json")
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(weekly_metrics, f, indent=2)
            
            logger.info(f"Stored weekly metrics for {week_str}")
        except Exception as e:
            logger.error(f"Error storing weekly metrics: {e}")
        
        return weekly_metrics
    
    def get_monthly_metrics(self, month: int = None, year: int = None) -> Dict:
        """
        Get aggregated metrics for a month.
        
        Args:
            month: Month number (1-12, defaults to last month)
            year: Year (defaults to current year)
            
        Returns:
            Dict containing aggregated monthly metrics
        """
        # Default to last month if no month provided
        today = datetime.date.today()
        if month is None:
            month = today.month - 1
            if month == 0:
                month = 12
                year = today.year - 1
        
        if year is None:
            year = today.year
        
        # Calculate start and end dates
        import calendar
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, last_day)
        
        # Get metrics for the date range
        daily_metrics = self.get_metrics_for_date_range(start_date, end_date)
        
        # Aggregate metrics
        monthly_metrics = {
            "month": month,
            "year": year,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "collected_at": datetime.datetime.now().isoformat(),
            "platforms": {},
            "weekly_breakdown": {}
        }
        
        # Initialize platform aggregates
        platforms = set()
        for daily in daily_metrics:
            platforms.update(daily.get("platforms", {}).keys())
        
        for platform in platforms:
            monthly_metrics["platforms"][platform] = {
                "platform": platform,
                "total_engagement": 0,
                "total_impressions": 0,
                "total_posts": 0,
                "weekly_engagement": {},
                "weekly_impressions": {},
                "weekly_posts": {}
            }
        
        # Aggregate daily metrics into weekly buckets
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            # Calculate week end (Saturday)
            days_to_saturday = 5 - current_date.weekday()
            if days_to_saturday < 0:
                days_to_saturday += 7
            
            week_end = current_date + datetime.timedelta(days=days_to_saturday)
            if week_end > end_date:
                week_end = end_date
            
            week_metrics = {
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": week_end.strftime("%Y-%m-%d"),
                "platforms": {}
            }
            
            # Initialize platform weekly metrics
            for platform in platforms:
                week_metrics["platforms"][platform] = {
                    "platform": platform,
                    "engagement": 0,
                    "impressions": 0,
                    "posts": 0
                }
            
            # Find daily metrics for this week
            week_daily_metrics = [
                m for m in daily_metrics 
                if start_date <= datetime.datetime.strptime(m["date"], "%Y-%m-%d").date() <= week_end
            ]
            
            # Aggregate daily metrics for this week
            for daily in week_daily_metrics:
                for platform, metrics in daily.get("platforms", {}).items():
                    if platform in week_metrics["platforms"]:
                        platform_week = week_metrics["platforms"][platform]
                        
                        # Add to weekly totals
                        platform_week["engagement"] += metrics.get("engagement", 0)
                        platform_week["impressions"] += metrics.get("impressions", 0)
                        platform_week["posts"] += metrics.get("posts", 0)
                        
                        # Add to monthly platform totals
                        monthly_metrics["platforms"][platform]["total_engagement"] += metrics.get("engagement", 0)
                        monthly_metrics["platforms"][platform]["total_impressions"] += metrics.get("impressions", 0)
                        monthly_metrics["platforms"][platform]["total_posts"] += metrics.get("posts", 0)
                        
                        # Track weekly breakdown
                        week_key = f"week_{week_num}"
                        monthly_metrics["p<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>