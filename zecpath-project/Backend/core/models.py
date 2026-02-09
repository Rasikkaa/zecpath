from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('candidate', 'Candidate'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True, blank=False, null=False)
    is_verified = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def save(self, *args, **kwargs):
        if not self.role:
            self.role = 'admin'  # Default role for superuser
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate role field"""
        from django.core.exceptions import ValidationError
        if self.role and self.role not in [choice[0] for choice in self.ROLE_CHOICES]:
            raise ValidationError({'role': 'Invalid role selected.'})
        super().clean()

    
    def __str__(self):
        return self.email

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected'),
    ]
    
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE)
    job = models.ForeignKey('employers.Job', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', db_index=True)
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resume_snapshot = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    match_score = models.IntegerField(default=0, db_index=True)
    match_breakdown = models.JSONField(default=dict, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'applied_at']),
            models.Index(fields=['candidate', 'applied_at']),
            models.Index(fields=['job', 'applied_at']),
        ]
        unique_together = ['candidate', 'job']
    
    def save(self, *args, **kwargs):
        # Track status changes
        if self.pk:
            try:
                old_instance = Application.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    self._status_changed = True
                    self._old_status = old_instance.status
            except Application.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.candidate.user.email} - {self.job.title}"

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=50, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=50, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.application} - {self.old_status} to {self.new_status}"

class AuditLog(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=100, db_index=True)
    target_model = models.CharField(max_length=50)
    target_id = models.IntegerField()
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['target_model', 'target_id']),
        ]
    
    def __str__(self):
        return f"{self.admin.email} - {self.action} - {self.timestamp}"

class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    recipient = models.EmailField(db_index=True)
    subject = models.CharField(max_length=255)
    template_name = models.CharField(max_length=100)
    context_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    retry_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['recipient', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient} - {self.subject} - {self.status}"