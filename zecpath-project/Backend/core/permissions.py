from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        print(f"IsEmployer check - User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"User role: {getattr(request.user, 'role', 'No role')}")
        result = request.user.is_authenticated and request.user.role == 'employer'
        print(f"Permission result: {result}")
        return result

class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'candidate'

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'employer'):
            return obj.employer.user == request.user
        return False