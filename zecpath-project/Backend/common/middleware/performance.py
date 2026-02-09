from django.db import connection
from django.utils.deprecation import MiddlewareMixin
import time
import logging

logger = logging.getLogger(__name__)

class QueryCountMiddleware(MiddlewareMixin):
    """Monitor database query count and execution time"""
    
    def process_request(self, request):
        request._query_start_time = time.time()
        request._query_count = len(connection.queries)
    
    def process_response(self, request, response):
        if hasattr(request, '_query_start_time'):
            total_time = time.time() - request._query_start_time
            query_count = len(connection.queries) - request._query_count
            
            if total_time > 1.0 or query_count > 20:
                logger.warning(
                    f"SLOW: {request.method} {request.path} | "
                    f"Time: {total_time:.2f}s | Queries: {query_count}"
                )
            
            response['X-Query-Count'] = str(query_count)
            response['X-Response-Time'] = f"{total_time:.3f}s"
        
        return response
