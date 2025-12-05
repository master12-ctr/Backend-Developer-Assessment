
from django.test import TestCase
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from django.utils import timezone
from datetime import timedelta

class ModelTests(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.country = Country.objects.create(
            name="Test Country",
            code="TC"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.blog = Blog.objects.create(
            title="Test Blog",
            content="Test content",
            author=self.user,
            country=self.country
        )
    
    def test_country_creation(self):
        """Test country model creation"""
        self.assertEqual(str(self.country), "Test Country (TC)")
        self.assertEqual(Country.objects.count(), 1)
    
    def test_blog_creation(self):
        """Test blog model creation"""
        self.assertEqual(str(self.blog), "Test Blog")
        self.assertEqual(self.blog.author, self.user)
        self.assertEqual(self.blog.country, self.country)
    
    def test_blog_view_creation(self):
        """Test blog view model creation"""
        blog_view = BlogView.objects.create(
            blog=self.blog,
            user=self.user,
            country=self.country,
            viewed_at=timezone.now(),
            duration=60
        )
        
        self.assertTrue(str(blog_view).startswith("Test Blog viewed at"))
        self.assertEqual(BlogView.objects.count(), 1)
    
    def test_blog_view_str_method(self):
        """Test string representation of BlogView"""
        blog_view = BlogView.objects.create(
            blog=self.blog,
            user=self.user,
            country=self.country,
            viewed_at=timezone.make_aware(timezone.datetime(2025, 12, 4, 10, 30)),
            duration=60
        )
        
        self.assertIn("Test Blog viewed at 2025", str(blog_view))