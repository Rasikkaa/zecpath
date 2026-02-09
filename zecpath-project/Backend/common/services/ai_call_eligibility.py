from datetime import datetime, timedelta
from django.utils import timezone

class AICallEligibility:
    """Eligibility engine for AI call triggers"""
    
    # Business rules
    MIN_ATS_SCORE = 0  # Allow any score for testing
    CALL_WINDOW_START = 9  # 9 AM
    CALL_WINDOW_END = 18   # 6 PM
    
    @staticmethod
    def is_eligible(application):
        """Check if application is eligible for AI call"""
        checks = {
            'ats_score': AICallEligibility._check_ats_score(application),
            'job_status': AICallEligibility._check_job_status(application),
            'candidate_available': AICallEligibility._check_candidate_availability(application),
            'not_already_called': AICallEligibility._check_not_called(application),
            'status_valid': AICallEligibility._check_status(application),
        }
        
        return all(checks.values()), checks
    
    @staticmethod
    def _check_ats_score(application):
        """ATS score >= threshold"""
        return application.match_score >= AICallEligibility.MIN_ATS_SCORE
    
    @staticmethod
    def _check_job_status(application):
        """Job must be published"""
        return application.job.status == 'published'
    
    @staticmethod
    def _check_candidate_availability(application):
        """Candidate marked as available"""
        return getattr(application.candidate, 'is_available_for_call', True)
    
    @staticmethod
    def _check_not_called(application):
        """Not already in call queue"""
        from core.ai_call_models import AICallQueue
        return not AICallQueue.objects.filter(
            application=application,
            status__in=['queued', 'in_progress']
        ).exists()
    
    @staticmethod
    def _check_status(application):
        """Application status is shortlisted or interview_scheduled"""
        return application.status in ['shortlisted', 'interview_scheduled']
    
    @staticmethod
    def get_next_call_slot():
        """Calculate next available call slot within business hours"""
        now = timezone.now()
        
        # If within call window, schedule in 5 minutes
        if AICallEligibility.CALL_WINDOW_START <= now.hour < AICallEligibility.CALL_WINDOW_END:
            return now + timedelta(minutes=5)
        
        # Otherwise, schedule for next day at 9 AM
        next_day = now + timedelta(days=1)
        return next_day.replace(hour=AICallEligibility.CALL_WINDOW_START, minute=0, second=0)
    
    @staticmethod
    def should_retry(call_queue):
        """Check if failed call should be retried"""
        return call_queue.retry_count < call_queue.max_retries
