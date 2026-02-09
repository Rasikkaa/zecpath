from django.core.cache import cache
from functools import wraps
import hashlib
import json

class CacheService:
    """Simple caching service"""
    
    # Cache timeouts (seconds)
    TIMEOUT_SHORT = 300      # 5 minutes
    TIMEOUT_MEDIUM = 1800    # 30 minutes
    TIMEOUT_LONG = 3600      # 1 hour
    
    @staticmethod
    def get(key):
        return cache.get(key)
    
    @staticmethod
    def set(key, value, timeout=TIMEOUT_MEDIUM):
        cache.set(key, value, timeout)
    
    @staticmethod
    def delete(key):
        cache.delete(key)
    
    @staticmethod
    def clear_pattern(pattern):
        """Clear all keys matching pattern"""
        cache.delete_pattern(pattern)

def cache_response(timeout=300, key_prefix='view'):
    """Decorator to cache view response data"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{request.path}:{request.GET.urlencode()}"
            
            # Try cache
            cached_data = cache.get(cache_key)
            if cached_data:
                from rest_framework.response import Response
                return Response(cached_data)
            
            # Execute view
            response = func(self, request, *args, **kwargs)
            
            # Cache only the data, not the response object
            if hasattr(response, 'data'):
                cache.set(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator

def invalidate_cache(patterns):
    """Invalidate cache patterns after model changes"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for pattern in patterns:
                CacheService.clear_pattern(pattern)
            return result
        return wrapper
    return decorator
