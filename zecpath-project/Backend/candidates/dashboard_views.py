from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from core.permissions import IsCandidate
from core.models import Application, ApplicationStatusHistory
from employers.models import Job
from .models import Candidate, SavedJob
from .serializers import CandidateProfileSerializer
from employers.serializers import JobSerializer
from core.serializers import ApplicationSerializer
from common.utils.pagination import paginate_queryset

class CandidateDashboardAPI(APIView):
    permission_classes = [IsCandidate]
    
    def get(self, request):
        candidate = Candidate.objects.get(user=request.user)
        applications = Application.objects.filter(candidate=candidate)
        
        stats = {
            'total_applications': applications.count(),
            'pending': applications.filter(status='pending').count(),
            'shortlisted': applications.filter(status='shortlisted').count(),
            'interview_scheduled': applications.filter(status='interview_scheduled').count(),
            'reviewed': applications.filter(status='reviewed').count(),
            'accepted': applications.filter(status='accepted').count(),
            'rejected': applications.filter(status='rejected').count(),
            'selected': applications.filter(status='selected').count(),
            'saved_jobs': SavedJob.objects.filter(candidate=candidate).count(),
        }
        return Response(stats)

class JobRecommendationsAPI(APIView):
    permission_classes = [IsCandidate]
    
    def get(self, request):
        candidate = Candidate.objects.get(user=request.user)
        
        # Get candidate skills
        candidate_skills = candidate.skills if isinstance(candidate.skills, list) else []
        
        # Base queryset
        jobs = Job.objects.filter(status='published').select_related('employer__user')
        
        # Exclude already applied
        applied_job_ids = Application.objects.filter(candidate=candidate).values_list('job_id', flat=True)
        jobs = jobs.exclude(id__in=applied_job_ids)
        
        # Match by skills
        if candidate_skills:
            q_objects = Q()
            for skill in candidate_skills:
                q_objects |= Q(skills__icontains=skill)
            jobs = jobs.filter(q_objects)
        
        # Match by experience
        if candidate.experience_years:
            jobs = jobs.filter(experience__icontains=str(candidate.experience_years))
        
        # Match by salary
        if candidate.expected_salary:
            jobs = jobs.filter(
                Q(salary_min__lte=candidate.expected_salary) | Q(salary_min__isnull=True)
            )
        
        jobs = jobs.order_by('-is_featured', '-created_at')
        
        result = paginate_queryset(jobs, request)
        serializer = JobSerializer(result['page_obj'], many=True)
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result)

class SavedJobsAPI(APIView):
    permission_classes = [IsCandidate]
    
    def get(self, request):
        candidate = Candidate.objects.get(user=request.user)
        saved_jobs = SavedJob.objects.filter(candidate=candidate).select_related('job__employer__user')
        
        result = paginate_queryset(saved_jobs, request)
        jobs = [saved.job for saved in result['page_obj']]
        serializer = JobSerializer(jobs, many=True)
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result)

class SaveJobAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request, job_id):
        try:
            candidate = Candidate.objects.get(user=request.user)
            job = Job.objects.get(id=job_id)
            
            saved_job, created = SavedJob.objects.get_or_create(candidate=candidate, job=job)
            
            if created:
                return Response({'message': 'Job saved successfully'}, status=status.HTTP_201_CREATED)
            return Response({'message': 'Job already saved'}, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, job_id):
        try:
            candidate = Candidate.objects.get(user=request.user)
            saved_job = SavedJob.objects.get(candidate=candidate, job_id=job_id)
            saved_job.delete()
            return Response({'message': 'Job unsaved successfully'}, status=status.HTTP_204_NO_CONTENT)
        except SavedJob.DoesNotExist:
            return Response({'error': 'Saved job not found'}, status=status.HTTP_404_NOT_FOUND)

class InterviewStatusAPI(APIView):
    permission_classes = [IsCandidate]
    
    def get(self, request):
        candidate = Candidate.objects.get(user=request.user)
        applications = Application.objects.filter(
            candidate=candidate,
            status='interview_scheduled'
        ).select_related('job__employer__user').order_by('-applied_at')
        
        result = paginate_queryset(applications, request)
        serializer = ApplicationSerializer(result['page_obj'], many=True, context={'request': request})
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result)

class ApplicationTimelineAPI(APIView):
    permission_classes = [IsCandidate]
    
    def get(self, request, app_id):
        try:
            candidate = Candidate.objects.get(user=request.user)
            application = Application.objects.get(id=app_id, candidate=candidate)
            
            history = ApplicationStatusHistory.objects.filter(application=application).order_by('changed_at')
            
            timeline = [{
                'old_status': h.old_status,
                'new_status': h.new_status,
                'changed_at': h.changed_at,
                'changed_by': h.changed_by.email
            } for h in history]
            
            return Response({
                'application_id': application.id,
                'job_title': application.job.title,
                'current_status': application.status,
                'applied_at': application.applied_at,
                'timeline': timeline
            })
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
