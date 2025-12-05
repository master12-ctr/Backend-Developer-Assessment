# analytics_app/schemas.py
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# API #1 Schema
blog_views_schema = swagger_auto_schema(
    operation_description="Group blogs and views by selected object_type",
    manual_parameters=[
        openapi.Parameter(
            'object_type',
            openapi.IN_QUERY,
            description="Group by country or user",
            type=openapi.TYPE_STRING,
            enum=['country', 'user'],
            required=True
        ),
        openapi.Parameter(
            'range',
            openapi.IN_QUERY,
            description="Time range filter",
            type=openapi.TYPE_STRING,
            enum=['month', 'week', 'year']
        ),
        openapi.Parameter(
            'filters',
            openapi.IN_QUERY,
            description="JSON filter expression",
            type=openapi.TYPE_STRING,
            example='{"operator":"and","conditions":[{"field":"blog__title","operator":"contains","value":"test"}]}'
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Number of results per page",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'offset',
            openapi.IN_QUERY,
            description="Results offset for pagination",
            type=openapi.TYPE_INTEGER
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "object_type": "country",
                    "range": "month",
                    "count": 10,
                    "next": "http://api.example.com/analytics/blog-views/?limit=10&offset=10",
                    "previous": None,
                    "data": [
                        {"x": "United States", "y": 15, "z": 45},
                        {"x": "United Kingdom", "y": 12, "z": 38}
                    ]
                }
            }
        ),
        400: openapi.Response(
            description="Bad Request",
            examples={
                "application/json": {
                    "error": "Invalid object_type. Must be 'country' or 'user'"
                }
            }
        ),
        500: openapi.Response(
            description="Internal Server Error",
            examples={
                "application/json": {
                    "error": "Internal server error",
                    "request_id": "abc123-def456"
                }
            }
        )
    }
)

# API #2 Schema
top_analytics_schema = swagger_auto_schema(
    operation_description="Returns Top 10 based on total views",
    manual_parameters=[
        openapi.Parameter(
            'top',
            openapi.IN_QUERY,
            description="Top by user, country, or blog",
            type=openapi.TYPE_STRING,
            enum=['user', 'country', 'blog'],
            required=True
        ),
        openapi.Parameter(
            'range',
            openapi.IN_QUERY,
            description="Time range filter",
            type=openapi.TYPE_STRING,
            enum=['month', 'week', 'year']
        ),
        openapi.Parameter(
            'filters',
            openapi.IN_QUERY,
            description="JSON filter expression",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "top_type": "user",
                    "data": [
                        {"x": "John Doe", "y": 15, "z": 120},
                        {"x": "Jane Smith", "y": 12, "z": 95}
                    ]
                }
            }
        )
    }
)

# API #3 Schema
performance_schema = swagger_auto_schema(
    operation_description="Time-series performance for a user or all users",
    manual_parameters=[
        openapi.Parameter(
            'compare',
            openapi.IN_QUERY,
            description="Comparison period",
            type=openapi.TYPE_STRING,
            enum=['month', 'week', 'day', 'year'],
            required=True
        ),
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description="Filter by user ID",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'filters',
            openapi.IN_QUERY,
            description="JSON filter expression",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: openapi.Response(
            description="Success",
            examples={
                "application/json": {
                    "compare": "month",
                    "user_id": None,
                    "data": [
                        {"x": "October 2025 (15 blogs)", "y": 150, "z": 0.0},
                        {"x": "November 2025 (20 blogs)", "y": 220, "z": 46.67},
                        {"x": "December 2025 (18 blogs)", "y": 310, "z": 40.91}
                    ]
                }
            }
        )
    }
)