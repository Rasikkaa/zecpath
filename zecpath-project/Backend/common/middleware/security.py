from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import time


class RateLimitMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware"""
    
    RATE_LIMITS = {
        'login': (5, 300),      # 5 attempts per 5 minutes
        'signup': (3, 600),     # 3 attempts per 10 minutes
        'default': (100, 60),   # 100 requests per minute
    }
    
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Determine rate limit
        if 'login' in request.path:
            limit, window = self.RATE_LIMITS['login']
            key = f'ratelimit:login:{ip}'
        elif 'signup' in request.path:
            limit, window = self.RATE_LIMITS['signup']
            key = f'ratelimit:signup:{ip}'
        else:
            limit, window = self.RATE_LIMITS['default']
            key = f'ratelimit:default:{ip}'
        
        # Check rate limit
        current = cache.get(key, 0)
        if current >= limit:
            return JsonResponse({
                'success': False,
                'message': 'Rate limit exceeded. Try again later.',
                'data': None,
                'errors': {}
            }, status=429)
        
        # Increment counter
        cache.set(key, current + 1, window)
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses"""
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # HTTPS only
        if not request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'"
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
