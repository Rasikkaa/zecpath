from django.db import models
from core.models import Application, CustomUser

class AICallQueue(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    TRIGGER_CHOICES = [
        ('auto', 'Automatic'),
        ('manual', 'Manual'),
    ]
    
    OUTCOME_CHOICES = [
        ('pending', 'Pending'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('callback_requested', 'Callback Requested'),
        ('no_response', 'No Response'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='ai_calls')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued', db_index=True)
    scheduled_at = models.DateTimeField(db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    error_message = models.TextField(blank=True)
    call_duration = models.IntegerField(null=True, blank=True)
    
    # Day 34: Audit & Outcome
    triggered_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    trigger_reason = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='auto')
    call_outcome = models.CharField(max_length=30, choices=OUTCOME_CHOICES, default='pending')
    conversation_summary = models.TextField(blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"AI Call - {self.application} - {self.status}"


class AIInterviewSession(models.Model):
    call_queue = models.OneToOneField(AICallQueue, on_delete=models.CASCADE, related_name='session')
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    transcript_json = models.JSONField(default=dict, blank=True)
    full_transcript_text = models.TextField(blank=True)
    total_questions = models.IntegerField(default=0)
    total_answers = models.IntegerField(default=0)
    overall_score = models.FloatField(null=True, blank=True)  # Day 37
    category_scores = models.JSONField(default=dict, blank=True)  # Day 37
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session {self.session_id}"


class AIConversationTurn(models.Model):
    session = models.ForeignKey(AIInterviewSession, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField()
    question_text = models.TextField()
    answer_text = models.TextField(blank=True)
    category = models.CharField(max_length=20, blank=True)  # Day 36
    follow_up_triggered = models.BooleanField(default=False)  # Day 36
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    # Day 37: Answer Scoring
    answer_score = models.FloatField(null=True, blank=True)
    relevance_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)
    keyword_matches = models.JSONField(default=dict, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    ai_annotations = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['turn_number']
        unique_together = ['session', 'turn_number']
    
    def __str__(self):
        return f"Turn {self.turn_number} - {self.session.session_id}"


class AICallTranscript(models.Model):
    session = models.OneToOneField(AIInterviewSession, on_delete=models.CASCADE, related_name='transcript')
    raw_audio_url = models.URLField(blank=True)
    transcript_text = models.TextField()
    transcript_json = models.JSONField(default=dict)
    language = models.CharField(max_length=10, default='en')
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transcript - {self.session.session_id}"
