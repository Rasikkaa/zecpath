from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from core.permissions import IsEmployer, IsAdmin
from core.models import Application
from .models import Employer, Job
from .serializers import EmployerProfileSerializer, JobSerializer
from .services import EmployerService, JobService
from core.serializers import ApplicationSerializer
from common.utils.pagination import paginate_queryset
from django.core.exceptions import ValidationError

class EmployerProfileAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request):
        try:
            if request.user.role == 'admin':
                employer_id = request.GET.get('id')
                if employer_id:
                    employer = Employer.objects.get(id=employer_id)
                else:
                    return Response({'error': 'Employer ID required for admin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                employer = Employer.objects.get(user=request.user)
            serializer = EmployerProfileSerializer(employer)
            return Response(serializer.data)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        employer, error = EmployerService.update_employer_profile(request.user, request.data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmployerProfileSerializer(employer)
        return Response(serializer.data)
    
    def patch(self, request):
        return self.put(request)
    
    def delete(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            user = employer.user
            employer.delete()
            user.delete()
            return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class EmployerJobsAPI(APIView):
    permission_classes = [IsEmployer]
    
    def get(self, request):
        result, error = JobService.get_employer_jobs(request.user, 
                                                   request.GET.get('page', 1),
                                                   request.GET.get('page_size', 10))
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)

class JobCreateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            
            if not employer.verification:
                return Response({'error': 'Employer not verified. Wait for admin approval.'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            serializer = JobSerializer(data=request.data)
            if serializer.is_valid():
                job = serializer.save(employer=employer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class JobUpdateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def put(self, request, job_id):
        job, error = JobService.update_job(request.user, job_id, request.data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JobSerializer(job)
        return Response(serializer.data)
    
    def patch(self, request, job_id):
        return self.put(request, job_id)
    
    def delete(self, request, job_id):
        success, message = JobService.delete_job(request.user, job_id)
        if success:
            return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

class JobToggleStatusAPI(APIView):
    permission_classes = [IsEmployer]
    
    def patch(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            
            # Toggle between published and closed
            if job.status == 'published':
                job.status = 'closed'
                message = 'Job deactivated successfully'
            else:
                job.status = 'published'
                message = 'Job activated successfully'
            
            job.save()
            return Response({
                'message': message,
                'status': job.status
            })
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class JobActivateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.status = 'published'
            job.save()
            return Response({'message': 'Job published successfully'})
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class JobDeactivateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.status = 'closed'
            job.save()
            return Response({'message': 'Job closed successfully'})
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class JobApplicationsAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, job_id):
        try:
            if request.user.role == 'employer':
                job = Job.objects.get(id=job_id, employer__user=request.user)
            else:  # admin
                job = Job.objects.get(id=job_id)
            
            applications = Application.objects.filter(job=job).select_related('candidate__user').order_by('-applied_at')
            
            # Filter by ATS stage
            status_filter = request.GET.get('status')
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            # Search candidates
            search = request.GET.get('search')
            if search:
                applications = applications.filter(
                    Q(candidate__user__first_name__icontains=search) |
                    Q(candidate__user__last_name__icontains=search) |
                    Q(candidate__user__email__icontains=search)
                )
            
            result = paginate_queryset(applications, request)
            
            serializer = ApplicationSerializer(result['page_obj'], many=True, context={'request': request})
            result['results'] = serializer.data
            del result['page_obj']
            
            return Response(result)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class ShortlistCandidateAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, app_id):
        try:
            from common.utils.ats_rules import ATSWorkflowRules
            
            if request.user.role == 'employer':
                application = Application.objects.get(id=app_id, job__employer__user=request.user)
            else:
                application = Application.objects.get(id=app_id)
            
            ATSWorkflowRules.validate_transition(application.status, 'shortlisted')
            
            application._changed_by = request.user
            application.status = 'shortlisted'
            application.save()
            
            return Response({'message': 'Candidate shortlisted successfully'})
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RejectCandidateAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, app_id):
        try:
            from common.utils.ats_rules import ATSWorkflowRules
            
            if request.user.role == 'employer':
                application = Application.objects.get(id=app_id, job__employer__user=request.user)
            else:
                application = Application.objects.get(id=app_id)
            
            ATSWorkflowRules.validate_transition(application.status, 'rejected')
            
            application._changed_by = request.user
            application.status = 'rejected'
            application.save()
            
            return Response({'message': 'Candidate rejected'})
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmployerDashboardAPI(APIView):
    permission_classes = [IsEmployer]
    
    def get(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            
            # Get analytics data
            jobs = Job.objects.filter(employer=employer)
            applications = Application.objects.filter(job__employer=employer)
            
            # Calculate metrics
            total_jobs = jobs.count()
            total_applications = applications.count()
            shortlisted = applications.filter(status='shortlisted').count()
            selected = applications.filter(status='selected').count()
            
            # Status distribution
            status_counts = {}
            for status_choice in Application.STATUS_CHOICES:
                status = status_choice[0]
                count = applications.filter(status=status).count()
                status_counts[status] = count
            
            # Calculate ratios
            shortlist_ratio = (shortlisted / total_applications * 100) if total_applications > 0 else 0
            selection_ratio = (selected / total_applications * 100) if total_applications > 0 else 0
            
            analytics = {
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'shortlisted_count': shortlisted,
                'selected_count': selected,
                'shortlist_ratio': round(shortlist_ratio, 2),
                'selection_ratio': round(selection_ratio, 2),
                'status_distribution': status_counts
            }
            
            return Response(analytics)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)