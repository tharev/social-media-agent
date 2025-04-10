"""
Report Generator component for the Team Leader Agent.

This module implements the reporting functionality for generating
comprehensive performance reports across social media platforms.
"""

import datetime
import logging
from typing import Dict, List, Optional, Any
import json
import os
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from jinja2 import Template

logger = logging.getLogger("team_leader.report_generator")

class ReportGenerator:
    """
    Report Generator for creating comprehensive social media performance reports.
    
    The ReportGenerator is responsible for:
    - Creating weekly performance reports
    - Generating visualizations of key metrics
    - Formatting reports in various output formats
    - Providing actionable insights and recommendations
    """
    
    def __init__(self, config: Dict = None, analytics_engine=None):
        """
        Initialize the ReportGenerator.
        
        Args:
            config: Configuration dictionary
            analytics_engine: Reference to the AnalyticsEngine instance
        """
        self.config = config or {}
        self.analytics_engine = analytics_engine
        self.report_templates = self._load_templates()
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        logger.info("ReportGenerator initialized")
    
    def _load_templates(self) -> Dict:
        """
        Load report templates.
        
        Returns:
            Dict containing templates for different report formats
        """
        # HTML template for weekly report
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ report.title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }
                .summary {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }
                .platform {
                    margin-bottom: 40px;
                    padding: 20px;
                    border: 1px solid #eee;
                    border-radius: 5px;
                }
                .platform-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .metrics {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .metric {
                    flex: 1;
                    min-width: 200px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    text-align: center;
                }
                .metric h3 {
                    margin-top: 0;
                    font-size: 16px;
                }
                .metric p {
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0;
                }
                .chart {
                    margin: 20px 0;
                    text-align: center;
                }
                .chart img {
                    max-width: 100%;
                    height: auto;
                }
                .top-content {
                    margin-top: 30px;
                }
                .content-item {
                    padding: 10px;
                    margin-bottom: 10px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }
                .recommendations {
                    margin-top: 40px;
                    padding: 20px;
                    background-color: #e8f4f8;
                    border-radius: 5px;
                }
                .recommendation {
                    margin-bottom: 10px;
                    padding-left: 20px;
                    position: relative;
                }
                .recommendation:before {
                    content: "→";
                    position: absolute;
                    left: 0;
                }
                .footer {
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #777;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ report.title }}</h1>
                <p>{{ report.period.start }} to {{ report.period.end }}</p>
            </div>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="metrics">
                    <div class="metric">
                        <h3>Total Posts</h3>
                        <p>{{ report.summary.total_posts }}</p>
                    </div>
                    <div class="metric">
                        <h3>Total Engagement</h3>
                        <p>{{ report.summary.total_engagement }}</p>
                    </div>
                    <div class="metric">
                        <h3>Avg. Engagement Rate</h3>
                        <p>{{ report.summary.avg_engagement_rate }}%</p>
                    </div>
                    <div class="metric">
                        <h3>Followers Growth</h3>
                        <p>{{ report.summary.total_followers_growth }}</p>
                    </div>
                </div>
                
                {% if report.summary.charts.engagement %}
                <div class="chart">
                    <h3>Engagement Across Platforms</h3>
                    <img src="data:image/png;base64,{{ report.summary.charts.engagement }}" alt="Engagement Chart">
                </div>
                {% endif %}
            </div>
            
            {% for platform_name, platform in report.platforms.items() %}
            <div class="platform">
                <div class="platform-header">
                    <h2>{{ platform_name|capitalize }}</h2>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <h3>Posts</h3>
                        <p>{{ platform.posts }}</p>
                    </div>
                    <div class="metric">
                        <h3>Engagement</h3>
                        <p>{{ platform.engagement }}</p>
                    </div>
                    <div class="metric">
                        <h3>Impressions</h3>
                        <p>{{ platform.impressions }}</p>
                    </div>
                    <div class="metric">
                        <h3>Followers Growth</h3>
                        <p>{{ platform.followers_growth }}</p>
                    </div>
                </div>
                
                {% if platform.charts.daily_engagement %}
                <div class="chart">
                    <h3>Daily Engagement</h3>
                    <img src="data:image/png;base64,{{ platform.charts.daily_engagement }}" alt="Daily Engagement Chart">
                </div>
                {% endif %}
                
                {% if platform.top_performing_content %}
                <div class="top-content">
                    <h3>Top Performing Content</h3>
                    <div class="content-item">
                        <p><strong>Content ID:</strong> {{ platform.top_performing_content.id }}</p>
                        <p><strong>Type:</strong> {{ platform.top_performing_content.content_type }}</p>
                        <p><strong>Engagement:</strong> {{ platform.top_performing_content.metrics.engagement }}</p>
                        <p><strong>Posted:</strong> {{ platform.top_performing_content.posted_at }}</p>
                    </div>
                </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <div class="recommendations">
                <h2>Recommendations</h2>
                {% for recommendation in report.recommendations %}
                <div class="recommendation">
                    <p>{{ recommendation }}</p>
                </div>
                {% endfor %}
            </div>
            
            <div class="footer">
                <p>Generated by Social Media Agent System on {{ report.generated_at }}</p>
            </div>
        </body>
        </html>
        """
        
        # Markdown template for weekly report
        markdown_template = """
        # {{ report.title }}
        
        **Period:** {{ report.period.start }} to {{ report.period.end }}
        
        ## Executive Summary
        
        - **Total Posts:** {{ report.summary.total_posts }}
        - **Total Engagement:** {{ report.summary.total_engagement }}
        - **Avg. Engagement Rate:** {{ report.summary.avg_engagement_rate }}%
        - **Followers Growth:** {{ report.summary.total_followers_growth }}
        
        {% for platform_name, platform in report.platforms.items() %}
        ## {{ platform_name|capitalize }}
        
        - **Posts:** {{ platform.posts }}
        - **Engagement:** {{ platform.engagement }}
        - **Impressions:** {{ platform.impressions }}
        - **Followers Growth:** {{ platform.followers_growth }}
        
        {% if platform.top_performing_content %}
        ### Top Performing Content
        
        - **Content ID:** {{ platform.top_performing_content.id }}
        - **Type:** {{ platform.top_performing_content.content_type }}
        - **Engagement:** {{ platform.top_performing_content.metrics.engagement }}
        - **Posted:** {{ platform.top_performing_content.posted_at }}
        {% endif %}
        
        {% endfor %}
        
        ## Recommendations
        
        {% for recommendation in report.recommendations %}
        - {{ recommendation }}
        {% endfor %}
        
        ---
        
        Generated by Social Media Agent System on {{ report.generated_at }}
        """
        
        return {
            "html": Template(html_template),
            "markdown": Template(markdown_template)
        }
    
    def generate_weekly_report(self, end_date: datetime.date = None, platforms: List[str] = None) -> Dict:
        """
        Generate a weekly progress report.
        
        Args:
            end_date: End date for the report period (defaults to today)
            platforms: List of platforms to include in the report
            
        Returns:
            Dict containing the report data
        """
        if end_date is None:
            end_date = datetime.date.today()
        
        start_date = end_date - datetime.timedelta(days=7)
        
        # Use platforms from config if not specified
        if platforms is None:
            platforms = self.config.get("platforms", ["facebook", "twitter", "instagram", "tiktok"])
        
        report = {
            "title": f"Weekly Social Media Performance Report",
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platforms": {},
            "summary": {
                "total_posts": 0,
                "total_engagement": 0,
                "total_impressions": 0,
                "avg_engagement_rate": 0.0,
                "total_followers_growth": 0,
                "charts": {}
            },
            "recommendations": []
        }
        
        # Process each platform
        for platform in platforms:
            # Skip if analytics engine is not available
            if self.analytics_engine is None:
                logger.warning("Analytics engine not available, using placeholder data")
                report["platforms"][platform] = self._generate_placeholder_data(platform)
                continue
            
            # Get metrics for this platform
            metrics = self.analytics_engine.get_metrics(
                platform,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            # Initialize platform data
            platform_data = {
                "posts": 0,
                "engagement": 0,
                "impressions": 0,
                "clicks": 0,
                "followers_growth": 0,
                "top_performing_content": None,
                "metrics_by_day": {},
                "charts": {}
            }
            
            # Process daily metrics
            daily_engagement = []
            daily_impressions = []
            dates = []
            
            for date_str, daily_metrics in sorted(metrics.items()):
                # Add date to list
                dates.append(date_str)
                
                # Update platform metrics
                platform_data["posts"] += daily_metrics.get("posts", 0)
                platform_data["engagement"] += daily_metrics.get("engagement", 0)
                platform_data["impressions"] += daily_metrics.get("impressions", 0)
                platform_data["clicks"] += daily_metrics.get("clicks", 0)
                
                # Store daily metrics
                platform_data["metrics_by_day"][date_str] = daily_metrics
                
                # Collect data for charts
                daily_engagement.append(daily_metrics.get("engagement", 0))
                daily_impressions.append(daily_metrics.get("impressions", 0))
            
            # Get followers growth
            start_followers = self.analytics_engine.metrics_store.get(platform, {}).get(
                start_date.strftime("%Y-%m-%d"), {}).get("followers", 0)
            end_followers = self.analytics_engine.metrics_store.get(platform, {}).get(
                end_date.strftime("%Y-%m-%d"), {}).get("followers", 0)
            platform_data["followers_growth"] = end_followers - start_followers
            
            # Get top performing content
            best_content = self.analytics_engine.get_best_performing_content(platform, 7)
            if best_content:
                platform_data["top_performing_content"] = best_content[0]
            
            # Generate charts
            if dates and daily_engagement:
                platform_data["charts"]["daily_engagement"] = self._create_line_chart(
                    dates, daily_engagement, "Daily Engagement", "Date", "Engagement"
                )
            
            # Add platform data to report
            report["platforms"][platform] = platform_data
            
            # Update summary
            report["summary"]["total_posts"] += platform_data["posts"]
            report["summary"]["total_engagement"] += platform_data["engagement"]
            report["summary"]["total_impressions"] += platform_data["impressions"]
            report["summary"]["total_followers_growth"] += platform_data["followers_growth"]
        
        # Calculate average engagement rate
        if report["summary"]["total_impressions"] > 0:
            report["summary"]["avg_engagement_rate"] = round(
                (report["summary"]["total_engagement"] / report["summary"]["total_impressions"]) * 100,
<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>