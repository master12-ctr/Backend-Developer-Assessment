
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class AnalyticsAPIException(APIException):
    """Base exception for analytics APIs"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred while processing your request.'
    default_code = 'analytics_error'
    
    def __init__(self, detail=None, code=None, log_level='error'):
        super().__init__(detail, code)
        
        # Log the exception
        if log_level == 'error':
            logger.error(f"AnalyticsAPIException: {detail}")
        elif log_level == 'warning':
            logger.warning(f"AnalyticsAPIException: {detail}")
        else:
            logger.info(f"AnalyticsAPIException: {detail}")


class InvalidFilterException(AnalyticsAPIException):
    """Invalid filter parameters"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid filter parameters provided.'
    default_code = 'invalid_filter'


class TimeRangeException(AnalyticsAPIException):
    """Invalid time range"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid time range specified.'
    default_code = 'invalid_time_range'


class DataNotFoundException(AnalyticsAPIException):
    """No data found for criteria"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'No data found for the specified criteria.'
    default_code = 'data_not_found'


class DatabaseQueryException(AnalyticsAPIException):
    """Database query error"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Database query error.'
    default_code = 'database_error'