from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response
from django.conf import settings
from django.core.paginator import Paginator

class StandardPageNumberPagination(PageNumberPagination):
    """Offset-based pagination with complete metadata"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

class InfiniteScrollPagination(CursorPagination):
    """Cursor-based pagination for infinite scroll"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'has_more': self.get_next_link() is not None
        })

class JobCursorPagination(CursorPagination):
    """Cursor-based pagination for real-time data"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
class ApplicationCursorPagination(CursorPagination):
    """Cursor-based pagination for applications"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    ordering = '-applied_at'
    cursor_query_param = 'cursor'

def paginate_queryset(queryset, request):
    """Helper function for manual pagination"""
    try:
        page_size = int(request.GET.get('page_size', 10))
        page_number = int(request.GET.get('page', 1))
        page_size = max(1, min(100, page_size))
        page_number = max(1, page_number)
    except (ValueError, TypeError):
        page_size = 10
        page_number = 1
    
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)
    
    return {
        'count': paginator.count,
        'next': f"?page={page_obj.next_page_number()}&page_size={page_size}" if page_obj.has_next() else None,
        'previous': f"?page={page_obj.previous_page_number()}&page_size={page_size}" if page_obj.has_previous() else None,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'page_obj': page_obj
    }