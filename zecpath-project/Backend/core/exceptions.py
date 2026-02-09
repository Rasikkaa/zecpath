from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': 'An error occurred',
            'data': None,
            'errors': {}
        }
        
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_response_data['errors'] = exc.detail
                custom_response_data['message'] = 'Validation failed'
            elif isinstance(exc.detail, list):
                custom_response_data['errors'] = {'detail': exc.detail}
                custom_response_data['message'] = str(exc.detail[0]) if exc.detail else 'An error occurred'
            else:
                custom_response_data['message'] = str(exc.detail)
        
        # Handle specific status codes
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Bad request'
        elif response.status_code >= 500:
            custom_response_data['message'] = 'Internal server error'
        
        response.data = custom_response_data
    
    return response

class APIResponse:
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response({
            'success': True,
            'message': message,
            'data': data,
            'errors': {}
        }, status=status_code)
    
    @staticmethod
    def error(message="Error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response({
            'success': False,
            'message': message,
            'data': None,
            'errors': errors or {}
        }, status=status_code)
    
    @staticmethod
    def created(data=None, message="Created successfully"):
        return APIResponse.success(data, message, status.HTTP_201_CREATED)
    
    @staticmethod
    def unauthorized(message="Authentication required"):
        return APIResponse.error(message, status_code=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="Permission denied"):
        return APIResponse.error(message, status_code=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="Resource not found"):
        return APIResponse.error(message, status_code=status.HTTP_404_NOT_FOUND)