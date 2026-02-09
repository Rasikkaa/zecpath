from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .ai_call_views import AICallQueueListAPI, AICallTriggerAPI, AICallStatsAPI, AIConversationDetailAPI
from .question_views import QuestionTemplateListAPI, JobQuestionFlowAPI, InterviewStateAPI
from .twilio_webhooks import twilio_callback, twilio_question, twilio_response, twilio_status_callback
from .answer_scoring_views import AnswerSubmitAPI, AnswerScoreAPI, SessionScoresAPI, AggregateScoreAPI
from .interview_views import (
    AvailabilitySlotAPI, InterviewScheduleAPI, AvailableSlotsAPI,
    InterviewConfirmAPI, InterviewDeclineAPI, InterviewRescheduleAPI, InterviewListAPI
)
from .report_views import CandidateReportAPI, BulkReportsAPI, JobReportsAPI

urlpatterns = [
    path('', views.home_api, name='home_api'),
    
    # Auth endpoints
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Public job listing endpoints
    path('jobs/', views.JobListAPI.as_view(), name='job_list'),
    path('jobs/featured/', views.FeaturedJobsAPI.as_view(), name='featured_jobs'),
    path('jobs/latest/', views.LatestJobsAPI.as_view(), name='latest_jobs'),
    path('jobs/<int:job_id>/apply/', views.JobApplicationAPI.as_view(), name='job_apply'),
    
    # Application tracking endpoints
    path('applications/', views.ApplicationListAPI.as_view(), name='application_list'),
    path('applications/<int:app_id>/', views.ApplicationDetailAPI.as_view(), name='application_detail'),
    path('applications/<int:app_id>/status/', views.ApplicationStatusUpdateAPI.as_view(), name='application_status_update'),
    
    # AI Call endpoints
    path('ai-calls/', AICallQueueListAPI.as_view(), name='ai_call_list'),
    path('ai-calls/trigger/<int:application_id>/', AICallTriggerAPI.as_view(), name='ai_call_trigger'),
    path('ai-calls/stats/', AICallStatsAPI.as_view(), name='ai_call_stats'),
    path('ai-calls/<int:call_id>/conversation/', AIConversationDetailAPI.as_view(), name='ai_conversation_detail'),
    
    # Twilio webhooks
    path('ai-calls/twilio-callback/', twilio_callback, name='twilio_callback'),
    path('ai-calls/twilio-question/<int:question_num>/', twilio_question, name='twilio_question'),
    path('ai-calls/twilio-response/<int:question_num>/', twilio_response, name='twilio_response'),
    path('ai-calls/twilio-status/', twilio_status_callback, name='twilio_status'),
    
    # Question Engine endpoints (Day 36)
    path('questions/templates/', QuestionTemplateListAPI.as_view(), name='question_templates'),
    path('questions/jobs/<int:job_id>/flow/', JobQuestionFlowAPI.as_view(), name='job_question_flow'),
    path('questions/state/<str:session_id>/', InterviewStateAPI.as_view(), name='interview_state'),
    
    # Answer Scoring endpoints (Day 37)
    path('answers/submit/', AnswerSubmitAPI.as_view(), name='answer_submit'),
    path('answers/<int:turn_id>/score/', AnswerScoreAPI.as_view(), name='answer_score'),
    path('sessions/<str:session_id>/scores/', SessionScoresAPI.as_view(), name='session_scores'),
    path('sessions/<str:session_id>/aggregate-score/', AggregateScoreAPI.as_view(), name='aggregate_score'),
    
    # Interview Scheduling endpoints (Day 38)
    path('availability/', AvailabilitySlotAPI.as_view(), name='availability_slots'),
    path('interviews/', InterviewListAPI.as_view(), name='interview_list'),
    path('interviews/schedule/<int:application_id>/', InterviewScheduleAPI.as_view(), name='interview_schedule'),
    path('interviews/<int:application_id>/available-slots/', AvailableSlotsAPI.as_view(), name='available_slots'),
    path('interviews/<int:schedule_id>/confirm/', InterviewConfirmAPI.as_view(), name='interview_confirm'),
    path('interviews/<int:schedule_id>/decline/', InterviewDeclineAPI.as_view(), name='interview_decline'),
    path('interviews/<int:schedule_id>/reschedule/', InterviewRescheduleAPI.as_view(), name='interview_reschedule'),
    
    # Candidate Report endpoints (Day 40)
    path('reports/candidate/<int:application_id>/', CandidateReportAPI.as_view(), name='candidate_report'),
    path('reports/bulk/', BulkReportsAPI.as_view(), name='bulk_reports'),
    path('reports/job/<int:job_id>/', JobReportsAPI.as_view(), name='job_reports'),
    
    # Admin endpoints
    path('admin/dashboard/', views.AdminDashboardAPI.as_view(), name='admin_dashboard'),
    path('admin/employers/pending/', views.PendingEmployersAPI.as_view(), name='pending_employers'),
    path('admin/employers/<int:employer_id>/approve/', views.ApproveEmployerAPI.as_view(), name='approve_employer'),
    path('admin/users/<int:user_id>/block/', views.BlockUserAPI.as_view(), name='block_user'),
    path('admin/jobs/<int:job_id>/delete/', views.AdminDeleteJobAPI.as_view(), name='admin_delete_job'),
    path('admin/jobs/<int:job_id>/flag/', views.FlagJobAPI.as_view(), name='flag_job'),
    path('admin/analytics/', views.PlatformAnalyticsAPI.as_view(), name='platform_analytics'),
    path('admin/audit-logs/', views.AuditLogsAPI.as_view(), name='audit_logs'),
    path('admin/email-logs/', views.EmailLogsAPI.as_view(), name='email_logs'),
    path('admin/jobs/<int:job_id>/ranked-candidates/', views.RankedCandidatesAPI.as_view(), name='admin_ranked_candidates'),
    path('profile/', views.UserTestAPI.as_view(), name='user_profile'),
    
    # Include app-specific URLs
    path('candidates/', include('candidates.urls')),
    path('employers/', include('employers.urls')),
]