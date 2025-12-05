
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from django.conf import settings
from .models import BlogView
from .services import AnalyticsService
from .filters import BlogViewFilter, PerformanceFilter
from .pagination import AnalyticsPagination
from .exceptions import InvalidFilterException, TimeRangeException, DataNotFoundException

logger = logging.getLogger(__name__)


# Swagger schemas for API documentation
blog_views_params = [
    openapi.Parameter(
        'object_type',
        openapi.IN_QUERY,
        description="Group by 'country' or 'user'",
        type=openapi.TYPE_STRING,
        enum=['country', 'user'],
        required=True
    ),
    openapi.Parameter(
        'range',
        openapi.IN_QUERY,
        description="Time range: 'month', 'week', 'year'",
        type=openapi.TYPE_STRING,
        enum=['month', 'week', 'year'],
        required=False
    ),
    openapi.Parameter(
        'filters',
        openapi.IN_QUERY,
        description="JSON filter expression",
        type=openapi.TYPE_STRING,
        required=False,
        example='{"operator":"and","conditions":[{"field":"blog__title","operator":"contains","value":"test"}]}'
    ),
    openapi.Parameter(
        'limit',
        openapi.IN_QUERY,
        description="Number of results per page (default: 100, max: 1000)",
        type=openapi.TYPE_INTEGER,
        required=False
    ),
    openapi.Parameter(
        'offset',
        openapi.IN_QUERY,
        description="Results offset for pagination",
        type=openapi.TYPE_INTEGER,
        required=False
    ),
]

top_analytics_params = [
    openapi.Parameter(
        'top',
        openapi.IN_QUERY,
        description="Top by 'user', 'country', or 'blog'",
        type=openapi.TYPE_STRING,
        enum=['user', 'country', 'blog'],
        required=True
    ),
    openapi.Parameter(
        'range',
        openapi.IN_QUERY,
        description="Time range: 'month', 'week', 'year'",
        type=openapi.TYPE_STRING,
        required=False
    ),
    openapi.Parameter(
        'filters',
        openapi.IN_QUERY,
        description="JSON filter expression",
        type=openapi.TYPE_STRING,
        required=False
    ),
]

performance_params = [
    openapi.Parameter(
        'compare',
        openapi.IN_QUERY,
        description="Comparison period: 'day', 'week', 'month', 'year'",
        type=openapi.TYPE_STRING,
        enum=['day', 'week', 'month', 'year'],
        required=True
    ),
    openapi.Parameter(
        'user_id',
        openapi.IN_QUERY,
        description="Filter by user ID",
        type=openapi.TYPE_INTEGER,
        required=False
    ),
    openapi.Parameter(
        'filters',
        openapi.IN_QUERY,
        description="JSON filter expression",
        type=openapi.TYPE_STRING,
        required=False
    ),
]



# Update the BlogViewsAnalyticsAPI view in views.py
class BlogViewsAnalyticsAPI(APIView):
    """API #1: Group blogs and views by selected object_type"""
    
    filter_backends = (BlogViewFilter,)
    pagination_class = AnalyticsPagination
    queryset = BlogView.objects.all()  # Add this line for Swagger
    
    @swagger_auto_schema(
        manual_parameters=blog_views_params,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'object_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'range': openapi.Schema(type=openapi.TYPE_STRING),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format='uri', nullable=True),
                        'limit': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'offset': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_STRING),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'z': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description="Bad Request"),
            500: openapi.Response(description="Internal Server Error"),
        }
    )
    def get(self, request):
        try:
            # Log request
            logger.info(f"BlogViewsAnalyticsAPI called: {request.query_params}")
            
            # Extract and validate parameters
            object_type = request.query_params.get('object_type', 'country')
            date_range = request.query_params.get('range', 'month')
            filters = request.query_params.get('filters')
            
            # Validate object_type
            if object_type not in ['country', 'user']:
                raise InvalidFilterException(
                    f"Invalid object_type: {object_type}. Must be 'country' or 'user'"
                )
            
            # Validate range
            if date_range and date_range not in ['month', 'week', 'year']:
                raise TimeRangeException(
                    f"Invalid range: {date_range}. Must be 'month', 'week', or 'year'"
                )
            
            # Get data from service
            data_queryset = AnalyticsService.get_blog_views_analytics(
                object_type=object_type,
                date_range=date_range,
                filters=filters
            )
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(data_queryset, request, view=self)
            
            # Prepare base response data
            base_response = {
                'object_type': object_type,
                'range': date_range,
                'data': list(data_queryset)  # Full data for non-paginated response
            }
            
            # If paginated, return paginated response
            if page is not None:
                # For paginated response, update data to be just the current page
                base_response['data'] = page
                return paginator.get_paginated_response(base_response)
            
            # Non-paginated response
            return Response(base_response)
            
        except InvalidFilterException as e:
            logger.warning(f"Invalid filter in BlogViewsAnalyticsAPI: {str(e)}")
            return Response(
                {'error': str(e), 'code': 'invalid_filter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TimeRangeException as e:
            logger.warning(f"Invalid time range in BlogViewsAnalyticsAPI: {str(e)}")
            return Response(
                {'error': str(e), 'code': 'invalid_time_range'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DataNotFoundException as e:
            logger.info(f"No data found in BlogViewsAnalyticsAPI: {str(e)}")
            return Response({
                'object_type': object_type,
                'range': date_range,
                'data': [],
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in BlogViewsAnalyticsAPI: {str(e)}", 
                        exc_info=True)
            return Response({
                'error': 'Internal server error',
                'detail': str(e) if settings.DEBUG else None,
                'code': 'internal_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopAnalyticsAPI(APIView):
    """API #2: Returns Top 10 based on total views"""

    filter_backends = (BlogViewFilter,)
    queryset = BlogView.objects.all()  # Add this line
    
    @swagger_auto_schema(
        manual_parameters=top_analytics_params,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'top_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_STRING),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'z': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description="Bad Request"),
            500: openapi.Response(description="Internal Server Error"),
        }
    )
    def get(self, request):
        try:
            # Log request
            logger.info(f"TopAnalyticsAPI called: {request.query_params}")
            
            # Extract and validate parameters
            top_type = request.query_params.get('top', 'user')
            date_range = request.query_params.get('range')
            filters = request.query_params.get('filters')
            
            # Validate top_type
            if top_type not in ['user', 'country', 'blog']:
                raise InvalidFilterException(
                    f"Invalid top_type: {top_type}. Must be 'user', 'country', or 'blog'"
                )
            
            # Get data from service
            data = AnalyticsService.get_top_analytics(
                top_type=top_type,
                date_range=date_range,
                filters=filters
            )
            
            return Response({
                'top_type': top_type,
                'data': list(data)
            })
            
        except InvalidFilterException as e:
            logger.warning(f"Invalid filter in TopAnalyticsAPI: {str(e)}")
            return Response(
                {'error': str(e), 'code': 'invalid_filter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in TopAnalyticsAPI: {str(e)}", 
                        exc_info=True)
            return Response({
                'error': 'Internal server error',
                'detail': str(e) if settings.DEBUG else None,
                'code': 'internal_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerformanceAnalyticsAPI(APIView):
    """API #3: Time-series performance for a user or all users"""
    
    filter_backends = (PerformanceFilter,)
    queryset = BlogView.objects.all()  # Add this line
    
    @swagger_auto_schema(
        manual_parameters=performance_params,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'compare': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_STRING),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'z': openapi.Schema(type=openapi.TYPE_NUMBER),
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description="Bad Request"),
            500: openapi.Response(description="Internal Server Error"),
        }
    )
    def get(self, request):
        try:
            # Log request
            logger.info(f"PerformanceAnalyticsAPI called: {request.query_params}")
            
            # Extract and validate parameters
            compare_type = request.query_params.get('compare', 'month')
            user_id = request.query_params.get('user_id')
            filters = request.query_params.get('filters')
            
            # Validate compare_type
            if compare_type not in ['day', 'week', 'month', 'year']:
                raise InvalidFilterException(
                    f"Invalid compare_type: {compare_type}. Must be 'day', 'week', 'month', or 'year'"
                )
            
            # Convert user_id to integer if provided
            if user_id:
                try:
                    user_id = int(user_id)
                except ValueError:
                    raise InvalidFilterException("user_id must be an integer")
            
            # Get data from service
            data = AnalyticsService.get_performance_analytics(
                compare_type=compare_type,
                user_id=user_id,
                filters=filters
            )
            
            return Response({
                'compare': compare_type,
                'user_id': user_id,
                'data': data
            })
            
        except InvalidFilterException as e:
            logger.warning(f"Invalid filter in PerformanceAnalyticsAPI: {str(e)}")
            return Response(
                {'error': str(e), 'code': 'invalid_filter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in PerformanceAnalyticsAPI: {str(e)}", 
                        exc_info=True)
            return Response({
                'error': 'Internal server error',
                'detail': str(e) if settings.DEBUG else None,
                'code': 'internal_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)