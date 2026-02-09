"""
Day 38 - Interview Scheduling Models
"""
from django.db import models
from core.models import Application, CustomUser


class AvailabilitySlot(models.Model):
    """Store available time slots for employers/candidates"""
    ROLE_CHOICES = [
        ('employer', 'Employer'),
        ('candidate', 'Candidate'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availability_slots')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    day_of_week = models.IntegerField()  # 0=Monday, 6=Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'day_of_week', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_day_display()} {self.start_time}-{self.end_time}"
    
    def get_day_display(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.day_of_week]


class InterviewSchedule(models.Model):
    """Interview scheduling with confirmation"""
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateTimeField(db_index=True)
    duration_minutes = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Confirmation tracking
    employer_confirmed = models.BooleanField(default=False)
    candidate_confirmed = models.BooleanField(default=False)
    
    # Meeting details
    meeting_link = models.URLField(blank=True)
    meeting_location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    # Rescheduling
    reschedule_count = models.IntegerField(default=0)
    max_reschedules = models.IntegerField(default=2)
    previous_schedule = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['interview_date']
        indexes = [
            models.Index(fields=['status', 'interview_date']),
            models.Index(fields=['application', 'status']),
        ]
    
    def __str__(self):
        return f"Interview - {self.application} - {self.interview_date}"
    
    def is_confirmed(self):
        return self.employer_confirmed and self.candidate_confirmed
    
    def can_reschedule(self):
        return self.reschedule_count < self.max_reschedules
