"""
Celery tasks for interview reminders
"""
from celery import shared_task
from django.utils import timezone
from core.reminder_models import InterviewReminder
from common.services.reminder_service import ReminderService
from common.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


@shared_task(name='scan_and_send_reminders')
def scan_and_send_reminders():
    """Periodic task to scan and send pending reminders"""
    pending_reminders = ReminderService.get_pending_reminders()
    
    results = {
        'scanned': pending_reminders.count(),
        'sent': 0,
        'failed': 0
    }
    
    for reminder in pending_reminders:
        try:
            send_reminder_task.delay(reminder.id)
            results['sent'] += 1
        except Exception as e:
            logger.error(f"Failed to queue reminder {reminder.id}: {str(e)}")
            results['failed'] += 1
    
    logger.info(f"Reminder scan complete: {results}")
    return results


@shared_task(name='send_reminder', bind=True, max_retries=3)
def send_reminder_task(self, reminder_id):
    """Send individual reminder"""
    try:
        reminder = InterviewReminder.objects.select_related(
            'schedule__application__candidate__user',
            'schedule__application__job__employer__user'
        ).get(id=reminder_id)
        
        schedule = reminder.schedule
        candidate = schedule.application.candidate
        job = schedule.application.job
        
        # Send to candidate
        EmailService.send_interview_reminder(
            schedule=schedule,
            reminder_type=reminder.reminder_type,
            recipient=candidate.user.email
        )
        
        # Send to employer
        EmailService.send_interview_reminder(
            schedule=schedule,
            reminder_type=reminder.reminder_type,
            recipient=job.employer.user.email
        )
        
        ReminderService.mark_sent(reminder)
        logger.info(f"Reminder sent: {reminder_id} ({reminder.reminder_type})")
        
        return {'status': 'sent', 'reminder_id': reminder_id}
        
    except InterviewReminder.DoesNotExist:
        logger.error(f"Reminder {reminder_id} not found")
        return {'status': 'error', 'message': 'Reminder not found'}
        
    except Exception as e:
        logger.error(f"Reminder failed: {reminder_id} - {str(e)}")
        
        reminder = InterviewReminder.objects.get(id=reminder_id)
        ReminderService.mark_failed(reminder, str(e))
        
        if ReminderService.should_retry(reminder):
            retry_delay = 60 * (2 ** reminder.retry_count)
            logger.info(f"Retrying reminder {reminder_id} in {retry_delay}s")
            raise self.retry(exc=e, countdown=retry_delay)
        
        return {'status': 'failed', 'message': str(e)}


@shared_task(name='create_reminders_for_new_interview')
def create_reminders_for_new_interview(schedule_id):
    """Create reminders when interview is scheduled"""
    from core.interview_models import InterviewSchedule
    
    try:
        schedule = InterviewSchedule.objects.get(id=schedule_id)
        reminders = ReminderService.create_reminders_for_interview(schedule)
        logger.info(f"Created reminders for interview {schedule_id}: {reminders}")
        return {'status': 'created', 'reminders': reminders}
    except Exception as e:
        logger.error(f"Failed to create reminders: {str(e)}")
        return {'status': 'error', 'message': str(e)}
