
import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
import json
from datetime import datetime, timedelta
from django.utils import timezone
from .models import BlogView


class DynamicFilterBackend(filters.DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        class DynamicFilterSet(filters.FilterSet):
            date_from = filters.DateFilter(field_name='viewed_at', lookup_expr='gte')
            date_to = filters.DateFilter(field_name='viewed_at', lookup_expr='lte')
            range = filters.CharFilter(method='filter_range')
            filters = filters.CharFilter(method='apply_dynamic_filters')
            
            class Meta:
                model = BlogView
                fields = ['blog', 'user', 'country']
            
            def filter_range(self, queryset, name, value):
                today = timezone.now()
                if value == 'week':
                    start_date = today - timedelta(days=7)
                elif value == 'month':
                    start_date = today - timedelta(days=30)
                elif value == 'year':
                    start_date = today - timedelta(days=365)
                else:
                    return queryset
                return queryset.filter(viewed_at__gte=start_date)
            
            def apply_dynamic_filters(self, queryset, name, value):
                try:
                    filters_data = json.loads(value)
                    return self._apply_filters(queryset, filters_data)
                except (json.JSONDecodeError, KeyError):
                    return queryset
            
            def _apply_filters(self, queryset, filters_data):
                operator = filters_data.get('operator', 'and')
                conditions = filters_data.get('conditions', [])
                
                q_objects = Q()
                
                for condition in conditions:
                    field = condition.get('field')
                    op = condition.get('operator')
                    value = condition.get('value')
                    
                    if not all([field, op, value]):
                        continue
                    
                    lookup = self._get_lookup_expr(op)
                    q_obj = Q(**{f"{field}__{lookup}": value})
                    
                    if operator == 'and':
                        q_objects &= q_obj
                    elif operator == 'or':
                        q_objects |= q_obj
                    elif operator == 'not':
                        q_objects &= ~q_obj
                
                return queryset.filter(q_objects)
            
            def _get_lookup_expr(self, operator):
                lookup_map = {
                    'eq': 'exact',
                    'gt': 'gt',
                    'gte': 'gte',
                    'lt': 'lt',
                    'lte': 'lte',
                    'contains': 'icontains',
                    'in': 'in',
                }
                return lookup_map.get(operator, 'exact')
        
        return DynamicFilterSet


class BlogViewFilter(DynamicFilterBackend):
    pass


class PerformanceFilter(DynamicFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        class PerformanceFilterSet(filters.FilterSet):
            compare = filters.CharFilter(method='filter_compare')
            user_id = filters.NumberFilter(field_name='blog__author__id')
            
            class Meta:
                model = BlogView
                fields = ['user_id']
        
        return PerformanceFilterSet