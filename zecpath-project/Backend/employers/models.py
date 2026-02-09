from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, blank=True, db_index=True)
    website = models.URLField(blank=True)
    domain = models.CharField(max_length=100, blank=True, db_index=True)
    company_description = models.TextField(blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    verification = models.BooleanField(default=False, db_index=True)
    
    def __str__(self):
        return self.company_name or self.user.email

class Job(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    skills = models.JSONField(default=list, blank=True)
    experience = models.CharField(max_length=100, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=100, db_index=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    auto_shortlist_enabled = models.BooleanField(default=False)
    auto_shortlist_threshold = models.IntegerField(default=80)
    auto_reject_threshold = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['location', 'status']),
            models.Index(fields=['title', 'status']),
            models.Index(fields=['job_type', 'status']),
            models.Index(fields=['salary_min', 'salary_max']),
            models.Index(fields=['is_featured', 'status', 'created_at']),
            models.Index(fields=['status', 'is_featured', '-created_at']),
        ]
    
    def __str__(self):
        return self.title