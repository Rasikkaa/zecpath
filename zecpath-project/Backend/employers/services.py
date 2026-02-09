from .models import Employer, Job
from .serializers import EmployerProfileSerializer, JobSerializer
from django.core.paginator import Paginator

class EmployerService:
    @staticmethod
    def get_employer_profile(user):
        try:
            employer = Employer.objects.get(user=user)
            return employer, None
        except Employer.DoesNotExist:
            return None, "Employer profile not found"
    
    @staticmethod
    def update_employer_profile(user, data):
        try:
            employer = Employer.objects.get(user=user)
            serializer = EmployerProfileSerializer(employer, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return employer, None
            return None, serializer.errors
        except Employer.DoesNotExist:
            return None, "Employer profile not found"

class JobService:
    @staticmethod
    def create_job(user, job_data):
        try:
            employer = Employer.objects.get(user=user)
            serializer = JobSerializer(data=job_data)
            if serializer.is_valid():
                job = serializer.save(employer=employer)
                return job, None
            return None, serializer.errors
        except Employer.DoesNotExist:
            return None, "Employer profile not found"
    
    @staticmethod
    def update_job(user, job_id, job_data):
        try:
            employer = Employer.objects.get(user=user)
            job = Job.objects.get(id=job_id, employer=employer)
            serializer = JobSerializer(job, data=job_data, partial=True)
            if serializer.is_valid():
                job = serializer.save()
                return job, None
            return None, serializer.errors
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return None, "Job not found or not owned by you"
    
    @staticmethod
    def delete_job(user, job_id):
        try:
            employer = Employer.objects.get(user=user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.delete()
            return True, "Job deleted successfully"
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return False, "Job not found or not owned by you"
    
    @staticmethod
    def get_employer_jobs(user, page_number=1, page_size=10):
        try:
            employer = Employer.objects.get(user=user)
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
        except Employer.DoesNotExist:
            return None, "Employer profile not found"