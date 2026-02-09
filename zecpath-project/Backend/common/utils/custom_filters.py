from django.db import models
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

class CustomFilterBackend(BaseFilterBackend):
    """Custom filter backend for basic filtering without django-filter dependency"""
    
    def filter_queryset(self, request, queryset, view):
        # Role filtering
        role = request.query_params.get('role')
        if role and hasattr(queryset.model, 'role'):
            queryset = queryset.filter(role=role)
        
        # Status filtering
        status = request.query_params.get('status')
        if status and hasattr(queryset.model, 'status'):
            queryset = queryset.filter(status=status)
        
        # Date filtering
        created_after = request.query_params.get('created_after')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        
        created_before = request.query_params.get('created_before')
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        # Location filtering
        location = request.query_params.get('location')
        if location and hasattr(queryset.model, 'location'):
            queryset = queryset.filter(location__icontains=location)
        
        # Title filtering
        title = request.query_params.get('title')
        if title and hasattr(queryset.model, 'title'):
            queryset = queryset.filter(title__icontains=title)
        
        # Company filtering
        company = request.query_params.get('company')
        if company:
            if hasattr(queryset.model, 'employer'):
                queryset = queryset.filter(employer__company_name__icontains=company)
        
        # Verification filtering
        verification = request.query_params.get('verification')
        if verification is not None and hasattr(queryset.model, 'verification'):
            queryset = queryset.filter(verification=verification.lower() == 'true')
        
        # Experience filtering
        exp_min = request.query_params.get('experience_years_min')
        if exp_min and hasattr(queryset.model, 'experience_years'):
            queryset = queryset.filter(experience_years__gte=exp_min)
        
        exp_max = request.query_params.get('experience_years_max')
        if exp_max and hasattr(queryset.model, 'experience_years'):
            queryset = queryset.filter(experience_years__lte=exp_max)
        
        # Salary filtering
        salary_min = request.query_params.get('expected_salary_min')
        if salary_min and hasattr(queryset.model, 'expected_salary'):
            queryset = queryset.filter(expected_salary__gte=salary_min)
        
        salary_max = request.query_params.get('expected_salary_max')
        if salary_max and hasattr(queryset.model, 'expected_salary'):
            queryset = queryset.filter(expected_salary__lte=salary_max)
        
        return queryset