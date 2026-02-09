from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Application, ApplicationStatusHistory

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'employer':
            from employers.models import Employer
            Employer.objects.create(user=instance)
        elif instance.role == 'candidate':
            from candidates.models import Candidate
            Candidate.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'employer' and hasattr(instance, 'employer'):
        instance.employer.save()
    elif instance.role == 'candidate' and hasattr(instance, 'candidate'):
        instance.candidate.save()

@receiver(post_save, sender=Application)
def log_status_change(sender, instance, **kwargs):
    if hasattr(instance, '_status_changed') and instance._status_changed:
        ApplicationStatusHistory.objects.create(
            application=instance,
            old_status=instance._old_status,
            new_status=instance.status,
            changed_by=getattr(instance, '_changed_by', None) or instance.candidate.user
        )

@receiver(post_save, sender=Application)
def send_notification_emails(sender, instance, created, **kwargs):
    """Send emails on application events"""
    from common.services.email_service import EmailService
    
    if created:
        # New application submitted
        EmailService.send_application_submitted(instance)
        EmailService.send_new_application_to_employer(instance)
    
    elif hasattr(instance, '_status_changed') and instance._status_changed:
        # Status changed
        if instance.status == 'shortlisted':
            EmailService.send_application_shortlisted(instance)
        elif instance.status == 'rejected':
            EmailService.send_application_rejected(instance)

@receiver(post_save, sender=Application)
def trigger_ai_call(sender, instance, created, **kwargs):
    """Trigger AI call when application is shortlisted"""
    if hasattr(instance, '_status_changed') and instance._status_changed:
        if instance.status == 'shortlisted':
            from common.tasks_ai_calls import schedule_ai_call_task
            schedule_ai_call_task.delay(instance.id)