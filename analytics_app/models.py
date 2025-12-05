# analytics_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class Country(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=3, unique=True, db_index=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']


class Blog(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs', db_index=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            # Single column indexes
            models.Index(fields=['created_at']),
            models.Index(fields=['title']),
            
            # Composite indexes for common query patterns
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['country', 'created_at']),
            models.Index(fields=['author', 'country', 'created_at']),
            
            # Text search index (for PostgreSQL)
            # models.Index(fields=['title'], name='blog_title_idx', opclasses=['varchar_pattern_ops']),
        ]
    
    def __str__(self):
        return self.title


class BlogView(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='views', db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                            related_name='blog_views', db_index=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    viewed_at = models.DateTimeField(default=timezone.now, db_index=True)
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    
    class Meta:
        indexes = [
            # Single column indexes
            models.Index(fields=['viewed_at']),
            models.Index(fields=['duration']),
            
            # Composite indexes for analytics queries
            models.Index(fields=['blog', 'viewed_at']),
            models.Index(fields=['user', 'viewed_at']),
            models.Index(fields=['country', 'viewed_at']),
            
            # Composite indexes for common analytics queries
            models.Index(fields=['country', 'viewed_at', 'blog']),
            models.Index(fields=['user', 'viewed_at', 'blog']),
            models.Index(fields=['blog', 'viewed_at', 'country']),
            
            # Covering indexes for performance
            models.Index(fields=['viewed_at', 'country', 'user', 'blog']),
            models.Index(fields=['country', 'viewed_at', 'user', 'blog']),
        ]
        verbose_name_plural = "Blog Views"
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.blog.title} viewed at {self.viewed_at.strftime('%Y-%m-%d %H:%M')}"