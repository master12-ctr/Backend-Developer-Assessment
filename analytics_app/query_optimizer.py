
from django.db import connection
from django.db.models import QuerySet
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Utility class for optimizing database queries
    """
    
    @staticmethod
    def explain_query(queryset):
        """
        Explain the query plan for debugging
        """
        if not isinstance(queryset, QuerySet):
            return "Not a QuerySet"
        
        with connection.cursor() as cursor:
            sql, params = queryset.query.sql_with_params()
            cursor.execute(f"EXPLAIN ANALYZE {sql}", params)
            return cursor.fetchall()
    
    @staticmethod
    def optimize_queryset(queryset, hint=None):
        """
        Apply optimizations to queryset
        """
        # Force specific joins if needed
        if hint == 'force_index':
            # This is database-specific and may require raw SQL
            pass
        
        # Ensure we're using select_related/prefetch_related properly
        if not queryset.query.select_related:
            # Auto-detect foreign keys that should be selected
            model = queryset.model
            foreign_keys = [
                field.name for field in model._meta.fields 
                if field.is_relation and field.many_to_one
            ]
            
            # This is just an example - in practice, be more selective
            if foreign_keys:
                queryset = queryset.select_related(*foreign_keys)
        
        return queryset
    
    @staticmethod
    def get_query_stats():
        """
        Get database query statistics
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    datname as database,
                    numbackends as connections,
                    xact_commit as commits,
                    xact_rollback as rollbacks,
                    tup_returned as rows_returned,
                    tup_fetched as rows_fetched,
                    tup_inserted as rows_inserted,
                    tup_updated as rows_updated,
                    tup_deleted as rows_deleted
                FROM pg_stat_database 
                WHERE datname = current_database();
            """)
            return cursor.fetchone()