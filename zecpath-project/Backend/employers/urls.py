from django.urls import path
from . import views
from .automation_views import JobAutomationSettingsAPI, JobAutomationRunAPI, JobAutomationPreviewAPI
from core.views import RankedCandidatesAPI

app_name = 'employers'

urlpatterns = [
    # Employer profile endpoints
    path('profile/', views.EmployerProfileAPI.as_view(), name='employer_profile'),
    path('dashboard/', views.EmployerDashboardAPI.as_view(), name='employer_dashboard'),
    
    # Job management endpoints
    path('jobs/', views.EmployerJobsAPI.as_view(), name='employer_jobs'),
    path('jobs/create/', views.JobCreateAPI.as_view(), name='job_create'),
    path('jobs/<int:job_id>/update/', views.JobUpdateAPI.as_view(), name='job_update'),
    path('jobs/<int:job_id>/toggle-status/', views.JobToggleStatusAPI.as_view(), name='job_toggle_status'),
    path('jobs/<int:job_id>/activate/', views.JobActivateAPI.as_view(), name='job_activate'),
    path('jobs/<int:job_id>/deactivate/', views.JobDeactivateAPI.as_view(), name='job_deactivate'),
    
    # Application management endpoints
    path('jobs/<int:job_id>/applications/', views.JobApplicationsAPI.as_view(), name='job_applications'),
    path('jobs/<int:job_id>/ranked-candidates/', RankedCandidatesAPI.as_view(), name='ranked_candidates'),
    path('applications/<int:app_id>/shortlist/', views.ShortlistCandidateAPI.as_view(), name='shortlist_candidate'),
    path('applications/<int:app_id>/reject/', views.RejectCandidateAPI.as_view(), name='reject_candidate'),
    
    # Automation endpoints
    path('jobs/<int:job_id>/automation/settings/', JobAutomationSettingsAPI.as_view(), name='automation_settings'),
    path('jobs/<int:job_id>/automation/run/', JobAutomationRunAPI.as_view(), name='automation_run'),
    path('jobs/<int:job_id>/automation/preview/', JobAutomationPreviewAPI.as_view(), name='automation_preview'),
]