
import time
import json
from django.utils.deprecation import MiddlewareMixin
from ..monitoring.models import APIRequestLog

class APIMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware for monitoring API performance and usage
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Only log API requests
            if request.path.startswith('/analytics/'):
                try:
                    # Extract user from request
                    user = request.user if request.user.is_authenticated else None
                    
                    # Extract client IP
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        client_ip = x_forwarded_for.split(',')[0]
                    else:
                        client_ip = request.META.get('REMOTE_ADDR')
                    
                    # Extract query params
                    query_params = dict(request.GET)
                    
                    # Extract request body (if JSON)
                    request_body = None
                    if request.body and request.content_type == 'application/json':
                        try:
                            request_body = json.loads(request.body.decode('utf-8'))
                        except:
                            pass
                    
                    # Extract response body (if JSON)
                    response_body = None
                    if hasattr(response, 'data'):
                        response_body = response.data
                    elif response.get('Content-Type', '').startswith('application/json'):
                        try:
                            response_body = json.loads(response.content.decode('utf-8'))
                        except:
                            pass
                    
                    # Create log entry
                    APIRequestLog.objects.create(
                        request_id=getattr(request, 'request_id', None),
                        method=request.method,
                        path=request.path,
                        query_params=query_params,
                        request_body=request_body,
                        status_code=response.status_code,
                        response_body=response_body,
                        user=user,
                        client_ip=client_ip,
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        request_time=timezone.now() - timedelta(seconds=duration),
                        response_time=timezone.now(),
                        duration_ms=duration * 1000
                    )
                    
                except Exception as e:
                    # Don't fail the request if monitoring fails
                    logger.error(f"Failed to log API request: {str(e)}")
        
        return response