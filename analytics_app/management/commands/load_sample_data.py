
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
        print("="*70)
        print("🚀 LOADING COMPREHENSIVE SAMPLE DATA FOR ANALYTICS ASSESSMENT")
        print("="*70)
        
        # Clear existing data first
        print("\n🗑️ STEP 1: Clearing existing data...")
        
        # Delete in correct order to avoid foreign key constraints
        try:
            BlogView.objects.all().delete()
            print("  ✓ Cleared all blog views")
        except Exception as e:
            print(f"  ⚠️ Warning clearing blog views: {e}")
        
        try:
            Blog.objects.all().delete()
            print("  ✓ Cleared all blogs")
        except Exception as e:
            print(f"  ⚠️ Warning clearing blogs: {e}")
        
        try:
            Country.objects.all().delete()
            print("  ✓ Cleared all countries")
        except Exception as e:
            print(f"  ⚠️ Warning clearing countries: {e}")
        
        # Delete non-superuser users
        try:
            non_superusers = User.objects.filter(is_superuser=False)
            user_count = non_superusers.count()
            
            # First, update foreign keys to None to avoid constraint errors
            Blog.objects.filter(author__in=non_superusers).update(author=None)
            BlogView.objects.filter(user__in=non_superusers).update(user=None)
            
            # Then delete the users
            non_superusers.delete()
            print(f"  ✓ Cleared {user_count} non-superuser users")
        except Exception as e:
            print(f"  ⚠️ Warning clearing users: {e}")
        
        print("\n📊 STEP 2: Creating test users...")
        users = []
        for i in range(1, 11):
            try:
                user = User.objects.create_user(
                    username=f'testuser{i}',
                    email=f'test{i}@example.com',
                    first_name=f'Test{i}',
                    last_name='User',
                    password='testpass123'
                )
                users.append(user)
                print(f"  ✓ Created user: {user.username}")
            except Exception as e:
                print(f"  ⚠️ Error creating user testuser{i}: {e}")
                # Try with a different username
                try:
                    user = User.objects.create_user(
                        username=f'testuser_{i}_{random.randint(1000, 9999)}',
                        email=f'test{i}@example.com',
                        first_name=f'Test{i}',
                        last_name='User',
                        password='testpass123'
                    )
                    users.append(user)
                    print(f"  ✓ Created user: {user.username}")
                except Exception as e2:
                    print(f"  ❌ Failed to create user: {e2}")
        
        if not users:
            print("  ❌ No users created. Aborting.")
            return
            
        print(f"\n✅ Created {len(users)} test users")
        
        print("\n🌍 STEP 3: Creating countries...")
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
            try:
                country = Country.objects.create(
                    name=data['name'],
                    code=data['code']
                )
                countries.append(country)
                print(f"  ✓ Created country: {country.name} ({country.code})")
            except Exception as e:
                print(f"  ⚠️ Error creating country {data['name']}: {e}")
        
        if not countries:
            print("  ❌ No countries created. Aborting.")
            return
            
        print(f"\n✅ Created {len(countries)} countries")
        
        print("\n📝 STEP 4: Creating blog posts...")
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
        ]
        
        for i, title in enumerate(blog_titles):
            try:
                blog = Blog.objects.create(
                    title=title,
                    content=f"This is a detailed article about {title}. " * 20,
                    author=random.choice(users),
                    country=random.choice(countries),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 365))
                )
                blogs.append(blog)
                if i < 5:  # Show first 5 blogs for progress
                    print(f"  ✓ Created blog: {title}")
            except Exception as e:
                print(f"  ⚠️ Error creating blog '{title}': {e}")
        
        if not blogs:
            print("  ❌ No blogs created. Aborting.")
            return
            
        print(f"\n✅ Created {len(blogs)} blog posts")
        
        print("\n👁️ STEP 5: Creating blog views (this may take a moment)...")
        total_views = 0
        now = timezone.now()
        
        # Create a smaller dataset for testing
        total_days = 30  # Reduced from 90 to 30 for faster testing
        print(f"  📅 Generating views for last {total_days} days")
        
        # Create daily view patterns (more views on weekdays)
        for day_offset in range(total_days):
            view_date = now - timedelta(days=day_offset)
            day_of_week = view_date.weekday()  # Monday=0, Sunday=6
            
            # More views on weekdays
            if day_of_week < 5:  # Weekday
                daily_views = random.randint(5, 15)  # Reduced for faster testing
            else:  # Weekend
                daily_views = random.randint(2, 5)
            
            # Create views for this day
            for _ in range(daily_views):
                try:
                    # Create view at a random time during the day
                    hour = random.randint(0, 23)
                    minute = random.randint(0, 59)
                    
                    viewed_at = view_date.replace(
                        hour=hour,
                        minute=minute,
                        second=0,
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
                except Exception as e:
                    print(f"  ⚠️ Error creating blog view: {e}")
            
            # Show progress every 5 days
            if day_offset % 5 == 0:
                percentage = int((day_offset / total_days) * 100)
                print(f"  📊 Day {day_offset}/{total_days} ({percentage}%) - {daily_views} views today")
        
        print(f"\n✅ Created {total_views:,} blog views")
        
        # Final summary
        print("\n" + "="*70)
        print("✅ SAMPLE DATA LOADED SUCCESSFULLY")
        print("="*70)
        print("\n📊 DATA SUMMARY:")
        print(f"  👥 Users: {User.objects.filter(is_superuser=False).count()} test users")
        print(f"  🌍 Countries: {Country.objects.count()} countries")
        print(f"  📝 Blogs: {Blog.objects.count()} blog posts")
        print(f"  👁️  Blog Views: {BlogView.objects.count():,} views")
        
        print("\n🔐 TEST CREDENTIALS:")
        print("  📧 Username: testuser1")
        print("  🔑 Password: testpass123")
        
        print("\n🔗 ASSESSMENT API ENDPOINTS:")
        print("  📈 API #1 - Blog Views Analytics:")
        print("     http://localhost:8000/analytics/blog-views/?object_type=country&range=month")
        print("     http://localhost:8000/analytics/blog-views/?object_type=user&range=month")
        
        print("\n  🏆 API #2 - Top Analytics:")
        print("     http://localhost:8000/analytics/top/?top=user")
        print("     http://localhost:8000/analytics/top/?top=country")
        print("     http://localhost:8000/analytics/top/?top=blog")
        
        print("\n  📊 API #3 - Performance Analytics:")
        print("     http://localhost:8000/analytics/performance/?compare=month")
        print("     http://localhost:8000/analytics/performance/?compare=week")
        
        print("\n📚 DOCUMENTATION:")
        print("  📖 Swagger UI: http://localhost:8000/swagger/")
        print("  📋 ReDoc: http://localhost:8000/redoc/")
        print("  ⚙️  Admin: http://localhost:8000/admin/")
        
        print("\n🧪 TEST COMMANDS:")
        print("  $ python manage.py test analytics_app")
        
        print("\n" + "="*70)
        print("🎉 SAMPLE DATA READY FOR ASSESSMENT TESTING!")
        print("="*70)
