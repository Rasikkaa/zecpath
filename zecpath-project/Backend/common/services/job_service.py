from django.core.paginator import Paginator
from employers.models import Job, Employer
from candidates.models import Candidate
from core.models import CustomUser, Application
from employers.serializers import JobSerializer
from core.serializers import ApplicationSerializer
from common.utils.querysets import OptimizedQuerysetMixin


class JobService(OptimizedQuerysetMixin):
    """Service class for job-related operations"""
    
    @staticmethod
    def get_paginated_jobs(page_number=1, page_size=10):
        """Get paginated list of jobs with optimized queries"""
        try:
            page_size = max(1, min(100, int(page_size)))  # Limit page size
            page_number = max(1, int(page_number))
        except (ValueError, TypeError):
            page_size = 10
            page_number = 1
        
        jobs = JobService.get_optimized_jobs_queryset().filter(status='published').order_by('-created_at')
        paginator = Paginator(jobs, page_size)
        page_obj = paginator.get_page(page_number)
        
        return {
            'count': paginator.count,
            'next': f"?page={page_obj.next_page_number()}&page_size={page_size}" if page_obj.has_next() else None,
            'previous': f"?page={page_obj.previous_page_number()}&page_size={page_size}" if page_obj.has_previous() else None,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': JobSerializer(page_obj, many=True).data
        }
    
    @staticmethod
    def create_job(user, job_data):
        """Create a new job for employer"""
        try:
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist:
            return None, "Employer profile not found"
        
        serializer = JobSerializer(data=job_data)
        if serializer.is_valid():
            job = serializer.save(employer=employer)
            return job, None
        return None, serializer.errors
    
    @staticmethod
    def update_job(user, job_id, job_data):
        """Update job if user owns it"""
        try:
            employer = Employer.objects.get(user=user)
            job = Job.objects.get(id=job_id, employer=employer)
        except Employer.DoesNotExist:
            return None, "Employer profile not found"
        except Job.DoesNotExist:
            return None, "Job not found or not owned by you"
        
        serializer = JobSerializer(job, data=job_data, partial=True)
        if serializer.is_valid():
            job = serializer.save()
            return job, None
        return None, serializer.errors
    
    @staticmethod
    def delete_job(user, job_id):
        """Delete job if user owns it"""
        try:
            employer = Employer.objects.get(user=user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.delete()
            return True, "Job deleted successfully"
        except Employer.DoesNotExist:
            return False, "Employer profile not found"
        except Job.DoesNotExist:
            return False, "Job not found or not owned by you"
    
    @staticmethod
    def apply_to_job(user, job_id):
        """Apply to a job as candidate"""
        try:
            job = Job.objects.get(id=job_id, status='published')
            candidate = getattr(user, 'candidate', None)
            
            if not candidate:
                return None, "Candidate profile not found"
            
            # Check if already applied
            if Application.objects.filter(candidate=candidate, job=job).exists():
                return None, "Already applied to this job"
            
            application = Application.objects.create(candidate=candidate, job=job)
            return application, None
            
        except Job.DoesNotExist:
            return None, "Job not found or not available"
    
    @staticmethod
    def get_employer_jobs(user, page_number=1, page_size=10):
        """Get paginated jobs for employer"""
        try:
            employer = Employer.objects.get(user=user)
        except Employer.DoesNotExist:
            return None, "Employer profile not found"
        
        try:
            page_size = max(1, min(100, int(page_size)))
            page_number = max(1, int(page_number))
        except (ValueError, TypeError):
            page_size = 10
            page_number = 1
        
        jobs = Job.objects.filter(employer=employer).order_by('-created_at')
        paginator = Paginator(jobs, page_size)
        page_obj = paginator.get_page(page_number)
        
        return {
            'count': paginator.count,
            'next': f"?page={page_obj.next_page_number()}&page_size={page_size}" if page_obj.has_next() else None,
            'previous': f"?page={page_obj.previous_page_number()}&page_size={page_size}" if page_obj.has_previous() else None,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': JobSerializer(page_obj, many=True).data
        }, None