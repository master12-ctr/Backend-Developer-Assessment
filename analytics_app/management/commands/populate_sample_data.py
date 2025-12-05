
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from analytics_app.models import Country, Blog, BlogView
from datetime import datetime, timedelta
import random
from faker import Faker
from django.utils import timezone
import sys


class Command(BaseCommand):
    help = 'Populates database with sample data for testing'
    
    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Clear existing data first
        self.stdout.write("Clearing existing data...")
        BlogView.objects.all().delete()
        Blog.objects.all().delete()
        Country.objects.all().delete()
        
        # Don't delete superusers
        User.objects.filter(is_superuser=False).delete()
        
        # Create countries with unique codes
        self.stdout.write("Creating countries...")
        countries = []
        used_codes = set()
        
        for i in range(10):
            while True:
                code = fake.country_code()
                if code not in used_codes and len(code) == 2:
                    used_codes.add(code)
                    break
            
            country = Country.objects.create(
                name=fake.country(),
                code=code
            )
            countries.append(country)
        
        self.stdout.write(f"Created {len(countries)} countries")
        
        # Create users
        self.stdout.write("Creating users...")
        users = []
        for i in range(20):
            username = f"user_{i}_{fake.user_name()}"
            
            user = User.objects.create(
                username=username,
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            user.set_password('password123')
            user.save()
            users.append(user)
        
        self.stdout.write(f"Created {len(users)} users")
        
        # Create blogs
        self.stdout.write("Creating blogs...")
        blogs = []
        for i in range(50):
            blog = Blog.objects.create(
                title=f"{fake.sentence()} #{i}",
                content=fake.text(),
                author=random.choice(users),
                country=random.choice(countries)
            )
            blogs.append(blog)
        
        self.stdout.write(f"Created {len(blogs)} blogs")
        
        # Create blog views in bulk for better performance
        self.stdout.write("Creating blog views...")
        blog_views = []
        
        # Create more recent views for testing date ranges
        for i in range(500):  # Create 500 views
            blog = random.choice(blogs)
            days_ago = random.randint(0, 60)  # Last 60 days for better testing
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            # Make sure some views are from the last month
            if i < 100:  # Ensure 100 views from last 30 days
                days_ago = random.randint(0, 30)
            
            blog_view = BlogView(
                blog=blog,
                user=random.choice(users),
                country=random.choice(countries),
                viewed_at=timezone.now() - timedelta(
                    days=days_ago, 
                    hours=hours_ago, 
                    minutes=minutes_ago
                ),
                duration=random.randint(10, 600)
            )
            blog_views.append(blog_view)
        
        # Use bulk_create for better performance
        BlogView.objects.bulk_create(blog_views)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully populated sample data:\n'
            f'  - {len(countries)} countries\n'
            f'  - {len(users)} users\n'
            f'  - {len(blogs)} blogs\n'
            f'  - {len(blog_views)} blog views'
        ))