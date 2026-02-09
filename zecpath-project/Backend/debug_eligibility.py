"""
Quick debug script
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from core.models import Application
from common.services.ai_call_eligibility import AICallEligibility

app = Application.objects.first()
print(f"Application ID: {app.id}")
print(f"Status: {app.status}")
print(f"Match Score: {app.match_score}")
print(f"Job Status: {app.job.status}")

is_eligible, checks = AICallEligibility.is_eligible(app)
print(f"\nEligibility: {is_eligible}")
print(f"Checks: {checks}")

# Fix if needed
if app.status == 'interview_scheduled':
    print("\n✅ Status is interview_scheduled - should be eligible")
    print(f"Status check result: {app.status in ['shortlisted', 'interview_scheduled']}")
