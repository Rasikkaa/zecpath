from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

@shared_task(name='send_email_task')
def send_email_task(subject, message, recipient_list, html_message=None):
    """Async task for sending emails"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Email sent to {recipient_list}")
        return {'status': 'success', 'recipients': recipient_list}
    except Exception as e:
        logger.error(f"Email failed: {str(e)}")
        raise

@shared_task(name='parse_resume_task')
def parse_resume_task(resume_path):
    """Async task for parsing resumes"""
    from common.services.resume_analyzer import ResumeAnalyzer
    try:
        analyzer = ResumeAnalyzer()
        result = analyzer.analyze_resume(resume_path)
        logger.info(f"Resume parsed: {resume_path}")
        return result
    except Exception as e:
        logger.error(f"Resume parsing failed: {str(e)}")
        raise

@shared_task(name='calculate_ats_score_task')
def calculate_ats_score_task(application_id):
    """Async task for calculating ATS match score"""
    from core.models import Application
    from common.services.ats_scoring import ATSScoring
    try:
        application = Application.objects.get(id=application_id)
        scorer = ATSScoring()
        score_data = scorer.calculate_match_score(application.candidate, application.job)
        
        application.match_score = score_data['overall_score']
        application.match_breakdown = score_data
        application.save()
        
        logger.info(f"ATS score calculated for application {application_id}: {score_data['overall_score']}")
        return score_data
    except Exception as e:
        logger.error(f"ATS scoring failed: {str(e)}")
        raise

@shared_task(name='cleanup_old_logs')
def cleanup_old_logs():
    """Periodic task for cleaning up old logs"""
    from datetime import timedelta
    from django.utils import timezone
    from core.models import EmailLog
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = EmailLog.objects.filter(created_at__lt=cutoff_date).delete()[0]
    logger.info(f"Cleaned up {deleted_count} old email logs")
    return {'deleted': deleted_count}
