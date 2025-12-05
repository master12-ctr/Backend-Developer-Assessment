# analytics_app/tests/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from django.utils import timezone
from datetime import timedelta
import json

class APIViewTests(TestCase):
    
    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        
        # Create test data
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        
        self.blog = Blog.objects.create(
            title="Test Blog",
            content="Test content",
            author=self.user,
            country=self.country
        )
        
        # Create some views
        for i in range(3):
            BlogView.objects.create(
                blog=self.blog,
                user=self.user,
                country=self.country,
                viewed_at=timezone.now() - timedelta(days=i),
                duration=60
            )
    
    def test_blog_views_api_success(self):
        """Test successful API call for blog views"""
        response = self.client.get('/analytics/blog-views/', {
            'object_type': 'country',
            'range': 'month'
        })
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Check if response has expected structure
        self.assertIn('data', response_data)
        
        # For paginated response, check for pagination keys
        if 'object_type' in response_data:
            self.assertEqual(response_data['object_type'], 'country')
        # If it's a paginated response with metadata, check those
        elif 'data' in response_data:
            # Just check that we got data back
            self.assertIsInstance(response_data['data'], list)
    
    def test_blog_views_api_invalid_object_type(self):
        """Test API with invalid object_type"""
        response = self.client.get('/analytics/blog-views/', {
            'object_type': 'invalid',
            'range': 'month'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
    
    def test_top_analytics_api(self):
        """Test top analytics API"""
        response = self.client.get('/analytics/top/', {
            'top': 'user'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())
        self.assertEqual(response.json()['top_type'], 'user')
    
    def test_performance_analytics_api(self):
        """Test performance analytics API"""
        response = self.client.get('/analytics/performance/', {
            'compare': 'month'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json())
        self.assertEqual(response.json()['compare'], 'month')
    
    def test_api_with_filters(self):
        """Test API with JSON filters"""
        filters = json.dumps({
            'operator': 'and',
            'conditions': [{
                'field': 'country__name',
                'operator': 'eq',
                'value': 'Test Country'
            }]
        })
        
        response = self.client.get('/analytics/blog-views/', {
            'object_type': 'country',
            'filters': filters
        })
        
        self.assertEqual(response.status_code, 200)
    
    def test_api_pagination(self):
        """Test API pagination"""
        response = self.client.get('/analytics/blog-views/', {
            'object_type': 'country',
            'limit': 10,
            'offset': 0
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Check if pagination fields exist
        response_data = response.json()
        self.assertIn('count', response_data)
        self.assertIn('limit', response_data)
        self.assertIn('offset', response_data)