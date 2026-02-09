from core.models import Application
from employers.models import Job
from django.db.models import Q

class AutomationService:
    """ATS Automation Service for auto-shortlist and auto-reject"""
    
    @staticmethod
    def apply_auto_actions(application):
        """Apply automation rules to a single application"""
        job = application.job
        
        if not job.auto_shortlist_enabled:
            return None, "Automation disabled"
        
        score = application.match_score
        action_taken = None
        
        # Auto-shortlist
        if score >= job.auto_shortlist_threshold and application.status == 'pending':
            application.status = 'shortlisted'
            application.save()
            action_taken = 'auto_shortlisted'
        
        # Auto-reject
        elif score < job.auto_reject_threshold and application.status == 'pending':
            application.status = 'rejected'
            application.save()
            action_taken = 'auto_rejected'
        
        return action_taken, None
    
    @staticmethod
    def process_pending_applications(job_id):
        """Process all pending applications for a job"""
        try:
            job = Job.objects.get(id=job_id)
            
            if not job.auto_shortlist_enabled:
                return {'error': 'Automation not enabled for this job'}
            
            applications = Application.objects.filter(job=job, status='pending')
            
            results = {
                'total': applications.count(),
                'shortlisted': 0,
                'rejected': 0,
                'unchanged': 0
            }
            
            for app in applications:
                action, _ = AutomationService.apply_auto_actions(app)
                if action == 'auto_shortlisted':
                    results['shortlisted'] += 1
                elif action == 'auto_rejected':
                    results['rejected'] += 1
                else:
                    results['unchanged'] += 1
            
            return results
        except Job.DoesNotExist:
            return {'error': 'Job not found'}
    
    @staticmethod
    def bulk_process_applications():
        """Process all pending applications across all jobs with automation enabled"""
        jobs = Job.objects.filter(auto_shortlist_enabled=True, status='published')
        
        total_results = {
            'jobs_processed': 0,
            'total_applications': 0,
            'shortlisted': 0,
            'rejected': 0
        }
        
        for job in jobs:
            results = AutomationService.process_pending_applications(job.id)
            if 'error' not in results:
                total_results['jobs_processed'] += 1
                total_results['total_applications'] += results['total']
                total_results['shortlisted'] += results['shortlisted']
                total_results['rejected'] += results['rejected']
        
        return total_results
    
    @staticmethod
    def preview_auto_actions(job_id):
        """Preview what actions would be taken without applying them"""
        try:
            job = Job.objects.get(id=job_id)
            applications = Application.objects.filter(job=job, status='pending')
            
            preview = {
                'total_pending': applications.count(),
                'would_shortlist': applications.filter(match_score__gte=job.auto_shortlist_threshold).count(),
                'would_reject': applications.filter(match_score__lt=job.auto_reject_threshold).count(),
                'would_remain_pending': applications.filter(
                    match_score__gte=job.auto_reject_threshold,
                    match_score__lt=job.auto_shortlist_threshold
                ).count(),
                'thresholds': {
                    'shortlist': job.auto_shortlist_threshold,
                    'reject': job.auto_reject_threshold
                }
            }
            
            return preview, None
        except Job.DoesNotExist:
            return None, 'Job not found'
