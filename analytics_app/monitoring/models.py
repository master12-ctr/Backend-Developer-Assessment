# analytics_app/monitoring/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class APIRequestLog(models.Model):
    """
    Model for tracking API requests and responses
    """
    request_id = models.UUIDField(db_index=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    query_params = models.JSONField(null=True, blank=True)
    request_body = models.JSONField(null=True, blank=True)
    
    status_code = models.IntegerField()
    response_body = models.JSONField(null=True, blank=True)
    
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    request_time = models.DateTimeField()
    response_time = models.DateTimeField()
    duration_ms = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['request_time']),
            models.Index(fields=['path', 'request_time']),
            models.Index(fields=['status_code', 'request_time']),
            models.Index(fields=['user', 'request_time']),
        ]
    
    @property
    def is_success(self):
        return 200 <= self.status_code < 300
    
    @property
    def is_error(self):
        return self.status_code >= 400

class SystemMetrics(models.Model):
    """
    Model for storing system performance metrics
    """
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    cpu_percent = models.FloatField()
    memory_percent = models.FloatField()
    active_connections = models.IntegerField()
    queries_per_second = models.FloatField()
    response_time_avg = models.FloatField()
    error_rate = models.FloatField()
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
        ]

class AnalyticsMetrics(models.Model):
    """
    Model for storing analytics-specific metrics
    """
    period = models.DateTimeField(db_index=True)
    metric_type = models.CharField(max_length=50, choices=[
        ('daily_views', 'Daily Views'),
        ('unique_users', 'Unique Users'),
        ('top_countries', 'Top Countries'),
        ('performance', 'Performance'),
    ])
    data = models.JSONField()
    
    class Meta:
        indexes = [
            models.Index(fields=['period', 'metric_type']),
        ]
        unique_together = ['period', 'metric_type']