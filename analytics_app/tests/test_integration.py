# analytics_app/tests/test_integration.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from django.utils import timezone
from datetime import timedelta
import json

class IntegrationTests(TestCase):
    
    def setUp(self):
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
    
    def test_swagger_docs(self):
        """Test Swagger documentation endpoints"""
        urls = [
            '/swagger/',
            '/redoc/',
            '/swagger/?format=json',
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302], 
                         f"Failed for {url}: {response.status_code}")
    
    def test_all_api_endpoints(self):
        """Test all API endpoints with valid parameters"""
        test_cases = [
            {
                'url': '/analytics/blog-views/',
                'params': {'object_type': 'country', 'range': 'month'}
            },
            {
                'url': '/analytics/blog-views/',
                'params': {'object_type': 'user', 'range': 'month'}
            },
            {
                'url': '/analytics/top/',
                'params': {'top': 'user'}
            },
            {
                'url': '/analytics/top/',
                'params': {'top': 'country'}
            },
            {
                'url': '/analytics/top/',
                'params': {'top': 'blog'}
            },
            {
                'url': '/analytics/performance/',
                'params': {'compare': 'month'}
            },
            {
                'url': '/analytics/performance/',
                'params': {'compare': 'week'}
            },
        ]
        
        for test_case in test_cases:
            response = self.client.get(test_case['url'], test_case['params'])
            # Should return 200 (with data) or 404 (no data but valid endpoint)
            self.assertIn(response.status_code, [200, 404],
                         f"Failed for {test_case['url']} with {test_case['params']}")
    
    def test_api_validation(self):
        """Test API validation with invalid parameters"""
        test_cases = [
            {
                'url': '/analytics/blog-views/',
                'params': {'object_type': 'invalid'},
                'expected_status': 400
            },
            {
                'url': '/analytics/top/',
                'params': {'top': 'invalid'},
                'expected_status': 400
            },
            {
                'url': '/analytics/performance/',
                'params': {'compare': 'invalid'},
                'expected_status': 400
            },
        ]
        
        for test_case in test_cases:
            response = self.client.get(test_case['url'], test_case['params'])
            self.assertEqual(response.status_code, test_case['expected_status'],
                           f"Failed for {test_case['url']} with {test_case['params']}")