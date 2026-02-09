"""
Interview Reminder Service
"""
from django.utils import timezone
from datetime import timedelta
from core.interview_models import InterviewSchedule
from core.reminder_models import InterviewReminder
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    """Manage interview reminders"""
    
    REMINDER_STAGES = {
        '24h': timedelta(hours=24),
        '2h': timedelta(hours=2),
        '30min': timedelta(minutes=30),
    }
    
    @staticmethod
    def create_reminders_for_interview(schedule):
        """Create all reminder stages for an interview"""
        reminders_created = []
        
        for reminder_type, time_delta in ReminderService.REMINDER_STAGES.items():
            scheduled_at = schedule.interview_date - time_delta
            
            # Only create if scheduled time is in future
            if scheduled_at > timezone.now():
                reminder, created = InterviewReminder.objects.get_or_create(
                    schedule=schedule,
                    reminder_type=reminder_type,
                    defaults={'scheduled_at': scheduled_at}
                )
                if created:
                    reminders_created.append(reminder_type)
        
        return reminders_created
    
    @staticmethod
    def get_pending_reminders():
        """Get reminders that should be sent now"""
        now = timezone.now()
        
        return InterviewReminder.objects.filter(
            status='pending',
            scheduled_at__lte=now,
            schedule__status__in=['pending', 'confirmed']
        ).select_related('schedule__application__candidate__user', 'schedule__application__job')
    
    @staticmethod
    def mark_sent(reminder):
        """Mark reminder as sent"""
        reminder.status = 'sent'
        reminder.sent_at = timezone.now()
        reminder.save()
    
    @staticmethod
    def mark_failed(reminder, error_message):
        """Mark reminder as failed"""
        reminder.status = 'failed'
        reminder.error_message = error_message
        reminder.retry_count += 1
        reminder.save()
    
    @staticmethod
    def should_retry(reminder):
        """Check if reminder should be retried"""
        return reminder.retry_count < reminder.max_retries
    
    @staticmethod
    def cancel_reminders(schedule):
        """Cancel all pending reminders for a schedule"""
        InterviewReminder.objects.filter(
            schedule=schedule,
            status='pending'
        ).update(status='failed', error_message='Interview cancelled')
