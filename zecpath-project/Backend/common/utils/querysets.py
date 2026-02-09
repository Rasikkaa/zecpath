from django.db import models
from django.db.models import Prefetch, Count, Q

class OptimizedQuerysetMixin:
    """Mixin to provide optimized querysets for common operations"""
    
    @staticmethod
    def get_optimized_jobs_queryset():
        """Optimized queryset for jobs with related data"""
        return models.Job.objects.select_related(
            'employer',
            'employer__user'
        ).prefetch_related(
            Prefetch('application_set', 
                    queryset=models.Application.objects.select_related('candidate__user'))
        ).annotate(
            application_count=Count('application_set')
        )
    
    @staticmethod
    def get_optimized_applications_queryset():
        """Optimized queryset for applications with related data"""
        return models.Application.objects.select_related(
            'candidate',
            'candidate__user',
            'job',
            'job__employer',
            'job__employer__user'
        )
    
    @staticmethod
    def get_optimized_candidates_queryset():
        """Optimized queryset for candidates with related data"""
        return models.Candidate.objects.select_related('user').prefetch_related(
            Prefetch('application_set',
                    queryset=models.Application.objects.select_related('job__employer'))
        ).annotate(
            application_count=Count('application_set')
        )
    
    @staticmethod
    def get_optimized_employers_queryset():
        """Optimized queryset for employers with related data"""
        return models.Employer.objects.select_related('user').prefetch_related(
            Prefetch('job_set',
                    queryset=models.Job.objects.annotate(
                        application_count=Count('application_set')
                    ))
        ).annotate(
            job_count=Count('job_set'),
            total_applications=Count('job_set__application_set')
        )
    
    @staticmethod
    def get_optimized_users_queryset():
        """Optimized queryset for users with role-specific data"""
        return models.CustomUser.objects.prefetch_related(
            Prefetch('employer', 
                    queryset=models.Employer.objects.annotate(
                        job_count=Count('job_set')
                    )),
            Prefetch('candidate',
                    queryset=models.Candidate.objects.annotate(
                        application_count=Count('application_set')
                    ))
        )

# Import models after defining the mixin to avoid circular imports
from core import models