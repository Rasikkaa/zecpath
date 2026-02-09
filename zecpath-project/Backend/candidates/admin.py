from django.contrib import admin
from .models import Candidate, SavedJob

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_years', 'expected_salary']
    list_filter = ['experience_years', 'expected_salary']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['candidate__user__email', 'job__title']