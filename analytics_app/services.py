
from django.db.models import Count, Sum, F, Window, Q, Value, CharField
from django.db.models.functions import Trunc, Coalesce, Lag, Extract
from django.db.models.functions import Concat
from datetime import datetime, timedelta
from django.utils import timezone
import json
import logging

from .models import BlogView, Blog, User
from .exceptions import (
    InvalidFilterException, 
    TimeRangeException, 
    DataNotFoundException,
    DatabaseQueryException
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    
    @staticmethod
    def get_blog_views_analytics(object_type, date_range, filters=None):
        """
        API #1: Group blogs and views by selected object_type
        Returns: x=grouping_key, y=number_of_blogs, z=total_views
        """
        try:
            logger.info(f"get_blog_views_analytics called: object_type={object_type}, range={date_range}")
            
            # Validate object_type
            if object_type not in ['country', 'user']:
                raise InvalidFilterException(
                    f"Invalid object_type: {object_type}. Must be 'country' or 'user'"
                )
            
            queryset = BlogView.objects.select_related(
                'blog', 'user', 'country', 'blog__author'
            )
            
            # Apply date range
            queryset = AnalyticsService._apply_date_range(queryset, date_range)
            
            # Apply dynamic filters
            if filters:
                queryset = AnalyticsService._apply_filters(queryset, filters)
            
            # Group by object_type
            if object_type == 'country':
                # Filter out null countries first
                queryset = queryset.filter(country__isnull=False)
                result = queryset.values(
                    x=F('country__name')
                ).annotate(
                    y=Count('blog', distinct=True),
                    z=Count('id')
                ).order_by('-z')
            
            elif object_type == 'user':
                # Filter out null users first
                queryset = queryset.filter(user__isnull=False)
                result = queryset.annotate(
                    full_name=Concat(
                        F('user__first_name'), 
                        Value(' '), 
                        F('user__last_name'),
                        output_field=CharField()
                    )
                ).values(
                    x=F('full_name')
                ).annotate(
                    y=Count('blog', distinct=True),
                    z=Count('id')
                ).order_by('-z')
            
            # Check if data exists
            if not result.exists():
                logger.info(f"No data found for object_type={object_type}, range={date_range}")
                raise DataNotFoundException("No data found for the specified criteria")
            
            logger.info(f"get_blog_views_analytics returning {result.count()} results")
            return result
            
        except (InvalidFilterException, TimeRangeException, DataNotFoundException) as e:
            # Re-raise known exceptions
            raise e
        except Exception as e:
            logger.error(f"Error in get_blog_views_analytics: {str(e)}", 
                        exc_info=True,
                        extra={
                            'object_type': object_type,
                            'date_range': date_range,
                            'filters': filters
                        })
            raise DatabaseQueryException(f"Database query error: {str(e)}")
    
    @staticmethod
    def get_top_analytics(top_type, date_range=None, filters=None):
        """
        API #2: Returns Top 10 based on total views
        """
        try:
            logger.info(f"get_top_analytics called: top_type={top_type}, range={date_range}")
            
            # Validate top_type
            if top_type not in ['user', 'country', 'blog']:
                raise InvalidFilterException(
                    f"Invalid top_type: {top_type}. Must be 'user', 'country', or 'blog'"
                )
            
            queryset = BlogView.objects.select_related(
                'blog', 'user', 'country', 'blog__author'
            )
            
            if date_range:
                queryset = AnalyticsService._apply_date_range(queryset, date_range)
            
            if filters:
                queryset = AnalyticsService._apply_filters(queryset, filters)
            
            if top_type == 'user':
                queryset = queryset.filter(blog__author__isnull=False)
                result = queryset.values(
                    x=Concat(
                        F('blog__author__first_name'),
                        Value(' '),
                        F('blog__author__last_name'),
                        output_field=CharField()
                    )
                ).annotate(
                    y=Count('blog', distinct=True),
                    z=Count('id')
                ).order_by('-z')[:10]
            
            elif top_type == 'country':
                queryset = queryset.filter(country__isnull=False)
                result = queryset.values(
                    x=F('country__name')
                ).annotate(
                    y=Count('blog', distinct=True),
                    z=Count('id')
                ).order_by('-z')[:10]
            
            elif top_type == 'blog':
                result = queryset.values(
                    x=F('blog__title'),
                    y=F('blog__author__username')
                ).annotate(
                    z=Count('id')
                ).order_by('-z')[:10]
            
            logger.info(f"get_top_analytics returning {len(result)} results")
            return result
            
        except (InvalidFilterException, TimeRangeException) as e:
            raise e
        except Exception as e:
            logger.error(f"Error in get_top_analytics: {str(e)}", 
                        exc_info=True,
                        extra={
                            'top_type': top_type,
                            'date_range': date_range,
                            'filters': filters
                        })
            raise DatabaseQueryException(f"Database query error: {str(e)}")
    
    @staticmethod
    def get_performance_analytics(compare_type, user_id=None, filters=None):
        """
        API #3: Time-series performance for a user or all users
        Returns: x=period_label + number_of_blogs created, y=views, z=growth_percentage
        """
        try:
            logger.info(f"get_performance_analytics called: compare={compare_type}, user_id={user_id}")
            
            # Validate compare_type
            if compare_type not in ['day', 'week', 'month', 'year']:
                raise InvalidFilterException(
                    f"Invalid compare_type: {compare_type}. Must be 'day', 'week', 'month', or 'year'"
                )
            
            # Get blogs created per period
            blog_queryset = Blog.objects.all()
            if user_id:
                blog_queryset = blog_queryset.filter(author_id=user_id)
            
            trunc_kwarg = AnalyticsService._get_trunc_kwarg(compare_type)
            
            # Get blog creation counts per period
            blogs_per_period = list(blog_queryset.annotate(
                period=Trunc('created_at', **trunc_kwarg)
            ).values('period').annotate(
                blogs_created=Count('id')
            ).order_by('period'))
            
            # Get views per period
            views_queryset = BlogView.objects.select_related('blog')
            if user_id:
                views_queryset = views_queryset.filter(blog__author_id=user_id)
            
            if filters:
                views_queryset = AnalyticsService._apply_filters(views_queryset, filters)
            
            views_per_period = list(views_queryset.annotate(
                period=Trunc('viewed_at', **trunc_kwarg)
            ).values('period').annotate(
                total_views=Count('id')
            ).order_by('period'))
            
            # Combine data and calculate growth
            result = []
            previous_views = 0
            
            for period_data in views_per_period:
                period = period_data['period']
                views = period_data['total_views']
                
                # Get blogs created in this period
                blogs_in_period = 0
                for blog_period in blogs_per_period:
                    if blog_period['period'] == period:
                        blogs_in_period = blog_period['blogs_created']
                        break
                
                # Calculate growth percentage
                if previous_views > 0:
                    growth_pct = ((views - previous_views) / previous_views) * 100
                else:
                    growth_pct = 0 if views == 0 else 100
                
                # Format period label based on compare_type
                if compare_type == 'day':
                    period_label = period.strftime('%Y-%m-%d')
                elif compare_type == 'week':
                    # Get week number and year
                    week_num = period.strftime('%U')
                    year = period.strftime('%Y')
                    period_label = f"Week {week_num}, {year}"
                elif compare_type == 'month':
                    period_label = period.strftime('%B %Y')
                else:  # year
                    period_label = period.strftime('%Y')
                
                result.append({
                    'x': f"{period_label} ({blogs_in_period} blogs)",
                    'y': views,
                    'z': round(growth_pct, 2)
                })
                
                previous_views = views
            
            if not result:
                logger.info(f"No performance data found for compare={compare_type}, user_id={user_id}")
                raise DataNotFoundException("No performance data found for the specified criteria")
            
            logger.info(f"get_performance_analytics returning {len(result)} periods")
            return result
            
        except (InvalidFilterException, DataNotFoundException) as e:
            raise e
        except Exception as e:
            logger.error(f"Error in get_performance_analytics: {str(e)}", 
                        exc_info=True,
                        extra={
                            'compare_type': compare_type,
                            'user_id': user_id,
                            'filters': filters
                        })
            raise DatabaseQueryException(f"Database query error: {str(e)}")
    
    @staticmethod
    def _apply_date_range(queryset, date_range):
        today = timezone.now()
        if date_range == 'week':
            start_date = today - timedelta(days=7)
        elif date_range == 'month':
            start_date = today - timedelta(days=30)
        elif date_range == 'year':
            start_date = today - timedelta(days=365)
        else:
            return queryset  # No date filter if range is not specified
        
        return queryset.filter(viewed_at__gte=start_date)
    
    @staticmethod
    def _apply_filters(queryset, filters):
        try:
            if not filters:
                return queryset
            
            filters_data = json.loads(filters)
            q_objects = Q()
            
            operator = filters_data.get('operator', 'and')
            conditions = filters_data.get('conditions', [])
            
            for condition in conditions:
                field = condition.get('field')
                op = condition.get('operator')
                value = condition.get('value')
                
                if not all([field, op, value]):
                    continue
                
                lookup = AnalyticsService._get_lookup(field, op)
                q_obj = Q(**{lookup: value})
                
                if operator == 'and':
                    q_objects &= q_obj
                elif operator == 'or':
                    q_objects |= q_obj
                elif operator == 'not':
                    q_objects &= ~q_obj
            
            return queryset.filter(q_objects)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in filters: {filters}")
            raise InvalidFilterException(f"Invalid JSON format in filters: {str(e)}")
        except KeyError as e:
            logger.warning(f"Missing key in filters: {filters}")
            raise InvalidFilterException(f"Missing key in filters: {str(e)}")
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            raise InvalidFilterException(f"Error applying filters: {str(e)}")
    
    @staticmethod
    def _get_lookup(field, operator):
        lookup_map = {
            'eq': 'exact',
            'gt': 'gt',
            'gte': 'gte',
            'lt': 'lt',
            'lte': 'lte',
            'contains': 'icontains',
            'in': 'in',
        }
        lookup_expr = lookup_map.get(operator, 'exact')
        return f"{field}__{lookup_expr}"
    
    @staticmethod
    def _get_trunc_kwarg(compare_type):
        trunc_map = {
            'day': 'day',
            'week': 'week',
            'month': 'month',
            'year': 'year',
        }
        return {'kind': trunc_map.get(compare_type, 'month')}