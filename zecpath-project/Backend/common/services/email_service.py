from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from core.models import EmailLog
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Email sending service with template support and logging"""
    
    MAX_RETRIES = 3
    
    @staticmethod
    def send_email(recipient, subject, template_name, context, retry_count=0):
        """
        Send email with HTML template
        Returns: (success, error_message)
        """
        # Create email log
        email_log = EmailLog.objects.create(
            recipient=recipient,
            subject=subject,
            template_name=template_name,
            context_data=context,
            retry_count=retry_count
        )
        
        try:
            # Render HTML template
            html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=html_content,  # Fallback plain text
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            # Update log
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.save()
            
            logger.info(f"Email sent to {recipient}: {subject}")
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            email_log.status = 'failed'
            email_log.error_message = error_msg
            email_log.save()
            
            logger.error(f"Email failed to {recipient}: {error_msg}")
            
            # Retry logic
            if retry_count < EmailService.MAX_RETRIES:
                logger.info(f"Retrying email to {recipient} (attempt {retry_count + 1})")
                return EmailService.send_email(recipient, subject, template_name, context, retry_count + 1)
            
            return False, error_msg
    
    @staticmethod
    def send_application_submitted(application):
        """Send email when candidate submits application"""
        context = {
            'candidate_name': application.candidate.user.get_full_name() or application.candidate.user.email,
            'job_title': application.job.title,
            'company_name': application.job.employer.company_name or 'Company',
            'applied_date': application.applied_at.strftime('%B %d, %Y'),
        }
        
        return EmailService.send_email(
            recipient=application.candidate.user.email,
            subject=f'Application Submitted - {application.job.title}',
            template_name='application_submitted',
            context=context
        )
    
    @staticmethod
    def send_application_shortlisted(application):
        """Send email when candidate is shortlisted"""
        context = {
            'candidate_name': application.candidate.user.get_full_name() or application.candidate.user.email,
            'job_title': application.job.title,
            'company_name': application.job.employer.company_name or 'Company',
        }
        
        return EmailService.send_email(
            recipient=application.candidate.user.email,
            subject=f'Congratulations! You\'ve been shortlisted - {application.job.title}',
            template_name='application_shortlisted',
            context=context
        )
    
    @staticmethod
    def send_application_rejected(application):
        """Send email when application is rejected"""
        context = {
            'candidate_name': application.candidate.user.get_full_name() or application.candidate.user.email,
            'job_title': application.job.title,
            'company_name': application.job.employer.company_name or 'Company',
        }
        
        return EmailService.send_email(
            recipient=application.candidate.user.email,
            subject=f'Application Update - {application.job.title}',
            template_name='application_rejected',
            context=context
        )
    
    @staticmethod
    def send_new_application_to_employer(application):
        """Notify employer of new application"""
        context = {
            'employer_name': application.job.employer.user.get_full_name() or 'Employer',
            'candidate_name': application.candidate.user.get_full_name() or application.candidate.user.email,
            'job_title': application.job.title,
            'match_score': application.match_score,
            'applied_date': application.applied_at.strftime('%B %d, %Y'),
        }
        
        return EmailService.send_email(
            recipient=application.job.employer.user.email,
            subject=f'New Application Received - {application.job.title}',
            template_name='employer_new_application',
            context=context
        )
    
    @staticmethod
    def send_interview_scheduled(schedule):
        """Send email when interview is scheduled"""
        context = {
            'candidate_name': schedule.application.candidate.user.get_full_name() or schedule.application.candidate.user.email,
            'employer_name': schedule.application.job.employer.user.get_full_name() or 'Employer',
            'job_title': schedule.application.job.title,
            'interview_date': schedule.interview_date.strftime('%B %d, %Y at %I:%M %p'),
            'duration': schedule.duration_minutes,
            'meeting_link': schedule.meeting_link,
            'meeting_location': schedule.meeting_location,
        }
        
        # Send to candidate
        EmailService.send_email(
            recipient=schedule.application.candidate.user.email,
            subject=f'Interview Scheduled - {schedule.application.job.title}',
            template_name='interview_scheduled',
            context=context
        )
        
        # Send to employer
        EmailService.send_email(
            recipient=schedule.application.job.employer.user.email,
            subject=f'Interview Scheduled - {schedule.application.job.title}',
            template_name='interview_scheduled',
            context=context
        )
    
    @staticmethod
    def send_interview_confirmed(schedule):
        """Send email when interview is confirmed by both parties"""
        context = {
            'candidate_name': schedule.application.candidate.user.get_full_name() or schedule.application.candidate.user.email,
            'job_title': schedule.application.job.title,
            'interview_date': schedule.interview_date.strftime('%B %d, %Y at %I:%M %p'),
        }
        
        EmailService.send_email(
            recipient=schedule.application.candidate.user.email,
            subject=f'Interview Confirmed - {schedule.application.job.title}',
            template_name='interview_confirmed',
            context=context
        )
    
    @staticmethod
    def send_interview_rescheduled(schedule):
        """Send email when interview is rescheduled"""
        context = {
            'candidate_name': schedule.application.candidate.user.get_full_name() or schedule.application.candidate.user.email,
            'job_title': schedule.application.job.title,
            'new_date': schedule.interview_date.strftime('%B %d, %Y at %I:%M %p'),
        }
        
        # Send to candidate
        EmailService.send_email(
            recipient=schedule.application.candidate.user.email,
            subject=f'Interview Rescheduled - {schedule.application.job.title}',
            template_name='interview_rescheduled',
            context=context
        )
        
        # Send to employer
        EmailService.send_email(
            recipient=schedule.application.job.employer.user.email,
            subject=f'Interview Rescheduled - {schedule.application.job.title}',
            template_name='interview_rescheduled',
            context=context
        )
    
    @staticmethod
    def send_interview_reminder(schedule, reminder_type, recipient):
        """Send interview reminder email"""
        reminder_labels = {
            '24h': '24 hours',
            '2h': '2 hours',
            '30min': '30 minutes'
        }
        
        context = {
            'candidate_name': schedule.application.candidate.user.get_full_name() or schedule.application.candidate.user.email,
            'job_title': schedule.application.job.title,
            'company_name': schedule.application.job.employer.company_name or 'Company',
            'interview_date': schedule.interview_date.strftime('%B %d, %Y at %I:%M %p'),
            'reminder_time': reminder_labels.get(reminder_type, reminder_type),
            'meeting_link': schedule.meeting_link,
            'meeting_location': schedule.meeting_location,
        }
        
        return EmailService.send_email(
            recipient=recipient,
            subject=f'Interview Reminder - {schedule.application.job.title}',
            template_name=f'interview_reminder_{reminder_type}',
            context=context
        )
    
    @staticmethod
    def get_email_logs(recipient=None, status=None, limit=100):
        """Get email logs with filters"""
        logs = EmailLog.objects.all()
        
        if recipient:
            logs = logs.filter(recipient=recipient)
        if status:
            logs = logs.filter(status=status)
        
        return logs[:limit]
