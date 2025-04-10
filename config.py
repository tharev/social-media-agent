"""
Configuration file for the social media agent system.

This file contains the configuration settings for the social media agent system,
including API keys, platform settings, and scheduling preferences.
"""

import os
from typing import Dict, Any

# API Keys (replace with your actual API keys or use environment variables)
API_KEYS = {
    # LLM API Keys
    "openai": os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here"),
    "anthropic": os.environ.get("ANTHROPIC_API_KEY", "your_anthropic_api_key_here"),
    
    # Social Media Platform API Keys
    "facebook": {
        "app_id": os.environ.get("FACEBOOK_APP_ID", "your_facebook_app_id_here"),
        "app_secret": os.environ.get("FACEBOOK_APP_SECRET", "your_facebook_app_secret_here"),
        "access_token": os.environ.get("FACEBOOK_ACCESS_TOKEN", "your_facebook_access_token_here"),
    },
    "twitter": {
        "api_key": os.environ.get("TWITTER_API_KEY", "your_twitter_api_key_here"),
        "api_secret": os.environ.get("TWITTER_API_SECRET", "your_twitter_api_secret_here"),
        "access_token": os.environ.get("TWITTER_ACCESS_TOKEN", "your_twitter_access_token_here"),
        "access_token_secret": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "your_twitter_access_token_secret_here"),
    },
    "instagram": {
        "username": os.environ.get("INSTAGRAM_USERNAME", "your_instagram_username_here"),
        "password": os.environ.get("INSTAGRAM_PASSWORD", "your_instagram_password_here"),
        "business_id": os.environ.get("INSTAGRAM_BUSINESS_ID", "your_instagram_business_id_here"),
    },
    "tiktok": {
        "app_id": os.environ.get("TIKTOK_APP_ID", "your_tiktok_app_id_here"),
        "app_secret": os.environ.get("TIKTOK_APP_SECRET", "your_tiktok_app_secret_here"),
        "access_token": os.environ.get("TIKTOK_ACCESS_TOKEN", "your_tiktok_access_token_here"),
    }
}

# Platform Settings
PLATFORM_SETTINGS = {
    "facebook": {
        "enabled": True,
        "post_frequency": "daily",  # daily, alternate_days, weekly
        "best_times": ["09:00", "15:00", "19:00"],  # Best times to post (24-hour format)
        "content_types": ["text", "image", "link"],
        "max_posts_per_day": 2,
    },
    "twitter": {
        "enabled": True,
        "post_frequency": "daily",
        "best_times": ["08:00", "12:00", "17:00", "20:00"],
        "content_types": ["text", "image", "poll"],
        "max_posts_per_day": 5,
    },
    "instagram": {
        "enabled": True,
        "post_frequency": "alternate_days",  # every other day
        "best_times": ["11:00", "17:00", "20:00"],
        "content_types": ["image", "carousel", "reel"],
        "max_posts_per_day": 1,
    },
    "tiktok": {
        "enabled": True,
        "post_frequency": "weekly",  # once per week
        "best_times": ["15:00", "19:00", "21:00"],
        "content_types": ["video"],
        "max_posts_per_day": 1,
    }
}

# Content Generation Settings
CONTENT_SETTINGS = {
    "business_name": "Your Business Name",
    "business_description": "A brief description of your business and what you offer",
    "business_industry": "Your Industry",
    "target_audience": ["demographic1", "demographic2", "demographic3"],
    "brand_voice": "professional",  # professional, casual, humorous, informative
    "content_themes": [
        "product_highlights",
        "industry_news",
        "tips_and_advice",
        "behind_the_scenes",
        "customer_stories"
    ],
    "hashtags": {
        "primary": ["#yourbrand", "#yourindustry"],
        "secondary": ["#relevant", "#hashtags", "#foryour", "#business"]
    },
    "competitor_accounts": [
        "competitor1",
        "competitor2",
        "competitor3"
    ]
}

# LLM Settings
LLM_SETTINGS = {
    "text_provider": "openai",  # openai, anthropic, etc.
    "text_model": "gpt-4",  # model name
    "image_provider": "openai",
    "image_model": "dall-e-3",
    "temperature": 0.7,  # creativity level (0.0-1.0)
    "max_tokens": 500,
    "style_preferences": {
        "facebook": "professional",
        "twitter": "concise",
        "instagram": "visual",
        "tiktok": "trendy"
    }
}

# Reporting Settings
REPORTING_SETTINGS = {
    "weekly_report_day": "Monday",
    "weekly_report_time": "09:00",
    "metrics_to_track": [
        "engagement",
        "impressions",
        "followers",
        "clicks",
        "conversions"
    ],
    "email_recipients": [
        "manager@example.com",
        "team@example.com"
    ],
    "report_format": "html"  # html, pdf, json
}

# System Settings
SYSTEM_SETTINGS = {
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "data_directory": "data",
    "metrics_directory": "metrics",
    "reports_directory": "reports",
    "content_directory": "content",
    "timezone": "UTC",
}

def get_config() -> Dict[str, Any]:
    """
    Get the complete configuration dictionary.
    
    Returns:
        Dict containing all configuration settings
    """
    return {
        "api_keys": API_KEYS,
        "platform_settings": PLATFORM_SETTINGS,
        "content_settings": CONTENT_SETTINGS,
        "llm_settings": LLM_SETTINGS,
        "reporting_settings": REPORTING_SETTINGS,
        "system_settings": SYSTEM_SETTINGS
    }
