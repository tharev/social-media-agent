"""
Analytics component for the Team Leader Agent.

This module implements the analytics functionality for collecting and analyzing
performance metrics across different social media platforms.
"""

import datetime
import logging
from typing import Dict, List, Optional, Any
import json
import os
import pandas as pd
import numpy as np
from collections import defaultdict

logger = logging.getLogger("team_leader.analytics")

class AnalyticsEngine:
    """
    Analytics engine for collecting and analyzing social media performance metrics.
    
    The AnalyticsEngine is responsible for:
    - Collecting metrics from platform-specific agents
    - Analyzing performance trends
    - Identifying insights and opportunities
    - Providing data for reporting
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the AnalyticsEngine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.metrics_store = {}
        self.platform_benchmarks = self._load_benchmarks()
        
        logger.info("AnalyticsEngine initialized")
    
    def _load_benchmarks(self) -> Dict:
        """
        Load performance benchmarks for each platform.
        
        Returns:
            Dict containing benchmark metrics
        """
        # Default benchmarks based on industry averages
        default_benchmarks = {
            "facebook": {
                "engagement_rate": 0.064,  # 6.4% average engagement rate
                "click_through_rate": 0.011,  # 1.1% average CTR
                "growth_rate": 0.02  # 2% monthly follower growth
            },
            "twitter": {
                "engagement_rate": 0.045,  # 4.5% average engagement rate
                "click_through_rate": 0.02,  # 2% average CTR
                "growth_rate": 0.015  # 1.5% monthly follower growth
            },
            "instagram": {
                "engagement_rate": 0.079,  # 7.9% average engagement rate
                "click_through_rate": 0.016,  # 1.6% average CTR
                "growth_rate": 0.03  # 3% monthly follower growth
            },
            "tiktok": {
                "engagement_rate": 0.18,  # 18% average engagement rate
                "click_through_rate": 0.03,  # 3% average CTR
                "growth_rate": 0.05  # 5% monthly follower growth
            }
        }
        
        # Try to load from config if available
        benchmarks = self.config.get("platform_benchmarks", default_benchmarks)
        
        logger.info("Loaded platform benchmarks")
        return benchmarks
    
    def store_metrics(self, platform: str, date: str, metrics: Dict) -> None:
        """
        Store metrics for a platform on a specific date.
        
        Args:
            platform: Platform name
            date: Date string (YYYY-MM-DD)
            metrics: Dictionary of metrics
        """
        if platform not in self.metrics_store:
            self.metrics_store[platform] = {}
        
        self.metrics_store[platform][date] = metrics
        logger.info(f"Stored metrics for {platform} on {date}")
    
    def get_metrics(self, platform: str, start_date: str, end_date: str = None) -> Dict:
        """
        Get metrics for a platform within a date range.
        
        Args:
            platform: Platform name
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD), defaults to start_date
            
        Returns:
            Dict containing metrics for the specified period
        """
        if end_date is None:
            end_date = start_date
        
        if platform not in self.metrics_store:
            logger.warning(f"No metrics available for platform {platform}")
            return {}
        
        # Convert dates to datetime objects for comparison
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Filter metrics within date range
        result = {}
        for date_str, metrics in self.metrics_store[platform].items():
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if start <= date <= end:
                result[date_str] = metrics
        
        return result
    
    def calculate_engagement_rate(self, platform: str, period: int = 7) -> float:
        """
        Calculate the average engagement rate for a platform over a period.
        
        Args:
            platform: Platform name
            period: Number of days to analyze
            
        Returns:
            float: Average engagement rate
        """
        if platform not in self.metrics_store:
            logger.warning(f"No metrics available for platform {platform}")
            return 0.0
        
        # Get dates for the period
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=period)
        
        total_engagement = 0
        total_impressions = 0
        
        # Iterate through dates in the period
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if date_str in self.metrics_store[platform]:
                metrics = self.metrics_store[platform][date_str]
                total_engagement += metrics.get("engagement", 0)
                total_impressions += metrics.get("impressions", 0)
            
            current_date += datetime.timedelta(days=1)
        
        # Calculate engagement rate
        if total_impressions > 0:
            engagement_rate = total_engagement / total_impressions
        else:
            engagement_rate = 0.0
        
        return engagement_rate
    
    def calculate_growth_rate(self, platform: str, period: int = 30) -> float:
        """
        Calculate the follower growth rate for a platform over a period.
        
        Args:
            platform: Platform name
            period: Number of days to analyze
            
        Returns:
            float: Growth rate as a percentage
        """
        if platform not in self.metrics_store:
            logger.warning(f"No metrics available for platform {platform}")
            return 0.0
        
        # Get dates for the period
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=period)
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Get follower counts
        start_followers = 0
        if start_date_str in self.metrics_store[platform]:
            start_followers = self.metrics_store[platform][start_date_str].get("followers", 0)
        
        end_followers = 0
        if end_date_str in self.metrics_store[platform]:
            end_followers = self.metrics_store[platform][end_date_str].get("followers", 0)
        
        # Calculate growth rate
        if start_followers > 0:
            growth_rate = (end_followers - start_followers) / start_followers * 100
        else:
            growth_rate = 0.0
        
        return growth_rate
    
    def identify_trends(self, platform: str, metric: str, period: int = 30) -> Dict:
        """
        Identify trends in a specific metric for a platform.
        
        Args:
            platform: Platform name
            metric: Metric name
            period: Number of days to analyze
            
        Returns:
            Dict containing trend information
        """
        if platform not in self.metrics_store:
            logger.warning(f"No metrics available for platform {platform}")
            return {"trend": "unknown", "slope": 0.0, "confidence": 0.0}
        
        # Get dates for the period
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=period)
        
        # Collect metric values
        dates = []
        values = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if date_str in self.metrics_store[platform]:
                metrics = self.metrics_store[platform][date_str]
                if metric in metrics:
                    dates.append((current_date - start_date).days)
                    values.append(metrics[metric])
            
            current_date += datetime.timedelta(days=1)
        
        # If we don't have enough data, return unknown trend
        if len(dates) < 3:
            return {"trend": "unknown", "slope": 0.0, "confidence": 0.0}
        
        # Calculate trend using linear regression
        try:
            # Convert to numpy arrays
            x = np.array(dates)
            y = np.array(values)
            
            # Add constant for intercept
            X = np.vstack([x, np.ones(len(x))]).T
            
            # Perform linear regression
            slope, intercept = np.linalg.lstsq(X, y, rcond=None)[0]
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_total = np.sum((y - np.mean(y)) ** 2)
            ss_residual = np.sum((y - y_pred) ** 2)
            r_squared = 1 - (ss_residual / ss_total)
            
            # Determine trend direction
            if slope > 0.01:
                trend = "increasing"
            elif slope < -0.01:
                trend = "decreasing"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "slope": slope,
                "confidence": r_squared
            }
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return {"trend": "unknown", "slope": 0.0, "confidence": 0.0}
    
    def compare_to_benchmark(self, platform: str, metric: str, value: float) -> Dict:
        """
        Compare a metric value to the benchmark for a platform.
        
        Args:
            platform: Platform name
            metric: Metric name
            value: Metric value
            
        Returns:
            Dict containing comparison information
        """
        if platform not in self.platform_benchmarks:
            logger.warning(f"No benchmarks available for platform {platform}")
            return {"status": "unknown", "difference": 0.0}
        
        if metric not in self.platform_benchmarks[platform]:
            logger.warning(f"No benchmark for metric {metric} on platform {platform}")
            return {"status": "unknown", "difference": 0.0}
        
        benchmark = self.platform_benchmarks[platform][metric]
        difference = value - benchmark
        percentage_diff = (difference / benchmark) * 100 if benchmark > 0 else 0.0
        
        # Determine status
        if percentage_diff >= 10:
            status = "above"
        elif percentage_diff <= -10:
            status = "below"
        else:
            status = "on_par"
        
        return {
            "status": status,
            "difference": difference,
            "percentage_diff": percentage_diff,
            "benchmark": benchmark
        }
    
    def get_best_performing_content(self, platform: str, period: int = 30, metric: str = "engagement") -> List[Dict]:
        """
        Get the best performing content for a platform.
        
        Args:
            platform: Platform name
            period: Number of days to analyze
            metric: Metric to sort by
            
        Returns:
            List of content items sorted by performance
        """
        if platform not in self.metrics_store:
            logger.warning(f"No metrics available for platform {platform}")
            return []
        
        # Get dates for the period
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=period)
        
        # Collect content items with metrics
        content_items = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if date_str in self.metrics_store[platform]:
                metrics = self.metrics_store[platform][date_str]
                
                if "content" in metrics:
                    for content in metrics["content"]:
                        if metric in content.get("metrics", {}):
                            content_items.append(content)
            
            current_date += datetime.timedelta(days=1)
        
        # Sort by the specified metric
        sorted_content = sorted(
            content_items,
            key=lambda x: x.get("metrics", {}).get(metric, 0),
            reverse=True
        )
        
        return sorted_content[:10]  # Return top 10
    
    def get_optimal_posting_times(self, platform: str, period: int = 30) -> Dict:
        """
        Determine optimal posting times for a platform based on engagement.
        
        Args:
            platform: Platform name
            period: Number of days to analyze
            
        Returns:
            Dict containing optimal posting times
        """
        if platform not in self.metrics_store:
            logger.warning(f"No metrics available for platform {platform}")
            return {"times": ["12:00"], "confidence": 0.0}
        
        # Get dates for the period
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=period)
        
        # Collect hourly engagement data
        hourly_engagement = defaultdict(list)
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            
            if date_str in self.metrics_store[platform]:
                metrics = self.metrics_store[platform][date_str]
                
                if "hourly_engagement" in metrics:
                    for hour, engagement in metrics["hourly_engagement"].items():
                        hour_int = int(hour)
                        hourly_engagement[hour_int].append(engagement)
            
            current_date += datetime.timedelta(days=1)
        
        # Calculate average engagement for each hour
        avg_engagement = {}
        for hour, values in hourly_engagement.items():
            if values:
                avg_engagement[hour] = sum(values) / len(values)
        
        # If we don't have enough data, return default time
        if not avg_engagement:
            return {"times": ["12:00"], "confidence": 0.0}
        
        # Sort hours by average engagement
        sorted_hours = sorted(
            avg_engagement.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get top 3 hours
        top_hours = sorted_hours[:3]
        
        # Format as time strings
        optimal_times = [f"{hour:02d}:00" for hour, _ in top_hours]
        
        # Calculate confidence based on data points
        total_days = (end_date - start_date).days + 1
        data_points = sum(len(values) for values in hourly_engagement.values())
        confidence = min(1.0, data_points / (total_days * 24 * 0.5))
        
        return {
            "times": optimal_times,
            "confidence": confidence
        }
    
    def generate_insights(self, platform: str = None, period: int = 30) -> List[Dict]:
        """
        Generate insights based on analytics data.
        
        Args:
            platform: Platform name (if None, generate for all platforms)
            period: Number of days to analyze
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Determine which platforms to analyze
        platform<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>