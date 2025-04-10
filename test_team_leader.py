"""
Unit tests for the Team Leader module.

This module contains unit tests for the TeamLeader class and its components.
"""

import unittest
import os
import sys
import datetime
from unittest.mock import MagicMock, patch

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.team_leader.team_leader import TeamLeader
from src.team_leader.scheduler import Scheduler
from src.team_leader.analytics import Analytics
from src.team_leader.report_generator import TeamReportGenerator


class TestTeamLeader(unittest.TestCase):
    """Test cases for the TeamLeader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_platform_agents = {
            'facebook': MagicMock(),
            'twitter': MagicMock(),
            'instagram': MagicMock(),
            'tiktok': MagicMock()
        }
        
        self.mock_llm = MagicMock()
        self.mock_image_generator = MagicMock()
        
        self.team_leader = TeamLeader(
            platform_agents=self.mock_platform_agents,
            text_llm=self.mock_llm,
            image_generator=self.mock_image_generator
        )

    def test_initialization(self):
        """Test that TeamLeader initializes correctly."""
        self.assertIsNotNone(self.team_leader)
        self.assertIsNotNone(self.team_leader.scheduler)
        self.assertIsNotNone(self.team_leader.analytics)
        self.assertIsNotNone(self.team_leader.report_generator)
        self.assertEqual(len(self.team_leader.platform_agents), 4)

    def test_assign_task(self):
        """Test task assignment to platform agents."""
        # Mock the platform agent's post_content method
        self.mock_platform_agents['facebook'].post_content.return_value = {
            'success': True,
            'post_id': '12345'
        }
        
        result = self.team_leader.assign_task(
            platform='facebook',
            task_type='post',
            content={'text': 'Test post'},
            schedule_time=None
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'facebook')
        self.assertEqual(result['task_type'], 'post')
        self.mock_platform_agents['facebook'].post_content.assert_called_once()

    def test_generate_weekly_report(self):
        """Test weekly report generation."""
        # Mock the report generator's generate_weekly_report method
        self.team_leader.report_generator.generate_weekly_report = MagicMock(return_value={
            'success': True,
            'report': 'Weekly report content'
        })
        
        result = self.team_leader.generate_weekly_report()
        
        self.assertTrue(result['success'])
        self.assertIn('report', result)
        self.team_leader.report_generator.generate_weekly_report.assert_called_once()

    def test_get_platform_performance(self):
        """Test getting platform performance metrics."""
        # Mock the analytics' get_platform_performance method
        self.team_leader.analytics.get_platform_performance = MagicMock(return_value={
            'engagement': 100,
            'impressions': 1000,
            'followers': 500
        })
        
        result = self.team_leader.get_platform_performance('facebook')
        
        self.assertEqual(result['engagement'], 100)
        self.assertEqual(result['impressions'], 1000)
        self.assertEqual(result['followers'], 500)
        self.team_leader.analytics.get_platform_performance.assert_called_once_with('facebook')

    @patch('src.team_leader.team_leader.datetime')
    def test_schedule_content(self, mock_datetime):
        """Test content scheduling."""
        # Mock datetime.now to return a fixed date
        mock_now = datetime.datetime(2025, 3, 21, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        
        # Mock the scheduler's schedule_task method
        self.team_leader.scheduler.schedule_task = MagicMock(return_value={
            'success': True,
            'task_id': '12345',
            'scheduled_time': mock_now + datetime.timedelta(days=1)
        })
        
        result = self.team_leader.schedule_content(
            platform='instagram',
            content={'text': 'Scheduled post', 'image': 'image.jpg'},
            schedule_time=mock_now + datetime.timedelta(days=1)
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['platform'], 'instagram')
        self.assertEqual(result['task_id'], '12345')
        self.team_leader.scheduler.schedule_task.assert_called_once()


class TestScheduler(unittest.TestCase):
    """Test cases for the Scheduler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.scheduler = Scheduler()

    def test_initialization(self):
        """Test that Scheduler initializes correctly."""
        self.assertIsNotNone(self.scheduler)
        self.assertEqual(len(self.scheduler.scheduled_tasks), 0)

    def test_schedule_task(self):
        """Test scheduling a task."""
        task = {
            'platform': 'twitter',
            'content': {'text': 'Scheduled tweet'},
            'task_type': 'post'
        }
        
        schedule_time = datetime.datetime.now() + datetime.timedelta(hours=2)
        
        result = self.scheduler.schedule_task(task, schedule_time)
        
        self.assertTrue(result['success'])
        self.assertIn('task_id', result)
        self.assertEqual(len(self.scheduler.scheduled_tasks), 1)
        self.assertEqual(self.scheduler.scheduled_tasks[0]['platform'], 'twitter')

    def test_get_pending_tasks(self):
        """Test getting pending tasks."""
        # Add some tasks
        task1 = {
            'platform': 'facebook',
            'content': {'text': 'Task 1'},
            'task_type': 'post'
        }
        
        task2 = {
            'platform': 'instagram',
            'content': {'text': 'Task 2', 'image': 'image.jpg'},
            'task_type': 'post'
        }
        
        now = datetime.datetime.now()
        past_time = now - datetime.timedelta(hours=1)
        future_time = now + datetime.timedelta(hours=1)
        
        self.scheduler.schedule_task(task1, past_time)
        self.scheduler.schedule_task(task2, future_time)
        
        pending_tasks = self.scheduler.get_pending_tasks()
        
        self.assertEqual(len(pending_tasks), 1)
        self.assertEqual(pending_tasks[0]['platform'], 'facebook')


class TestAnalytics(unittest.TestCase):
    """Test cases for the Analytics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_platform_agents = {
            'facebook': MagicMock(),
            'twitter': MagicMock(),
            'instagram': MagicMock(),
            'tiktok': MagicMock()
        }
        
        self.analytics = Analytics(platform_agents=self.mock_platform_agents)

    def test_initialization(self):
        """Test that Analytics initializes correctly."""
        self.assertIsNotNone(self.analytics)
        self.assertEqual(len(self.analytics.platform_agents), 4)

    def test_get_platform_performance(self):
        """Test getting platform performance metrics."""
        # Mock the platform agent's get_metrics method
        self.mock_platform_agents['twitter'].get_metrics.return_value = {
            'engagement': 250,
            'impressions': 2500,
            'followers': 1000,
            'posts': 5
        }
        
        result = self.analytics.get_platform_performance('twitter')
        
        self.assertEqual(result['engagement'], 250)
        self.assertEqual(result['impressions'], 2500)
        self.assertEqual(result['followers'], 1000)
        self.mock_platform_agents['twitter'].get_metrics.assert_called_once()

    def test_get_overall_performance(self):
        """Test getting overall performance metrics across all platforms."""
        # Mock the platform agents' get_metrics methods
        self.mock_platform_agents['facebook'].get_metrics.return_value = {
            'engagement': 100,
            'impressions': 1000,
            'followers': 500,
            'posts': 3
        }
        
        self.mock_platform_agents['twitter'].get_metrics.return_value = {
            'engagement': 250,
            'impressions': 2500,
            'followers': 1000,
            'posts': 5
        }
        
        self.mock_platform_agents['instagram'].get_metrics.return_value = {
            'engagement': 300,
            'impressions': 3000,
            'followers': 1500,
            'posts': 4
        }
        
        self.mock_platform_agents['tiktok'].get_metrics.return_value = {
            'engagement': 400,
            'impressions': 4000,
            'followers': 2000,
            'posts': 2
        }
        
        result = self.analytics.get_overall_performance()
        
        self.assertEqual(result['total_engagement'], 1050)
        self.assertEqual(result['total_impressions'], 10500)
        self.assertEqual(result['total_followers'], 5000)
        self.assertEqual(result['total_posts'], 14)
        self.assertEqual(result['engagement_per_post'], 75)  # 1050/14


class TestTeamReportGenerator(unittest.TestCase):
    """Test cases for the TeamReportGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_analytics = MagicMock()
        self.report_generator = TeamReportGenerator(analytics=self.mock_analytics)

    def test_initialization(self):
        """Test that TeamReportGenerator initializes correctly."""
        self.assertIsNotNone(self.report_generator)
        self.assertIsNotNone(self.report_generator.analytics)

    def test_generate_weekly_report(self):
        """Test generating a weekly report."""
        # Mock the analytics' get_overall_performance method
        self.mock_analytics.get_overall_performance.return_value = {
            'total_engagement': 1050,
            'total_impressions': 10500,
            'total_followers': 5000,
            'total_posts': 14,
            'engagement_per_post': 75,
            'platforms': {
                'facebook': {'engagement': 100, 'impressions': 1000, 'followers': 500, 'posts': 3},
                'twitter': {'engagement': 250, 'impressions': 2500, 'followers': 1000, 'posts': 5},
                'instagram': {'engagement': 300, 'impressions': 3000, 'followers': 1500, 'posts': 4},
                'tiktok': {'engagement': 400, 'impressions': 4000, 'followers': 2000, 'posts': 2}
            }
        }
        
        # Mock the analytics' get_best_performing_posts method
        self.mock_analytics.get_best_performing_posts.return_value = [
            {'platform': 'tiktok', 'engagement': 200, 'content': 'Best post 1'},
            {'platform': 'instagram', 'engagement': 150, 'content': 'Best post 2'},
            {'platform': 'twitter', 'engagement': 100, 'content': 'Best post 3'}
        ]
        
        result = self.report_generator.generate_weekly_report()
        
        self.assertTrue(result['success'])
        self.assertIn('report', result)
        self.assertIn('summary', result['report'])
        self.assertIn('platform_performance', result['report'])
        self.assertIn('best_performing_posts', result['report'])
        self.assertIn('recommendations', result['report'])
        self.mock_analytics.get_overall_performance.assert_called_once()
        self.mock_analytics.get_best_performing_posts.assert_called_once()


if __name__ == '__main__':
    unittest.main()
