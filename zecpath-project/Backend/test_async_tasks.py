"""
Test script to trigger async tasks for screenshot demonstration
Run this while Celery worker is running to see task execution logs
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from common.tasks import send_email_task, cleanup_old_logs

print("=" * 60)
print("Testing Async Tasks - Day 32")
print("=" * 60)

# Test 1: Send Email Task
print("\n1. Triggering send_email_task...")
result1 = send_email_task.delay(
    subject="Test Async Email",
    message="This is a test email sent via Celery async task",
    recipient_list=["test@example.com"]
)
print(f"   Task ID: {result1.id}")
print(f"   Status: {result1.status}")

# Test 2: Cleanup Old Logs Task
print("\n2. Triggering cleanup_old_logs...")
result2 = cleanup_old_logs.delay()
print(f"   Task ID: {result2.id}")
print(f"   Status: {result2.status}")

print("\n" + "=" * 60)
print("Tasks submitted to Celery queue!")
print("Check Celery worker terminal for execution logs")
print("=" * 60)
