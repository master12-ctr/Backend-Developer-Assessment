# analytics_app/monitoring/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, F
from datetime import datetime, timedelta
from django.utils import timezone
from ..monitoring.models import APIRequestLog, SystemMetrics

class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring
    """
    def get(self, request):
        # Check database connection
        try:
            from django.db import connection
            connection.cursor()
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Check recent API performance
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_requests = APIRequestLog.objects.filter(
            response_time__gte=one_hour_ago
        )
        
        total_requests = recent_requests.count()
        error_rate = recent_requests.filter(status_code__gte=400).count()
        error_rate = (error_rate / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = recent_requests.aggregate(
            avg_time=Avg('duration_ms')
        )['avg_time'] or 0
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'components': {
                'database': db_status,
                'api': 'healthy',
                'cache': 'healthy',
            },
            'metrics': {
                'total_requests_last_hour': total_requests,
                'error_rate_percent': round(error_rate, 2),
                'avg_response_time_ms': round(avg_response_time, 2),
                'uptime': self.get_uptime(),
            }
        })
    
    def get_uptime(self):
        # This would require system-level monitoring
        # For now, return a placeholder
        return "24 hours"

class PerformanceDashboardView(APIView):
    """
    Dashboard for performance metrics
    """
    def get(self, request):
        # Time ranges
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # API usage statistics
        api_stats = APIRequestLog.objects.filter(
            response_time__gte=month_ago
        ).values('path').annotate(
            total_requests=Count('id'),
            avg_response_time=Avg('duration_ms'),
            error_count=Count('id', filter=F('status_code__gte', 400))
        ).order_by('-total_requests')[:10]
        
        # Hourly traffic for today
        hourly_traffic = []
        for hour in range(24):
            hour_start = timezone.make_aware(datetime.combine(today, time(hour, 0, 0)))
            hour_end = hour_start + timedelta(hours=1)
            
            count = APIRequestLog.objects.filter(
                response_time__gte=hour_start,
                response_time__lt=hour_end
            ).count()
            
            hourly_traffic.append({
                'hour': hour,
                'requests': count
            })
        
        # Top users by API usage
        top_users = APIRequestLog.objects.filter(
            user__isnull=False,
            response_time__gte=week_ago
        ).values('user__username').annotate(
            request_count=Count('id'),
            avg_response_time=Avg('duration_ms')
        ).order_by('-request_count')[:5]
        
        return Response({
            'time_period': {
                'today': today.isoformat(),
                'week_ago': week_ago.isoformat(),
                'month_ago': month_ago.isoformat(),
            },
            'api_statistics': list(api_stats),
            'hourly_traffic': hourly_traffic,
            'top_users': list(top_users),
            'summary': {
                'total_requests_today': sum(h['requests'] for h in hourly_traffic),
                'avg_response_time': APIRequestLog.objects.filter(
                    response_time__gte=today
                ).aggregate(avg=Avg('duration_ms'))['avg'] or 0,
            }
        })