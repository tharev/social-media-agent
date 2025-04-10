"""
Unit tests for the Reporting module.

This module contains unit tests for the reporting components.
"""

import unittest
import os
import sys
import datetime
from unittest.mock import MagicMock, patch

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reporting.metrics_collector import MetricsCollector
from src.reporting.report_generator import ReportGenerator


class TestMetricsCollector(unittest.TestCase):
    """Test cases for the MetricsCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_platform_agents = {
            'facebook': MagicMock(),
            'twitter': MagicMock(),
            'instagram': MagicMock(),
            'tiktok': MagicMock()
        }
        
        # Create a temporary metrics directory
        self.test_metrics_dir = "test_metrics"
        os.makedirs(self.test_metrics_dir, exist_ok=True)
        
        self.metrics_collector = MetricsCollector(
            platform_agents=self.mock_platform_agents,
            config={"metrics_dir": self.test_metrics_dir}
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        for file in os.listdir(self.test_metrics_dir):
            os.remove(os.path.join(self.test_metrics_dir, file))
        os.rmdir(self.test_metrics_dir)

    def test_initialization(self):
        """Test that MetricsCollector initializes correctly."""
        self.assertIsNotNone(self.metrics_collector)
        self.assertEqual(len(self.metrics_collector.platform_agents), 4)
        self.assertEqual(self.metrics_collector.metrics_dir, self.test_metrics_dir)

    def test_collect_daily_metrics(self):
        """Test collecting daily metrics from all platforms."""
        # Mock the platform agents' get_metrics methods
        self.mock_platform_agents['facebook'].get_metrics.return_value = {
            'engagement': 100,
            'impressions': 1000,
            'followers': 500,
            'posts': 3,
            'post_ids': ['fb1', 'fb2', 'fb3']
        }
        
        self.mock_platform_agents['twitter'].get_metrics.return_value = {
            'engagement': 250,
            'impressions': 2500,
            'followers': 1000,
            'posts': 5,
            'post_ids': ['tw1', 'tw2', 'tw3', 'tw4', 'tw5']
        }
        
        self.mock_platform_agents['instagram'].get_metrics.return_value = {
            'engagement': 300,
            'impressions': 3000,
            'followers': 1500,
            'posts': 4,
            'post_ids': ['ig1', 'ig2', 'ig3', 'ig4']
        }
        
        self.mock_platform_agents['tiktok'].get_metrics.return_value = {
            'engagement': 400,
            'impressions': 4000,
            'followers': 2000,
            'posts': 2,
            'post_ids': ['tk1', 'tk2']
        }
        
        # Use a specific date for testing
        test_date = datetime.date(2025, 3, 20)
        
        result = self.metrics_collector.collect_daily_metrics(test_date)
        
        self.assertEqual(result['date'], '2025-03-20')
        self.assertEqual(result['total_engagement'], 1050)
        self.assertEqual(result['total_impressions'], 10500)
        self.assertEqual(result['total_posts'], 14)
        
        # Check that metrics for each platform were collected
        self.assertIn('facebook', result['platforms'])
        self.assertIn('twitter', result['platforms'])
        self.assertIn('instagram', result['platforms'])
        self.assertIn('tiktok', result['platforms'])
        
        # Verify that the metrics file was created
        metrics_file = os.path.join(self.test_metrics_dir, 'daily_2025-03-20.json')
        self.assertTrue(os.path.exists(metrics_file))

    def test_collect_post_metrics(self):
        """Test collecting metrics for a specific post."""
        # Mock the platform agent's get_post_metrics method
        self.mock_platform_agents['twitter'].get_post_metrics.return_value = {
            'post_id': 'tw123',
            'engagement': 75,
            'impressions': 750,
            'likes': 40,
            'retweets': 20,
            'replies': 15
        }
        
        result = self.metrics_collector.collect_post_metrics('twitter', 'tw123')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], 'tw123')
        self.assertEqual(result['engagement'], 75)
        self.assertEqual(result['likes'], 40)
        
        # Verify that the post metrics directory was created
        post_metrics_dir = os.path.join(self.test_metrics_dir, 'posts')
        self.assertTrue(os.path.exists(post_metrics_dir))
        
        # Verify that the post metrics file was created
        post_metrics_file = os.path.join(post_metrics_dir, 'twitter_tw123.json')
        self.assertTrue(os.path.exists(post_metrics_file))

    def test_get_metrics_for_date_range(self):
        """Test getting metrics for a date range."""
        # Mock the collect_daily_metrics method
        self.metrics_collector.collect_daily_metrics = MagicMock(side_effect=[
            {'date': '2025-03-18', 'total_engagement': 900, 'platforms': {}},
            {'date': '2025-03-19', 'total_engagement': 950, 'platforms': {}},
            {'date': '2025-03-20', 'total_engagement': 1000, 'platforms': {}}
        ])
        
        start_date = datetime.date(2025, 3, 18)
        end_date = datetime.date(2025, 3, 20)
        
        result = self.metrics_collector.get_metrics_for_date_range(start_date, end_date)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['date'], '2025-03-18')
        self.assertEqual(result[1]['date'], '2025-03-19')
        self.assertEqual(result[2]['date'], '2025-03-20')
        self.assertEqual(self.metrics_collector.collect_daily_metrics.call_count, 3)

    def test_get_weekly_metrics(self):
        """Test getting aggregated metrics for a week."""
        # Mock the get_metrics_for_date_range method
        self.metrics_collector.get_metrics_for_date_range = MagicMock(return_value=[
            {
                'date': '2025-03-14',
                'platforms': {
                    'facebook': {'engagement': 90, 'impressions': 900, 'posts': 2},
                    'twitter': {'engagement': 180, 'impressions': 1800, 'posts': 3}
                }
            },
            {
                'date': '2025-03-15',
                'platforms': {
                    'facebook': {'engagement': 100, 'impressions': 1000, 'posts': 2},
                    'twitter': {'engagement': 200, 'impressions': 2000, 'posts': 4}
                }
            }
        ])
        
        week_end_date = datetime.date(2025, 3, 15)
        
        result = self.metrics_collector.get_weekly_metrics(week_end_date)
        
        self.assertEqual(result['start_date'], '2025-03-09')
        self.assertEqual(result['end_date'], '2025-03-15')
        self.assertEqual(result['total_engagement'], 570)
        self.assertEqual(result['total_impressions'], 5700)
        self.assertEqual(result['total_posts'], 11)
        
        # Check platform-specific aggregates
        self.assertEqual(result['platforms']['facebook']['total_engagement'], 190)
        self.assertEqual(result['platforms']['twitter']['total_engagement'], 380)
        
        # Verify that the weekly metrics file was created
        weekly_file = os.path.join(self.test_metrics_dir, 'weekly_20250309_to_20250315.json')
        self.assertTrue(os.path.exists(weekly_file))

    def test_get_best_performing_posts(self):
        """Test getting the best performing posts."""
        # Mock the get_metrics_for_date_range method
        self.metrics_collector.get_metrics_for_date_range = MagicMock(return_value=[
            {
                'date': '2025-03-20',
                'platforms': {
                    'facebook': {'post_ids': ['fb1', 'fb2']},
                    'twitter': {'post_ids': ['tw1', 'tw2']}
                }
            }
        ])
        
        # Mock the collect_post_metrics method
        self.metrics_collector.collect_post_metrics = MagicMock(side_effect=[
            {'success': True, 'post_id': 'fb1', 'platform': 'facebook', 'engagement': 50},
            {'success': True, 'post_id': 'fb2', 'platform': 'facebook', 'engagement': 80},
            {'success': True, 'post_id': 'tw1', 'platform': 'twitter', 'engagement': 120},
            {'success': True, 'post_id': 'tw2', 'platform': 'twitter', 'engagement': 90}
        ])
        
        start_date = datetime.date(2025, 3, 20)
        end_date = datetime.date(2025, 3, 20)
        
        result = self.metrics_collector.get_best_performing_posts(
            start_date=start_date,
            end_date=end_date,
            limit=3
        )
        
        self.assertEqual(len(result), 3)
        # Posts should be sorted by engagement (highest first)
        self.assertEqual(result[0]['post_id'], 'tw1')
        self.assertEqual(result[0]['engagement'], 120)
        self.assertEqual(result[1]['post_id'], 'tw2')
        self.assertEqual(result[1]['engagement'], 90)
        self.assertEqual(result[2]['post_id'], 'fb2')
        self.assertEqual(result[2]['engagement'], 80)


class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_metrics_collector = MagicMock()
        
        # Create temporary directories for reports and charts
        self.test_reports_dir = "test_reports"
        self.test_charts_dir = os.path.join(self.test_reports_dir, "charts")
        os.makedirs(self.test_charts_dir, exist_ok=True)
        
        self.report_generator = ReportGenerator(
            metrics_collector=self.mock_metrics_collector,
            config={"reports_dir": self.test_reports_dir}
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        for file in os.listdir(self.test_charts_dir):
            os.remove(os.path.join(self.test_charts_dir, file))
        os.rmdir(self.test_charts_dir)
        
        for file in os.listdir(self.test_reports_dir):
            os.remove(os.path.join(self.test_reports_dir, file))
        os.rmdir(self.test_reports_dir)

    def test_initialization(self):
        """Test that ReportGenerator initializes correctly."""
        self.assertIsNotNone(self.report_generator)
        self.assertIsNotNone(self.report_generator.metrics_collector)
        self.assertEqual(self.report_generator.reports_dir, self.test_reports_dir)
        self.assertEqual(self.report_generator.charts_dir, self.test_charts_dir)

    @patch('matplotlib.pyplot.savefig')
    def test_generate_weekly_report(self, mock_savefig):
        """Test generating a weekly report."""
        # Mock the metrics_collector's get_weekly_metrics method
        self.mock_metrics_collector.get_weekly_metrics.return_value = {
            'start_date': '2025-03-09',
            'end_date': '2025-03-15',
            'total_engagement': 570,
            'total_impressions': 5700,
            'total_posts': 11,
            'platforms': {
                'facebook': {
                    'total_engagement': 190,
                    'total_impressions': 1900,
                    'total_posts': 4,
                    'daily_engagement': {
                        '2025-03-14': 90,
                        '2025-03-15': 100
                    }
                },
                'twitter': {
                    'total_engagement': 380,
                    'total_impressions': 3800,
                    'total_posts': 7,
                    'daily_engagement': {
                        '2025-03-14': 180,
                        '2025-03-15': 200
                    }
                }
            }
        }
        
        # Mock the metrics_collector's get_best_performing_posts method
        self.mock_metrics_collector.get_best_performing_posts.return_value = [
            {'platform': 'twitter', 'post_id': 'tw1', 'engagement': 120, 'text': 'Best tweet'},
            {'platform': 'facebook', 'post_id': 'fb2', 'engagement': 80, 'text': 'Popular post'}
        ]
        
        # Mock the chart generation methods
        self.report_generator._generate_engagement_chart = MagicMock(
            return_value=os.path.join(self.test_charts_dir, 'engagement_chart.png')
        )
        
        self.report_generator._generate_platform_comparison_chart = MagicMock(
            return_value=os.path.join(self.test_charts_dir, 'platform_comparison.png')
        )
        
        # Create dummy chart files
        with open(os.path.join(self.test_charts_dir, 'engagement_chart.png'), 'w') as f:
            f.write('dummy chart')
        
        with open(os.path.join(self.test_charts_dir, 'platform_comparison.png'), 'w') as f:
            f.write('dummy chart')
        
        # Test with a specific date
        week_end_date = datetime.date(2025, 3, 15)
        
        result = self.report_generator.generate_weekly_report(week_end_date)
        
        self.assertTrue(result['success'])
        self.assertIn('title', result)
        self.assertIn('summary', result)
        self.assertIn('platform_performance', result)
        self.assertIn('best_performing_posts', result)
        self.assertIn('charts', result)
        self.assertIn('recommendations', result)
        
        # Check that the report contains the expected data
        self.assertEqual(result['summary']['total_engagement'], 570)
        self.assertEqual(result['summary']['total_impressions'], 5700)
        self.assertEqual(result['summary']['total_posts'], 11)
        
        # Check that platform performance data is included
        self.assertIn('facebook', result['platform_performance'])
        self.assertIn('twitter', result['platform_performance'])
        
        # Check that the report file was created
        report_file = os.path.join(self.test_reports_dir, 'weekly_report_20250309_to_20250315.json')
        self.assertTrue(os.path.exists(report_file))

    @patch('matplotlib.pyplot.savefig')
    def test_generate_platform_report(self, mock_savefig):
        """Test generating a platform-specific report."""
        # Mock the metrics_collector's get_platform_growth method
        self.mock_metrics_collector.get_platform_growth.return_value = {
            'platform': 'instagram',
            'start_date': '2025-03-01',
            'end_date': '2025-03-31',
            'start_followers': 1000,
            'end_followers': 1200,
            'follower_growth': 200,
            'follower_growth_percent': 20.0,
            'total_engagement': 1500,
            'total_impressions': 15000,
            'total_posts': 20,
            'daily_metrics': [
                {'date': '2025-03-01', 'metrics': {'engagement': 40, 'followers': 1000}},
                {'date': '2025-03-15', 'metrics': {'engagement': 50, 'followers': 1100}},
                {'date': '2025-03-31', 'metrics': {'engagement': 60, 'followers': 1200}}
            ]
        }
        
        # Mock the metrics_collector's get_best_performing_posts method
        self.mock_metrics_collector.get_best_performing_posts.return_value = [
            {'platform': 'instagram', 'post_id': 'ig1', 'engagement': 100, 'text': 'Popular post'},
            {'platform': 'instagram', 'post_id': 'ig2', 'engagement': 90, 'text': 'Another good post'}
        ]
        
        # Mock the chart generation method
        self.report_generator._generate_platform_trend_chart = MagicMock(
            return_value=os.path.join(self.test_charts_dir, 'platform_trend.png')
        )
        
        # Create dummy chart file
        with open(os.path.join(self.test_charts_dir, 'platform_trend.png'), 'w') as f:
            f.write('dummy chart')
        
        # Test with specific dates
        start_date <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>