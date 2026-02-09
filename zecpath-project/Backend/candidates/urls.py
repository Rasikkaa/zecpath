from django.urls import path
from . import views
from .dashboard_views import (
    CandidateDashboardAPI,
    JobRecommendationsAPI,
    SavedJobsAPI,
    SaveJobAPI,
    InterviewStatusAPI,
    ApplicationTimelineAPI
)

app_name = 'candidates'

urlpatterns = [
    # Candidate profile endpoints
    path('profile/', views.CandidateProfileAPI.as_view(), name='candidate_profile'),
    
    # Resume endpoints
    path('resume/upload/', views.ResumeUploadAPI.as_view(), name='resume_upload'),
    path('resume/delete/', views.ResumeDeleteAPI.as_view(), name='resume_delete'),
    path('resume/download/', views.ResumeDownloadAPI.as_view(), name='resume_download'),
    path('resume/download/<int:candidate_id>/', views.ResumeDownloadAPI.as_view(), name='resume_download_by_id'),
    path('resume/parse/', views.ResumeParseAPI.as_view(), name='resume_parse'),
    
    # Dashboard endpoints
    path('dashboard/', CandidateDashboardAPI.as_view(), name='candidate_dashboard'),
    path('recommendations/', JobRecommendationsAPI.as_view(), name='job_recommendations'),
    path('saved-jobs/', SavedJobsAPI.as_view(), name='saved_jobs_list'),
    path('saved-jobs/<int:job_id>/', SaveJobAPI.as_view(), name='save_job'),
    path('interviews/', InterviewStatusAPI.as_view(), name='interview_status'),
    path('applications/<int:app_id>/timeline/', ApplicationTimelineAPI.as_view(), name='application_timeline'),
]