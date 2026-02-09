"""
Day 39 - Interview Reminder Models
"""
from django.db import models
from core.interview_models import InterviewSchedule


class InterviewReminder(models.Model):
    REMINDER_TYPES = [
        ('24h', '24 Hours Before'),
        ('2h', '2 Hours Before'),
        ('30min', '30 Minutes Before'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    schedule = models.ForeignKey(InterviewSchedule, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    scheduled_at = models.DateTimeField(db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['schedule', 'reminder_type']
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.reminder_type} reminder for {self.schedule}"
