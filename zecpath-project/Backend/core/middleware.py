from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class RoleSecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Log suspicious access attempts
        if request.user.is_authenticated:
            role = getattr(request.user, 'role', None)
            path = request.path
            
            # Log admin access attempts
            if 'admin' in path and role != 'admin':
                logger.warning(f"Non-admin user {request.user.email} attempted admin access: {path}")
            
            # Log role mismatches for API endpoints
            if path.startswith('/api/'):
                if 'jobs/create' in path and role != 'employer':
                    logger.warning(f"Non-employer {request.user.email} attempted job creation")
                elif 'applications' in path and role not in ['candidate', 'admin']:
                    logger.warning(f"Unauthorized role {role} attempted application access")
        
        return None