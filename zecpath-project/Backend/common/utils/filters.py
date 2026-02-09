from django.db import models
from django.db.models import Q
from employers.models import Job, Employer
from candidates.models import Candidate
from core.models import CustomUser, Application

class JobFilter:
    """Manual job filtering without django-filter dependency"""
    
    @staticmethod
    def filter_queryset(queryset, params):
        """Apply filters to job queryset"""
        
        # Skills filter
        if params.get('skills'):
            skills_list = [skill.strip() for skill in params.get('skills').split(',')]
            for skill in skills_list:
                queryset = queryset.filter(skills__icontains=skill)
        
        # Salary filters
        if params.get('salary_min'):
            queryset = queryset.filter(salary_min__gte=params.get('salary_min'))
        if params.get('salary_max'):
            queryset = queryset.filter(salary_max__lte=params.get('salary_max'))
        
        # Location filter
        if params.get('location'):
            queryset = queryset.filter(location__icontains=params.get('location'))
        
        # Job type filter
        if params.get('job_type'):
            queryset = queryset.filter(job_type=params.get('job_type'))
        
        # Featured filter
        if params.get('is_featured'):
            queryset = queryset.filter(is_featured=params.get('is_featured').lower() == 'true')
        
        # Status filter
        if params.get('status'):
            queryset = queryset.filter(status=params.get('status'))
        
        return queryset.order_by('-is_featured', '-created_at')