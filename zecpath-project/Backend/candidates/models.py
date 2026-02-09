from django.db import models
from django.contrib.auth import get_user_model
import os
from common.utils.file_validators import FileValidator, resume_upload_path

User = get_user_model()

class SavedJob(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('employers.Job', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        unique_together = ['candidate', 'job']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.candidate.user.email} - {self.job.title}"

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.JSONField(default=dict, blank=True)
    education = models.CharField(max_length=200, blank=True)
    experience = models.CharField(max_length=500, blank=True)
    expected_salary = models.IntegerField(null=True, blank=True, db_index=True)
    experience_years = models.IntegerField(default=0, db_index=True)
    is_available_for_call = models.BooleanField(default=True, db_index=True)
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileValidator()],
        blank=True,
        null=True
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['experience_years', 'expected_salary']),
        ]
    
    def save(self, *args, **kwargs):
        # Delete old resume when uploading new one
        if self.pk:
            try:
                old_resume = Candidate.objects.get(pk=self.pk).resume
                if old_resume and old_resume != self.resume:
                    if os.path.isfile(old_resume.path):
                        os.remove(old_resume.path)
            except (Candidate.DoesNotExist, OSError, ValueError):
                pass  # Continue even if old file deletion fails
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.email