# analytics_app/middleware.py
import time
import uuid
import json
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging all API requests and responses"""
    

def process_request(self, request):
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())
    
    # Add trailing slash to certain URLs
    if request.path in ['/swagger', '/redoc']:
        from django.shortcuts import redirect
        return redirect(request.path + '/')

def process_request(self, request):
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())
    
    # Don't log admin or static requests
    if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
        # Normalize path by adding trailing slash if missing for certain paths
        if request.path in ['/swagger', '/redoc']:
            request.path = request.path + '/'
        
        log_data = {
            'request_id': request.request_id,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'client_ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        if request.body and request.content_type == 'application/json':
            try:
                log_data['request_body'] = json.loads(request.body.decode('utf-8'))
            except:
                pass
        
        logger.info(f"API Request: {json.dumps(log_data)}")
    
    return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
                log_data = {
                    'request_id': request.request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'response_size': len(response.content) if hasattr(response, 'content') else 0,
                }
                
                logger.info(f"API Response: {json.dumps(log_data)}")
                
                # Add request ID to response headers
                if isinstance(response, dict):
                    response['X-Request-ID'] = request.request_id
                elif hasattr(response, 'headers'):
                    response.headers['X-Request-ID'] = request.request_id
        
        return response
    
    def process_exception(self, request, exception):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'request_id': getattr(request, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'exception': str(exception),
                'exception_type': type(exception).__name__,
                'duration_ms': round(duration * 1000, 2),
            }
            
            logger.error(f"API Exception: {json.dumps(log_data)}")
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip