from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from core.models import CustomUser
from employers.models import Employer
from candidates.models import Candidate
from core.serializers import SignupSerializer
from core.exceptions import APIResponse


class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def register_user(user_data):
        """Register a new user with role-based profile creation"""
        serializer = SignupSerializer(data=user_data)
        if not serializer.is_valid():
            return None, serializer.errors
        
        user = CustomUser.objects.create_user(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            role=serializer.validated_data['role'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name']
        )
        
        # Create role-specific profile
        if user.role == 'employer':
            Employer.objects.create(user=user)
        elif user.role == 'candidate':
            Candidate.objects.create(user=user)
        
        return user, None
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user and return user object"""
        if not email or not password:
            return None, "Email and password required"
        
        user = authenticate(username=email, password=password)
        if not user:
            return None, "Invalid credentials"
        
        return user, None
    
    @staticmethod
    def generate_tokens(user):
        """Generate JWT tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def logout_user(refresh_token):
        """Logout user by blacklisting refresh token"""
        try:
            if not refresh_token:
                return False, "Refresh token required"
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True, "Logout successful"
        except TokenError:
            return False, "Invalid token"
    
    @staticmethod
    def get_user_data(user):
        """Get formatted user data for response"""
        return {
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name
        }