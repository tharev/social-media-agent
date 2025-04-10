"""
Unit tests for the Content Generation module.

This module contains unit tests for the content generation components.
"""

import unittest
import os
import sys
import datetime
from unittest.mock import MagicMock, patch

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.content_generation.content_generator import ContentGenerator
from src.content_generation.text_content_generator import TextContentGenerator
from src.content_generation.image_content_generator import ImageContentGenerator
from src.content_generation.content_optimizer import ContentOptimizer


class TestContentGenerator(unittest.TestCase):
    """Test cases for the ContentGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        
        self.content_generator = ContentGenerator(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator
        )

    def test_initialization(self):
        """Test that ContentGenerator initializes correctly."""
        self.assertIsNotNone(self.content_generator)
        self.assertIsNotNone(self.content_generator.text_llm)
        self.assertIsNotNone(self.content_generator.image_generator)

    def test_generate_text_content(self):
        """Test generating text content."""
        # Mock the text LLM's generate_text method
        self.mock_text_llm.generate_text.return_value = "Generated text content"
        
        result = self.content_generator.generate_text_content(
            platform="twitter",
            topic="technology",
            tone="informative"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content_type'], 'text')
        self.assertEqual(result['platform'], 'twitter')
        self.assertEqual(result['text'], 'Generated text content')
        self.mock_text_llm.generate_text.assert_called_once()

    def test_generate_image_content(self):
        """Test generating image content."""
        # Mock the image generator's generate_image method
        self.mock_image_generator.generate_image.return_value = {
            'success': True,
            'data': 'http://example.com/image.jpg'
        }
        
        result = self.content_generator.generate_image_content(
            platform="instagram",
            topic="nature",
            style="artistic"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content_type'], 'image')
        self.assertEqual(result['platform'], 'instagram')
        self.assertEqual(result['image_url'], 'http://example.com/image.jpg')
        self.mock_image_generator.generate_image.assert_called_once()

    def test_generate_combined_content(self):
        """Test generating combined text and image content."""
        # Mock the text LLM's generate_text method
        self.mock_text_llm.generate_text.return_value = "Generated text with image"
        
        # Mock the image generator's generate_image method
        self.mock_image_generator.generate_image.return_value = {
            'success': True,
            'data': 'http://example.com/combined_image.jpg'
        }
        
        result = self.content_generator.generate_combined_content(
            platform="facebook",
            topic="travel",
            tone="enthusiastic",
            style="vibrant"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content_type'], 'combined')
        self.assertEqual(result['platform'], 'facebook')
        self.assertEqual(result['text'], 'Generated text with image')
        self.assertEqual(result['image_url'], 'http://example.com/combined_image.jpg')
        self.mock_text_llm.generate_text.assert_called_once()
        self.mock_image_generator.generate_image.assert_called_once()


class TestTextContentGenerator(unittest.TestCase):
    """Test cases for the TextContentGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.text_generator = TextContentGenerator(text_llm=self.mock_text_llm)

    def test_initialization(self):
        """Test that TextContentGenerator initializes correctly."""
        self.assertIsNotNone(self.text_generator)
        self.assertIsNotNone(self.text_generator.text_llm)
        self.assertIsNotNone(self.text_generator.platform_settings)
        self.assertIsNotNone(self.text_generator.content_templates)

    def test_generate_content(self):
        """Test generating text content."""
        # Mock the text LLM's generate_text method
        self.mock_text_llm.generate_text.return_value = '{"text": "Generated social media post", "hashtags": ["#test", "#social", "#media"]}'
        
        result = self.text_generator.generate_content(
            platform="twitter",
            topic="technology",
            tone="informative"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'twitter')
        self.assertEqual(result['topic'], 'technology')
        self.assertEqual(result['tone'], 'informative')
        self.mock_text_llm.generate_text.assert_called_once()

    def test_generate_content_series(self):
        """Test generating a series of related content posts."""
        # Mock the text LLM's generate_text method
        self.mock_text_llm.generate_text.return_value = '[{"text": "Post 1", "hashtags": ["#test1"]}, {"text": "Post 2", "hashtags": ["#test2"]}, {"text": "Post 3", "hashtags": ["#test3"]}]'
        
        result = self.text_generator.generate_content_series(
            platform="facebook",
            topic="business",
            count=3
        )
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['platform'], 'facebook')
        self.assertEqual(result[0]['topic'], 'business')
        self.assertEqual(result[0]['series_position'], 1)
        self.assertEqual(result[0]['series_total'], 3)
        self.mock_text_llm.generate_text.assert_called_once()

    def test_generate_from_template(self):
        """Test generating content from a template."""
        # Add a test template
        self.text_generator.content_templates['test_template'] = "This is a {topic} template"
        
        # Mock the generate_content method
        self.text_generator.generate_content = MagicMock(return_value={
            'success': True,
            'text': 'This is a technology template',
            'platform': 'twitter',
            'topic': 'technology'
        })
        
        result = self.text_generator.generate_from_template(
            platform="twitter",
            template="test_template",
            template_vars={"topic": "technology"}
        )
        
        self.assertTrue(result['success'])
        self.text_generator.generate_content.assert_called_once()


class TestImageContentGenerator(unittest.TestCase):
    """Test cases for the ImageContentGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_image_generator = MagicMock()
        self.mock_text_llm = MagicMock()
        
        self.image_generator = ImageContentGenerator(
            image_generator=self.mock_image_generator,
            text_llm=self.mock_text_llm
        )

    def test_initialization(self):
        """Test that ImageContentGenerator initializes correctly."""
        self.assertIsNotNone(self.image_generator)
        self.assertIsNotNone(self.image_generator.image_generator)
        self.assertIsNotNone(self.image_generator.text_llm)
        self.assertIsNotNone(self.image_generator.platform_settings)
        self.assertIsNotNone(self.image_generator.image_styles)

    @patch('requests.get')
    def test_generate_image(self, mock_requests_get):
        """Test generating an image."""
        # Mock the image generator's generate_social_media_image method
        self.mock_image_generator.generate_social_media_image.return_value = {
            'success': True,
            'data': 'http://example.com/generated_image.jpg'
        }
        
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'image_data'
        mock_requests_get.return_value = mock_response
        
        result = self.image_generator.generate_image(
            platform="instagram",
            topic="nature",
            style="artistic",
            save_locally=True
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'instagram')
        self.assertEqual(result['topic'], 'nature')
        self.assertEqual(result['style'], 'artistic')
        self.assertEqual(result['data'], 'http://example.com/generated_image.jpg')
        self.mock_image_generator.generate_social_media_image.assert_called_once()
        mock_requests_get.assert_called_once_with('http://example.com/generated_image.jpg')

    def test_generate_image_series(self):
        """Test generating a series of related images."""
        # Mock the generate_image method
        self.image_generator.generate_image = MagicMock(side_effect=[
            {'success': True, 'data': 'http://example.com/image1.jpg', 'platform': 'instagram', 'topic': 'travel'},
            {'success': True, 'data': 'http://example.com/image2.jpg', 'platform': 'instagram', 'topic': 'travel'},
            {'success': True, 'data': 'http://example.com/image3.jpg', 'platform': 'instagram', 'topic': 'travel'}
        ])
        
        result = self.image_generator.generate_image_series(
            platform="instagram",
            topic="travel",
            count=3,
            style="vibrant"
        )
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['data'], 'http://example.com/image1.jpg')
        self.assertEqual(result[1]['data'], 'http://example.com/image2.jpg')
        self.assertEqual(result[2]['data'], 'http://example.com/image3.jpg')
        self.assertEqual(self.image_generator.generate_image.call_count, 3)


class TestContentOptimizer(unittest.TestCase):
    """Test cases for the ContentOptimizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_text_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        
        self.content_optimizer = ContentOptimizer(
            text_llm=self.mock_text_llm,
            image_generator=self.mock_image_generator
        )

    def test_initialization(self):
        """Test that ContentOptimizer initializes correctly."""
        self.assertIsNotNone(self.content_optimizer)
        self.assertIsNotNone(self.content_optimizer.text_llm)
        self.assertIsNotNone(self.content_optimizer.image_generator)
        self.assertIsNotNone(self.content_optimizer.platform_settings)

    def test_optimize_text_for_platform(self):
        """Test optimizing text content for a specific platform."""
        # Mock the text LLM's generate_text method
        self.mock_text_llm.generate_text.return_value = "Optimized text for Twitter"
        
        result = self.content_optimizer.optimize_text_for_platform(
            text="Original long text that needs to be optimized",
            source_platform="facebook",
            target_platform="twitter"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['original_text'], "Original long text that needs to be optimized")
        self.assertEqual(result['optimized_text'], "Optimized text for Twitter")
        self.assertEqual(result['source_platform'], "facebook")
        self.assertEqual(result['target_platform'], "twitter")
        self.mock_text_llm.generate_text.assert_called_once()

    def test_optimize_image_for_platform(self):
        """Test optimizing image content for a specific platform."""
        # Mock the image generator's optimize_for_platform method
        self.mock_image_generator.optimize_for_platform.return_value = {
            'success': True,
            'data': 'http://example.com/optimized_image.jpg'
        }
        
        result = self.content_optimizer.optimize_image_for_platform(
            image_path="/path/to/image.jpg",
            source_platform="instagram",
            target_platform="facebook"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['source_platform'], "instagram")
        self.assertEqual(result['target_platform'], "facebook")
        self.assertEqual(result['data'], 'http://example.com/optimized_image.jpg')
        self.mock_image_generator.optimize_for_platform.assert_called_once()

    def test_get_platform_recommendations(self):
        """Test getting platform recommendations for content."""
        # Mock the text LLM's generate_text method
        self.mock_text_llm.generate_text.return_value = '{"facebook": {"score": 8, "explanation": "Good for Facebook"}, "twitter": {"score": 6, "explanation": "OK for Twitter"}, "instagram": {"score": 9, "explanation": "Great for Instagram"}, "tiktok": {"score": 4, "explanation": "Not ideal for TikTok"}}'
        
        result = self.content_optimizer.get_platform_recommendations(
            content="This is a test post with an image about travel"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content'], "This is a test post with an image about travel")
        self.assertIn('recommendations', result)
        self.mock_text_llm.generate_text.assert_called_once()


if __name__ == '__main__':
    unittest.main()
