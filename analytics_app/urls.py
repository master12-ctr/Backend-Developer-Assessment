# analytics_app/urls.py
from django.urls import path
from .views import BlogViewsAnalyticsAPI, TopAnalyticsAPI, PerformanceAnalyticsAPI

urlpatterns = [
    path('analytics/blog-views/', BlogViewsAnalyticsAPI.as_view(), name='blog-views-analytics'),
    path('analytics/top/', TopAnalyticsAPI.as_view(), name='top-analytics'),
    path('analytics/performance/', PerformanceAnalyticsAPI.as_view(), name='performance-analytics'),
]

