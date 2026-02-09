from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsEmployer, IsAdmin
from employers.models import Job
from common.services.automation_service import AutomationService

class JobAutomationSettingsAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, employer__user=request.user)
            return Response({
                'auto_shortlist_enabled': job.auto_shortlist_enabled,
                'auto_shortlist_threshold': job.auto_shortlist_threshold,
                'auto_reject_threshold': job.auto_reject_threshold
            })
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, employer__user=request.user)
            
            job.auto_shortlist_enabled = request.data.get('auto_shortlist_enabled', job.auto_shortlist_enabled)
            job.auto_shortlist_threshold = request.data.get('auto_shortlist_threshold', job.auto_shortlist_threshold)
            job.auto_reject_threshold = request.data.get('auto_reject_threshold', job.auto_reject_threshold)
            
            # Validation
            if job.auto_reject_threshold >= job.auto_shortlist_threshold:
                return Response({'error': 'Reject threshold must be less than shortlist threshold'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            job.save()
            return Response({
                'message': 'Automation settings updated',
                'auto_shortlist_enabled': job.auto_shortlist_enabled,
                'auto_shortlist_threshold': job.auto_shortlist_threshold,
                'auto_reject_threshold': job.auto_reject_threshold
            })
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class JobAutomationRunAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, employer__user=request.user)
            
            if not job.auto_shortlist_enabled:
                return Response({'error': 'Automation not enabled for this job'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            results = AutomationService.process_pending_applications(job_id)
            
            if 'error' in results:
                return Response(results, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'message': 'Automation completed',
                'results': results
            })
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class JobAutomationPreviewAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, employer__user=request.user)
            preview, error = AutomationService.preview_auto_actions(job_id)
            
            if error:
                return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(preview)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
