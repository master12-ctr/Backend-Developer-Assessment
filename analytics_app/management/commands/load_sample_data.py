# analytics_app/management/commands/load_sample_data.py
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from django.utils import timezone
import random
import uuid

class Command(BaseCommand):
    help = 'Load comprehensive sample data for testing all features'
    
    def handle(self, *args, **options):
        self.stdout.write("Loading comprehensive sample data...")
        
        # Check if monitoring models are available
        try:
            from analytics_app.monitoring.models import APIRequestLog
            monitoring_available = True
        except ImportError:
            monitoring_available = False
            self.stdout.write(self.style.WARNING(
                "Monitoring models not available. Skipping API request logs."
            ))
        
        # Clear existing data
        self.stdout.write("Clearing existing data...")
        BlogView.objects.all().delete()
        Blog.objects.all().delete()
        Country.objects.all().delete()
        
        # Don't delete superusers
        User.objects.filter(is_superuser=False).delete()
        
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
            self.stdout.write(f"Created user: {user.username}")
        
        # Create test countries with realistic data
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
            {'name': 'Netherlands', 'code': 'NL'},
            {'name': 'Italy', 'code': 'IT'},
            {'name': 'Spain', 'code': 'ES'},
            {'name': 'Mexico', 'code': 'MX'},
            {'name': 'China', 'code': 'CN'},
        ]
        
        for data in country_data:
            country, created = Country.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            countries.append(country)
            self.stdout.write(f"Created country: {country.name} ({country.code})")
        
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
            'Django ORM Deep Dive',
            'Async Django with ASGI',
            'Building REST APIs with Django Ninja',
            'Caching Strategies for High-Traffic Sites',
            'Authentication and Authorization in Django',
        ]
        
        for i, title in enumerate(blog_titles):
            # Create blogs with varied creation dates
            days_ago = random.randint(0, 365)
            created_at = timezone.now() - timedelta(days=days_ago)
            
            blog = Blog.objects.create(
                title=title,
                content=self._generate_blog_content(title),
                author=random.choice(users),
                country=random.choice(countries),
                created_at=created_at
            )
            blogs.append(blog)
            if i < 5:  # Show first 5 for logging
                self.stdout.write(f"Created blog: {title}")
        
        self.stdout.write(f"Created {len(blogs)} blogs total")
        
        # Create realistic blog views with patterns
        total_views = 0
        now = timezone.now()
        
        self.stdout.write("Creating blog views...")
        
        # Create daily view patterns (more views on weekdays, recent days have more views)
        for day_offset in range(120):  # Last 120 days
            view_date = now - timedelta(days=day_offset)
            day_of_week = view_date.weekday()  # Monday=0, Sunday=6
            
            # More views on weekdays and recent days
            base_views = 15
            if day_of_week < 5:  # Weekday
                base_views += random.randint(10, 30)
            else:  # Weekend
                base_views += random.randint(5, 15)
            
            # More views for recent content (exponential decay)
            decay_factor = max(0.1, 1.0 - (day_offset / 120))
            daily_views = int(base_views * decay_factor)
            
            # Ensure at least some views for each day
            daily_views = max(3, daily_views)
            
            for _ in range(daily_views):
                # Create view at a random time during the day
                hour = random.randint(8, 22)  # Mostly during waking hours
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                
                viewed_at = view_date.replace(
                    hour=hour,
                    minute=minute,
                    second=second,
                    microsecond=0
                )
                
                # Some blogs are more popular than others
                blog = random.choices(
                    blogs,
                    weights=[random.uniform(0.5, 2.0) for _ in blogs]
                )[0]
                
                # 70% logged in users, 30% anonymous
                if random.random() < 0.7:
                    user = random.choice(users)
                else:
                    user = None
                
                BlogView.objects.create(
                    blog=blog,
                    user=user,
                    country=random.choice(countries),
                    viewed_at=viewed_at,
                    duration=random.randint(30, 1200)  # 30 seconds to 20 minutes
                )
                total_views += 1
            
            # Progress indicator
            if day_offset % 20 == 0:
                self.stdout.write(f"  Created views for day {day_offset}/120")
        
        self.stdout.write(f"Created {total_views:,} blog views")
        
        # Create API request logs for monitoring (if available)
        if monitoring_available:
            self.stdout.write("Creating API request logs...")
            
            # Create sample API logs for the last 30 days
            api_endpoints = [
                {'path': '/analytics/blog-views/', 'methods': ['GET']},
                {'path': '/analytics/top/', 'methods': ['GET']},
                {'path': '/analytics/performance/', 'methods': ['GET']},
                {'path': '/admin/', 'methods': ['GET']},
                {'path': '/swagger/', 'methods': ['GET']},
            ]
            
            api_log_count = 0
            for day_offset in range(30):
                log_date = now - timedelta(days=day_offset)
                
                # More logs on weekdays
                day_of_week = log_date.weekday()
                if day_of_week < 5:  # Weekday
                    logs_per_day = random.randint(50, 150)
                else:  # Weekend
                    logs_per_day = random.randint(10, 40)
                
                for i in range(logs_per_day):
                    hour = random.randint(0, 23)
                    minute = random.randint(0, 59)
                    
                    request_time = log_date.replace(
                        hour=hour,
                        minute=minute,
                        second=random.randint(0, 59),
                        microsecond=0
                    )
                    
                    endpoint = random.choice(api_endpoints)
                    method = random.choice(endpoint['methods'])
                    path = endpoint['path']
                    
                    # Random status codes (mostly 200, some errors)
                    if random.random() < 0.92:  # 92% success rate
                        status_code = 200
                    elif random.random() < 0.7:
                        status_code = random.choice([400, 401, 403])
                    else:
                        status_code = random.choice([404, 500, 502])
                    
                    # Add query parameters for analytics endpoints
                    query_params = {}
                    if path.startswith('/analytics/'):
                        if path == '/analytics/blog-views/':
                            query_params = {
                                'object_type': random.choice(['country', 'user']),
                                'range': random.choice(['month', 'week', 'year', ''])
                            }
                        elif path == '/analytics/top/':
                            query_params = {
                                'top': random.choice(['user', 'country', 'blog'])
                            }
                        elif path == '/analytics/performance/':
                            query_params = {
                                'compare': random.choice(['month', 'week', 'day', 'year'])
                            }
                    
                    # Random duration (50-500ms for success, 100-1000ms for errors)
                    if status_code == 200:
                        duration_ms = random.randint(50, 300)
                    else:
                        duration_ms = random.randint(100, 800)
                    
                    response_time = request_time + timedelta(milliseconds=duration_ms)
                    
                    # Create log entry
                    APIRequestLog.objects.create(
                        request_id=uuid.uuid4(),  # Proper UUID
                        method=method,
                        path=path,
                        query_params=query_params if query_params else None,
                        request_body=None,
                        status_code=status_code,
                        response_body=None,
                        user=random.choice(users + [None]),
                        client_ip=f"192.168.1.{random.randint(1, 255)}",
                        user_agent=self._get_random_user_agent(),
                        request_time=request_time,
                        response_time=response_time,
                        duration_ms=duration_ms
                    )
                    api_log_count += 1
                
                # Progress indicator
                if day_offset % 5 == 0:
                    self.stdout.write(f"  Created API logs for day {day_offset}/30")
            
            self.stdout.write(f"Created {api_log_count:,} API request logs")
        
        # Create test summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✓ SUCCESSFULLY LOADED SAMPLE DATA"))
        self.stdout.write("="*60)
        self.stdout.write(f"📊 Users: {len(users)} test users")
        self.stdout.write(f"🌍 Countries: {len(countries)} countries")
        self.stdout.write(f"📝 Blogs: {len(blogs)} blog posts")
        self.stdout.write(f"👁️ Views: {total_views:,} blog views")
        if monitoring_available:
            api_log_count = APIRequestLog.objects.count()
            self.stdout.write(f"📡 API Logs: {api_log_count:,} request logs")
        
        # Test credentials and URLs
        self.stdout.write("\n🔐 TEST CREDENTIALS:")
        self.stdout.write("  Username: testuser1")
        self.stdout.write("  Password: testpass123")
        
        self.stdout.write("\n🔗 TEST ENDPOINTS:")
        self.stdout.write("  API #1 - Blog Views by Country:")
        self.stdout.write("    http://localhost:8000/analytics/blog-views/?object_type=country&range=month")
        self.stdout.write("  API #1 - Blog Views by User:")
        self.stdout.write("    http://localhost:8000/analytics/blog-views/?object_type=user&range=month")
        self.stdout.write("  API #2 - Top Users:")
        self.stdout.write("    http://localhost:8000/analytics/top/?top=user")
        self.stdout.write("  API #2 - Top Countries:")
        self.stdout.write("    http://localhost:8000/analytics/top/?top=country")
        self.stdout.write("  API #2 - Top Blogs:")
        self.stdout.write("    http://localhost:8000/analytics/top/?top=blog")
        self.stdout.write("  API #3 - Monthly Performance:")
        self.stdout.write("    http://localhost:8000/analytics/performance/?compare=month")
        self.stdout.write("  API #3 - Weekly Performance:")
        self.stdout.write("    http://localhost:8000/analytics/performance/?compare=week")
        
        self.stdout.write("\n📚 DOCUMENTATION:")
        self.stdout.write("  Swagger UI: http://localhost:8000/swagger/")
        self.stdout.write("  ReDoc: http://localhost:8000/redoc/")
        self.stdout.write("  Admin: http://localhost:8000/admin/")
        
        self.stdout.write("\n🧪 RUN TESTS:")
        self.stdout.write("  python manage.py test analytics_app")
        self.stdout.write("  python manage.py run_performance_tests")
        
        self.stdout.write("\n🎯 SAMPLE FILTERS TO TEST:")
        self.stdout.write('  {"operator":"and","conditions":[{"field":"blog__title","operator":"contains","value":"Django"}]}')
        self.stdout.write('  {"operator":"or","conditions":[{"field":"country__name","operator":"eq","value":"United States"},{"field":"country__name","operator":"eq","value":"United Kingdom"}]}')
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ Sample data ready for testing!"))
        self.stdout.write("="*60)
    
    def _generate_blog_content(self, title):
        """Generate realistic blog content"""
        sections = [
            f"# {title}\n\n",
            "## Introduction\n\n",
            "In this comprehensive article, we will explore various aspects of the topic. "
            "This guide is designed for developers of all skill levels.\n\n",
            "## Key Concepts\n\n",
            "Understanding the fundamentals is crucial for mastering this subject. "
            "We'll cover the essential concepts that form the foundation.\n\n",
            "### Section 1: Core Principles\n\n",
            "The core principles include scalability, maintainability, and performance. "
            "Each of these plays a vital role in building robust applications.\n\n",
            "### Section 2: Best Practices\n\n",
            "Following industry best practices ensures code quality and reduces technical debt. "
            "We'll discuss patterns and anti-patterns to watch out for.\n\n",
            "## Implementation Examples\n\n",
            "Let's look at some practical examples to solidify our understanding. "
            "These examples demonstrate real-world applications of the concepts discussed.\n\n",
            "```python\n# Example code snippet\ndef example_function():\n    return \"Hello, World!\"\n```\n\n",
            "## Performance Considerations\n\n",
            "Performance optimization is key for production applications. "
            "We'll explore techniques for improving efficiency and reducing latency.\n\n",
            "## Conclusion\n\n",
            "Mastering this topic requires practice and continuous learning. "
            "The concepts covered here provide a solid foundation for further exploration.\n\n",
            "## Further Reading\n\n",
            "1. Official documentation\n2. Community resources\n3. Related articles and tutorials\n"
        ]
        
        return "".join(sections)
    
    def _get_random_user_agent(self):
        """Generate random user agent strings"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "PostmanRuntime/7.36.3",
            "curl/7.88.1",
            "python-requests/2.31.0",
        ]
        return random.choice(user_agents)