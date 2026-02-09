from django.contrib import admin
from .models import Employer, Job

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'domain', 'verification', 'website']
    list_filter = ['verification', 'company_size']
    search_fields = ['company_name', 'user__email', 'domain']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'employer', 'location', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'job_type', 'is_featured', 'created_at']
    search_fields = ['title', 'employer__company_name', 'location']