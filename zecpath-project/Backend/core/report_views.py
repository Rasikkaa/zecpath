"""
Day 40 - Candidate Report API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsEmployer, IsAdmin
from core.models import Application
from common.services.report_generator import CandidateReportGenerator


class CandidateReportAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, application_id):
        """Generate candidate evaluation report"""
        try:
            # Check access
            if request.user.role == 'employer':
                application = Application.objects.get(
                    id=application_id,
                    job__employer__user=request.user
                )
            else:
                application = Application.objects.get(id=application_id)
            
            # Generate report
            report, error = CandidateReportGenerator.generate_report(application_id)
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(report)
            
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)


class BulkReportsAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request):
        """Generate reports for multiple candidates"""
        application_ids = request.data.get('application_ids', [])
        
        if not application_ids:
            return Response({'error': 'application_ids required'}, status=status.HTTP_400_BAD_REQUEST)
        
        reports = []
        errors = []
        
        for app_id in application_ids:
            try:
                # Check access
                if request.user.role == 'employer':
                    Application.objects.get(id=app_id, job__employer__user=request.user)
                
                report, error = CandidateReportGenerator.generate_report(app_id)
                
                if error:
                    errors.append({'application_id': app_id, 'error': error})
                else:
                    reports.append(report)
                    
            except Application.DoesNotExist:
                errors.append({'application_id': app_id, 'error': 'Not found or no access'})
        
        return Response({
            'reports': reports,
            'errors': errors,
            'total': len(application_ids),
            'success': len(reports),
            'failed': len(errors),
        })


class JobReportsAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request, job_id):
        """Generate reports for all candidates of a job"""
        try:
            from employers.models import Job
            
            # Check access
            if request.user.role == 'employer':
                job = Job.objects.get(id=job_id, employer__user=request.user)
            else:
                job = Job.objects.get(id=job_id)
            
            # Get applications
            applications = Application.objects.filter(job=job)
            
            # Filter by status
            status_filter = request.GET.get('status')
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            # Generate reports
            reports = []
            for app in applications:
                report, error = CandidateReportGenerator.generate_report(app.id)
                if not error:
                    reports.append(report)
            
            # Sort by overall rating
            reports.sort(key=lambda x: x['overall_rating']['score'], reverse=True)
            
            return Response({
                'job_id': job_id,
                'job_title': job.title,
                'total_candidates': len(reports),
                'reports': reports,
            })
            
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
