from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Application, ApplicationStatusHistory, AuditLog, EmailLog
from .ai_call_models import AICallQueue, AIInterviewSession, AIConversationTurn, AICallTranscript
from .question_models import QuestionTemplate, QuestionFlow, InterviewState
from .interview_models import AvailabilitySlot, InterviewSchedule
from .reminder_models import InterviewReminder

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['email']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Custom Fields', {'fields': ('role', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'status', 'applied_at']

@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at']
    readonly_fields = ['changed_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action', 'target_model', 'target_id', 'timestamp']
    list_filter = ['action', 'target_model', 'timestamp']
    search_fields = ['admin__email', 'action', 'details']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'status', 'sent_at', 'created_at', 'retry_count']
    list_filter = ['status', 'created_at', 'sent_at']
    search_fields = ['recipient', 'subject']
    readonly_fields = ['created_at', 'sent_at']
    date_hierarchy = 'created_at'

@admin.register(AICallQueue)
class AICallQueueAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'status', 'trigger_reason', 'call_outcome', 'scheduled_at', 'completed_at']
    list_filter = ['status', 'trigger_reason', 'call_outcome', 'scheduled_at']
    search_fields = ['application__candidate__user__email', 'application__job__title']
    readonly_fields = ['created_at', 'started_at', 'completed_at']

@admin.register(AIInterviewSession)
class AIInterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'call_queue', 'total_questions', 'total_answers', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['created_at']

@admin.register(AIConversationTurn)
class AIConversationTurnAdmin(admin.ModelAdmin):
    list_display = ['session', 'turn_number', 'timestamp']
    list_filter = ['timestamp']
    ordering = ['session', 'turn_number']

@admin.register(AICallTranscript)
class AICallTranscriptAdmin(admin.ModelAdmin):
    list_display = ['session', 'language', 'confidence_score', 'created_at']
    list_filter = ['language', 'created_at']
    readonly_fields = ['created_at']

@admin.register(QuestionTemplate)
class QuestionTemplateAdmin(admin.ModelAdmin):
    list_display = ['category', 'question_text', 'role', 'order', 'is_active']
    list_filter = ['category', 'is_active', 'role']
    search_fields = ['question_text', 'role']

@admin.register(QuestionFlow)
class QuestionFlowAdmin(admin.ModelAdmin):
    list_display = ['job', 'template', 'order', 'is_required']
    list_filter = ['is_required']
    search_fields = ['job__title']

@admin.register(InterviewState)
class InterviewStateAdmin(admin.ModelAdmin):
    list_display = ['session', 'current_question_index', 'completed_categories']
    readonly_fields = ['session']

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['role', 'day_of_week', 'is_active']
    search_fields = ['user__email']

@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ['application', 'interview_date', 'status', 'employer_confirmed', 'candidate_confirmed']
    list_filter = ['status', 'interview_date']
    search_fields = ['application__candidate__user__email', 'application__job__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(InterviewReminder)
class InterviewReminderAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'reminder_type', 'status', 'scheduled_at', 'sent_at', 'retry_count']
    list_filter = ['reminder_type', 'status', 'scheduled_at']
    search_fields = ['schedule__application__candidate__user__email']
    readonly_fields = ['created_at', 'sent_at']