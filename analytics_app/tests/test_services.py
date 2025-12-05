
from django.test import TestCase
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from analytics_app.services import AnalyticsService
from django.utils import timezone
from datetime import timedelta
import json

class AnalyticsServiceTests(TestCase):
    
    def setUp(self):
        """Set up test data for analytics services"""
        # Create countries
        self.country1 = Country.objects.create(name="Country 1", code="C1")
        self.country2 = Country.objects.create(name="Country 2", code="C2")
        
        # Create users
        self.user1 = User.objects.create_user(
            username="user1",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", 
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        
        # Create blogs
        self.blog1 = Blog.objects.create(
            title="Blog 1",
            content="Content 1",
            author=self.user1,
            country=self.country1
        )
        self.blog2 = Blog.objects.create(
            title="Blog 2",
            content="Content 2", 
            author=self.user2,
            country=self.country2
        )
        
        # Create blog views
        now = timezone.now()
        
        # Recent views (last 30 days)
        for i in range(5):
            BlogView.objects.create(
                blog=self.blog1,
                user=self.user1,
                country=self.country1,
                viewed_at=now - timedelta(days=i),
                duration=60
            )
        
        # Older views
        for i in range(3):
            BlogView.objects.create(
                blog=self.blog2,
                user=self.user2,
                country=self.country2,
                viewed_at=now - timedelta(days=60 + i),
                duration=120
            )
    
    def test_get_blog_views_analytics_by_country(self):
        """Test grouping blog views by country"""
        result = AnalyticsService.get_blog_views_analytics('country', 'month')
        result_list = list(result)
        
        # Should have data for countries with recent views
        self.assertEqual(len(result_list), 1)  # Only country1 has recent views
        
        if result_list:
            self.assertEqual(result_list[0]['x'], 'Country 1')
            self.assertEqual(result_list[0]['y'], 1)  # 1 unique blog
            self.assertEqual(result_list[0]['z'], 5)  # 5 total views
    
    def test_get_blog_views_analytics_by_user(self):
        """Test grouping blog views by user"""
        result = AnalyticsService.get_blog_views_analytics('user', 'all')
        result_list = list(result)
        
        # Should have data for both users
        self.assertEqual(len(result_list), 2)
        
        # Sort by views descending
        result_list.sort(key=lambda x: x['z'], reverse=True)
        
        self.assertEqual(result_list[0]['x'], 'John Doe')
        self.assertEqual(result_list[0]['y'], 1)  # 1 unique blog
        self.assertEqual(result_list[0]['z'], 5)  # 5 total views
    
    def test_get_top_analytics_users(self):
        """Test top users analytics"""
        result = AnalyticsService.get_top_analytics('user', 'month')
        result_list = list(result)
        
        self.assertEqual(len(result_list), 1)  # Only one user with recent views
        self.assertEqual(result_list[0]['x'], 'John Doe')
    
    def test_get_performance_analytics_monthly(self):
        """Test monthly performance analytics"""
        result = AnalyticsService.get_performance_analytics('month')
        
        # Should return time-series data
        self.assertIsInstance(result, list)
        
        # Should have growth percentages
        if len(result) > 1:
            self.assertIn('z', result[1])  # Growth percentage