"""
Unit tests for the Platform Agents module.

This module contains unit tests for the platform-specific agent classes.
"""

import unittest
import os
import sys
import datetime
from unittest.mock import MagicMock, patch

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.platform_agents.base_agent import BasePlatformAgent
from src.platform_agents.facebook_agent import FacebookAgent
from src.platform_agents.twitter_agent import TwitterAgent
from src.platform_agents.instagram_agent import InstagramAgent
from src.platform_agents.tiktok_agent import TikTokAgent


class TestBasePlatformAgent(unittest.TestCase):
    """Test cases for the BasePlatformAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        self.base_agent = BasePlatformAgent(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator
        )

    def test_initialization(self):
        """Test that BasePlatformAgent initializes correctly."""
        self.assertIsNotNone(self.base_agent)
        self.assertEqual(self.base_agent.platform_name, "base")
        self.assertIsNotNone(self.base_agent.text_llm)
        self.assertIsNotNone(self.base_agent.image_generator)

    def test_post_content_not_implemented(self):
        """Test that post_content raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.base_agent.post_content({"text": "Test content"})

    def test_get_metrics_not_implemented(self):
        """Test that get_metrics raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.base_agent.get_metrics()

    def test_get_post_metrics_not_implemented(self):
        """Test that get_post_metrics raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.base_agent.get_post_metrics("12345")


class TestFacebookAgent(unittest.TestCase):
    """Test cases for the FacebookAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        self.mock_api_client = MagicMock()
        
        self.facebook_agent = FacebookAgent(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator,
            api_client=self.mock_api_client
        )

    def test_initialization(self):
        """Test that FacebookAgent initializes correctly."""
        self.assertIsNotNone(self.facebook_agent)
        self.assertEqual(self.facebook_agent.platform_name, "facebook")
        self.assertIsNotNone(self.facebook_agent.text_llm)
        self.assertIsNotNone(self.facebook_agent.image_generator)
        self.assertIsNotNone(self.facebook_agent.api_client)

    def test_post_content_text_only(self):
        """Test posting text-only content."""
        # Mock the API client's post method
        self.mock_api_client.post_to_facebook.return_value = {
            'success': True,
            'post_id': '12345',
            'url': 'https://facebook.com/posts/12345'
        }
        
        result = self.facebook_agent.post_content({
            'text': 'Test Facebook post'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], '12345')
        self.assertEqual(result['platform'], 'facebook')
        self.mock_api_client.post_to_facebook.assert_called_once()

    def test_post_content_with_image(self):
        """Test posting content with an image."""
        # Mock the API client's post method
        self.mock_api_client.post_to_facebook.return_value = {
            'success': True,
            'post_id': '12345',
            'url': 'https://facebook.com/posts/12345'
        }
        
        result = self.facebook_agent.post_content({
            'text': 'Test Facebook post with image',
            'image': '/path/to/image.jpg'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], '12345')
        self.assertEqual(result['platform'], 'facebook')
        self.mock_api_client.post_to_facebook.assert_called_once()

    def test_get_metrics(self):
        """Test getting Facebook metrics."""
        # Mock the API client's get_metrics method
        self.mock_api_client.get_facebook_metrics.return_value = {
            'engagement': 150,
            'impressions': 1500,
            'followers': 750,
            'posts': 5,
            'post_ids': ['1', '2', '3', '4', '5']
        }
        
        result = self.facebook_agent.get_metrics()
        
        self.assertEqual(result['engagement'], 150)
        self.assertEqual(result['impressions'], 1500)
        self.assertEqual(result['followers'], 750)
        self.assertEqual(len(result['post_ids']), 5)
        self.mock_api_client.get_facebook_metrics.assert_called_once()

    def test_get_post_metrics(self):
        """Test getting metrics for a specific post."""
        # Mock the API client's get_post_metrics method
        self.mock_api_client.get_facebook_post_metrics.return_value = {
            'post_id': '12345',
            'engagement': 50,
            'impressions': 500,
            'likes': 30,
            'comments': 15,
            'shares': 5
        }
        
        result = self.facebook_agent.get_post_metrics('12345')
        
        self.assertEqual(result['post_id'], '12345')
        self.assertEqual(result['engagement'], 50)
        self.assertEqual(result['likes'], 30)
        self.mock_api_client.get_facebook_post_metrics.assert_called_once_with('12345')


class TestTwitterAgent(unittest.TestCase):
    """Test cases for the TwitterAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        self.mock_api_client = MagicMock()
        
        self.twitter_agent = TwitterAgent(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator,
            api_client=self.mock_api_client
        )

    def test_initialization(self):
        """Test that TwitterAgent initializes correctly."""
        self.assertIsNotNone(self.twitter_agent)
        self.assertEqual(self.twitter_agent.platform_name, "twitter")
        self.assertIsNotNone(self.twitter_agent.text_llm)
        self.assertIsNotNone(self.twitter_agent.image_generator)
        self.assertIsNotNone(self.twitter_agent.api_client)

    def test_post_content_text_only(self):
        """Test posting text-only content."""
        # Mock the API client's post method
        self.mock_api_client.post_tweet.return_value = {
            'success': True,
            'tweet_id': '67890',
            'url': 'https://twitter.com/user/status/67890'
        }
        
        result = self.twitter_agent.post_content({
            'text': 'Test tweet'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], '67890')
        self.assertEqual(result['platform'], 'twitter')
        self.mock_api_client.post_tweet.assert_called_once()

    def test_post_content_with_image(self):
        """Test posting content with an image."""
        # Mock the API client's post method
        self.mock_api_client.post_tweet.return_value = {
            'success': True,
            'tweet_id': '67890',
            'url': 'https://twitter.com/user/status/67890'
        }
        
        result = self.twitter_agent.post_content({
            'text': 'Test tweet with image',
            'image': '/path/to/image.jpg'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], '67890')
        self.assertEqual(result['platform'], 'twitter')
        self.mock_api_client.post_tweet.assert_called_once()

    def test_get_metrics(self):
        """Test getting Twitter metrics."""
        # Mock the API client's get_metrics method
        self.mock_api_client.get_twitter_metrics.return_value = {
            'engagement': 200,
            'impressions': 2000,
            'followers': 1000,
            'posts': 8,
            'post_ids': ['1', '2', '3', '4', '5', '6', '7', '8']
        }
        
        result = self.twitter_agent.get_metrics()
        
        self.assertEqual(result['engagement'], 200)
        self.assertEqual(result['impressions'], 2000)
        self.assertEqual(result['followers'], 1000)
        self.assertEqual(len(result['post_ids']), 8)
        self.mock_api_client.get_twitter_metrics.assert_called_once()

    def test_get_post_metrics(self):
        """Test getting metrics for a specific tweet."""
        # Mock the API client's get_tweet_metrics method
        self.mock_api_client.get_tweet_metrics.return_value = {
            'tweet_id': '67890',
            'engagement': 75,
            'impressions': 750,
            'likes': 40,
            'retweets': 20,
            'replies': 15
        }
        
        result = self.twitter_agent.get_post_metrics('67890')
        
        self.assertEqual(result['post_id'], '67890')
        self.assertEqual(result['engagement'], 75)
        self.assertEqual(result['likes'], 40)
        self.mock_api_client.get_tweet_metrics.assert_called_once_with('67890')


class TestInstagramAgent(unittest.TestCase):
    """Test cases for the InstagramAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        self.mock_api_client = MagicMock()
        
        self.instagram_agent = InstagramAgent(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator,
            api_client=self.mock_api_client
        )

    def test_initialization(self):
        """Test that InstagramAgent initializes correctly."""
        self.assertIsNotNone(self.instagram_agent)
        self.assertEqual(self.instagram_agent.platform_name, "instagram")
        self.assertIsNotNone(self.instagram_agent.text_llm)
        self.assertIsNotNone(self.instagram_agent.image_generator)
        self.assertIsNotNone(self.instagram_agent.api_client)

    def test_post_content_with_image(self):
        """Test posting content with an image (required for Instagram)."""
        # Mock the API client's post method
        self.mock_api_client.post_to_instagram.return_value = {
            'success': True,
            'post_id': 'abc123',
            'url': 'https://instagram.com/p/abc123'
        }
        
        result = self.instagram_agent.post_content({
            'text': 'Test Instagram post',
            'image': '/path/to/image.jpg'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], 'abc123')
        self.assertEqual(result['platform'], 'instagram')
        self.mock_api_client.post_to_instagram.assert_called_once()

    def test_post_content_without_image(self):
        """Test posting content without an image (should fail for Instagram)."""
        result = self.instagram_agent.post_content({
            'text': 'Test Instagram post without image'
        })
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['platform'], 'instagram')
        self.mock_api_client.post_to_instagram.assert_not_called()

    def test_get_metrics(self):
        """Test getting Instagram metrics."""
        # Mock the API client's get_metrics method
        self.mock_api_client.get_instagram_metrics.return_value = {
            'engagement': 300,
            'impressions': 3000,
            'followers': 1500,
            'posts': 10,
            'post_ids': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        }
        
        result = self.instagram_agent.get_metrics()
        
        self.assertEqual(result['engagement'], 300)
        self.assertEqual(result['impressions'], 3000)
        self.assertEqual(result['followers'], 1500)
        self.assertEqual(len(result['post_ids']), 10)
        self.mock_api_client.get_instagram_metrics.assert_called_once()

    def test_get_post_metrics(self):
        """Test getting metrics for a specific post."""
        # Mock the API client's get_post_metrics method
        self.mock_api_client.get_instagram_post_metrics.return_value = {
            'post_id': 'abc123',
            'engagement': 120,
            'impressions': 1200,
            'likes': 100,
            'comments': 20,
            'saves': 15
        }
        
        result = self.instagram_agent.get_post_metrics('abc123')
        
        self.assertEqual(result['post_id'], 'abc123')
        self.assertEqual(result['engagement'], 120)
        self.assertEqual(result['likes'], 100)
        self.mock_api_client.get_instagram_post_metrics.assert_called_once_with('abc123')


class TestTikTokAgent(unittest.TestCase):
    """Test cases for the TikTokAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        self.mock_api_client = MagicMock()
        
        self.tiktok_agent = TikTokAgent(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator,
            api_client=self.mock_api_client
        )

    def test_initialization(self):
        """Test that TikTokAgent initializes correctly."""
        self.assertIsNotNone(self.tiktok_agent)
        self.assertEqual(self.tiktok_agent.platform_name, "tiktok")
        self.assertIsNotNone(self.tiktok_agent.text_llm)
        self.assertIsNotNone(self.tiktok_agent.image_generator)
        self.assertIsNotNone(self.tiktok_agent.api_client)

    def test_post_content_with_video(self):
        """Test posting content with a video (required for TikTok)."""
        # Mock the API client's post method
        self.mock_api_client.post_to_tiktok.return_value = {
            'success': True,
            'post_id': 'xyz789',
            'url': 'https://tiktok.com/@user/video/xyz789'
        }
        
        result = self.tiktok_agent.post_content({
            'text': 'Test TikTok post',
            'video': '/path/to/video.mp4'
        })
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], 'xyz789')
        self.assertEqual(result['platform'], 'tiktok')
        self.mock_api_client.post_to_tiktok.assert_called_once()

    def test_post_content_without_video(self):
        """Test posting content without a video (should fail for TikTok)."""
        result = self.tiktok_agent.post_content({
            'text': 'Test TikTok post without video'
        })
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['platform'], 'tiktok')
        self.mock_api_client.post_to_tiktok.assert_not_called()

    def test_get_metrics(self):
        """Test getting TikTok metrics."""
        # Mock the API client's get_metrics method
        self.mock_api_client.get_tiktok_metrics.return_value = {
            'engagement': 500,
            'impressions': 5000,
            'followers': 2500,
            'posts': 7,
            'post_ids': ['1', '2', '3', '4', '5', '6', '7']
        }
        
        result = self.tiktok_agent.get_metrics()
        
        self.assertEqual(result['engagement'], 500)
        self.assertEqual(result['impressions'], 5000)
        self.assertEqual(result['followers'], 2500)
        self.assertEqual(len(result['post_ids']), 7)
        self.mock_api_client.get_tiktok_metrics.assert_called_once()

    def test_get_post_metrics(self):
        """Test getting metrics for a specific post."""
        # Mock the API client's get_post_metrics method
      <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>