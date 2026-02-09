from django.db import models
from core.models import Application
from employers.models import Job

class QuestionTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('introduction', 'Introduction'),
        ('experience', 'Experience'),
        ('skills', 'Skills'),
        ('availability', 'Availability'),
        ('salary', 'Salary'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    question_text = models.TextField()
    role = models.CharField(max_length=50, blank=True)  # Empty = all roles
    condition = models.JSONField(default=dict, blank=True)  # {"min_experience": 3}
    follow_up_trigger = models.JSONField(default=dict, blank=True)  # {"keywords": ["python"]}
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'order']
    
    def __str__(self):
        return f"{self.category} - {self.question_text[:50]}"


class QuestionFlow(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='question_flows')
    template = models.ForeignKey(QuestionTemplate, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['job', 'template', 'order']
    
    def __str__(self):
        return f"{self.job.title} - Q{self.order}"


class InterviewState(models.Model):
    session = models.OneToOneField('core.AIInterviewSession', on_delete=models.CASCADE, related_name='state')
    current_question_index = models.IntegerField(default=0)
    context = models.JSONField(default=dict)  # Store answers for branching
    completed_categories = models.JSONField(default=list)
    next_question_id = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"State - {self.session.session_id}"
