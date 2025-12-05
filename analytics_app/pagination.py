# analytics_app/pagination.py
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict



class AnalyticsPagination(LimitOffsetPagination):
    """
    Custom pagination for analytics APIs with metadata
    """
    default_limit = 100
    max_limit = 1000
    
    def get_paginated_response(self, data):
        """
        Custom paginated response format
        """
        # Extract metadata from data if provided
        object_type = data.get('object_type') if isinstance(data, dict) else None
        date_range = data.get('range') if isinstance(data, dict) else None
        data_list = data.get('data', []) if isinstance(data, dict) else data
        
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('limit', self.limit),
            ('offset', self.offset),
            ('object_type', object_type),
            ('range', date_range),
            ('data', data_list)
        ]))
        
class AnalyticsPagination(LimitOffsetPagination):
    """
    Custom pagination for analytics APIs with metadata
    """
    default_limit = 100
    max_limit = 1000
    
    def get_paginated_response(self, data):
        """
        Custom paginated response format
        """
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('limit', self.limit),
            ('offset', self.offset),
            ('data', data.get('data', []))
        ]))
    
    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.com/analytics/blog-views/?limit=100&offset=100'
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.com/analytics/blog-views/?limit=100&offset=0'
                },
                'limit': {
                    'type': 'integer',
                    'example': 100
                },
                'offset': {
                    'type': 'integer',
                    'example': 0
                },
                'data': schema,
            },
        }