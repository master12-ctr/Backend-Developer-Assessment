
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Load comprehensive sample data for testing all features'
    
    def handle(self, *args, **options):
        self.stdout.write("Loading comprehensive sample data...")
        
        # Create test users
        users = []
        for i in range(1, 11):
            user, created = User.objects.get_or_create(
                username=f'testuser{i}',
                defaults={
                    'email': f'test{i}@example.com',
                    'first_name': f'Test{i}',
                    'last_name': 'User',
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
        
        # Create test countries
        countries = []
        country_data = [
            {'name': 'United States', 'code': 'US'},
            {'name': 'United Kingdom', 'code': 'GB'},
            {'name': 'Canada', 'code': 'CA'},
            {'name': 'Australia', 'code': 'AU'},
            {'name': 'Germany', 'code': 'DE'},
            {'name': 'France', 'code': 'FR'},
            {'name': 'Japan', 'code': 'JP'},
            {'name': 'India', 'code': 'IN'},
            {'name': 'Brazil', 'code': 'BR'},
            {'name': 'South Africa', 'code': 'ZA'},
        ]
        
        for data in country_data:
            country, created = Country.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            countries.append(country)
        
        # Create test blogs with realistic data
        blogs = []
        blog_titles = [
            'Getting Started with Django REST Framework',
            'Advanced Python Patterns and Techniques',
            'Building Scalable APIs with Django',
            'Machine Learning for Web Developers',
            'Data Visualization with Python and D3.js',
            'Microservices Architecture Best Practices',
            'DevOps for Django Applications',
            'React and Django: Full Stack Development',
            'Database Optimization Strategies',
            'Security Best Practices for Web APIs',
            'Testing Django Applications',
            'Deploying Django with Docker and Kubernetes',
            'Real-time Applications with Django Channels',
            'GraphQL vs REST: Choosing the Right API',
            'Performance Monitoring and Optimization',
        ]
        
        for i, title in enumerate(blog_titles):
            blog = Blog.objects.create(
                title=title,
                content=f"This is a detailed article about {title}. " * 20,
                author=random.choice(users),
                country=random.choice(countries),
                created_at=timezone.now() - timedelta(days=random.randint(0, 365))
            )
            blogs.append(blog)
        
        # Create realistic blog views with patterns
        total_views = 0
        now = timezone.now()
        
        # Create daily view patterns (more views on weekdays)
        for day_offset in range(90):  # Last 90 days
            view_date = now - timedelta(days=day_offset)
            day_of_week = view_date.weekday()  # Monday=0, Sunday=6
            
            # More views on weekdays
            if day_of_week < 5:  # Weekday
                daily_views = random.randint(20, 50)
            else:  # Weekend
                daily_views = random.randint(5, 15)
            
            for _ in range(daily_views):
                # Create view at a random time during the day
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                viewed_at = view_date.replace(
                    hour=hour,
                    minute=minute,
                    second=second,
                    microsecond=0
                )
                
                BlogView.objects.create(
                    blog=random.choice(blogs),
                    user=random.choice(users + [None]),  # Some anonymous views
                    country=random.choice(countries),
                    viewed_at=viewed_at,
                    duration=random.randint(30, 600)  # 30 seconds to 10 minutes
                )
                total_views += 1
        
        # Create API request logs for monitoring
        from analytics_app.monitoring.models import APIRequestLog
        
        # Create sample API logs for the last 30 days
        for day_offset in range(30):
            log_date = now - timedelta(days=day_offset)
            
            # Create varying number of logs per day
            logs_per_day = random.randint(50, 200)
            
            for i in range(logs_per_day):
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                
                request_time = log_date.replace(
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0
                )
                
                # Random API endpoint
                endpoints = [
                    '/analytics/blog-views/',
                    '/analytics/top/',
                    '/analytics/performance/',
                ]
                
                # Random status codes (mostly 200, some errors)
                if random.random() < 0.95:  # 95% success rate
                    status_code = 200
                else:
                    status_code = random.choice([400, 401, 403, 404, 500])
                
                APIRequestLog.objects.create(
                    request_id=f"test-{day_offset}-{i}",
                    method=random.choice(['GET', 'GET', 'GET']),  # Mostly GET
                    path=random.choice(endpoints),
                    query_params={'object_type': 'country', 'range': 'month'},
                    status_code=status_code,
                    user=random.choice(users + [None]),
                    client_ip=f"192.168.1.{random.randint(1, 255)}",
                    user_agent="Mozilla/5.0 (Test User Agent)",
                    request_time=request_time,
                    response_time=request_time + timedelta(milliseconds=random.randint(50, 500)),
                    duration_ms=random.randint(50, 500)
                )
        
        self.stdout.write(self.style.SUCCESS(
            f"✓ Successfully loaded comprehensive sample data:\n"
            f"  - {len(users)} users\n"
            f"  - {len(countries)} countries\n"
            f"  - {len(blogs)} blogs\n"
            f"  - {total_views:,} blog views\n"
            f"  - {APIRequestLog.objects.count():,} API request logs"
        ))
        self.stdout.write("\nSample credentials:")
        self.stdout.write("  - Username: testuser1")
        self.stdout.write("  - Password: testpass123")
        self.stdout.write("\nAccess APIs at: http://localhost:8000/analytics/")
        self.stdout.write("Swagger docs: http://localhost:8000/swagger/")