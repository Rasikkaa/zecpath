from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import CustomUser, Application
from candidates.models import Candidate
from .models import Employer, Job


class EmployerProfileTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.employer = Employer.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        response = self.client.get(reverse('employers:employer_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_profile(self):
        data = {'company_name': 'Test Company', 'company_size': '50-100'}
        response = self.client.put(reverse('employers:employer_profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employer.refresh_from_db()
        self.assertEqual(self.employer.company_name, 'Test Company')


class JobManagementTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.employer = Employer.objects.get(user=self.user)
        self.employer.verification = True
        self.employer.save()
        self.client.force_authenticate(user=self.user)
    
    def test_create_job(self):
        data = {
            'title': 'Software Engineer',
            'description': 'Looking for Python developer',
            'location': 'Remote',
            'skills': ['Python', 'Django'],
            'salary_min': 60000,
            'salary_max': 100000
        }
        response = self.client.post(reverse('employers:job_create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Job.objects.filter(title='Software Engineer').exists())
    
    def test_unverified_employer_cannot_create_job(self):
        self.employer.verification = False
        self.employer.save()
        data = {'title': 'Test Job', 'description': 'Test', 'location': 'Remote'}
        response = self.client.post(reverse('employers:job_create'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_job(self):
        job = Job.objects.create(employer=self.employer, title='Old Title', description='Test', location='Remote')
        data = {'title': 'New Title'}
        response = self.client.put(reverse('employers:job_update', kwargs={'job_id': job.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertEqual(job.title, 'New Title')
    
    def test_delete_job(self):
        job = Job.objects.create(employer=self.employer, title='Test', description='Test', location='Remote')
        response = self.client.delete(reverse('employers:job_update', kwargs={'job_id': job.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Job.objects.filter(id=job.id).exists())
    
    def test_toggle_job_status(self):
        job = Job.objects.create(employer=self.employer, title='Test', description='Test', location='Remote', status='published')
        response = self.client.patch(reverse('employers:job_toggle_status', kwargs={'job_id': job.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertEqual(job.status, 'closed')


class ATSWorkflowTests(APITestCase):
    def setUp(self):
        self.employer_user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.candidate_user = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.employer = Employer.objects.get(user=self.employer_user)
        self.candidate = Candidate.objects.get(user=self.candidate_user)
        self.job = Job.objects.create(employer=self.employer, title='Test', description='Test', location='Remote', status='published')
        self.application = Application.objects.create(candidate=self.candidate, job=self.job, status='pending')
        self.client.force_authenticate(user=self.employer_user)
    
    def test_shortlist_candidate(self):
        response = self.client.post(reverse('employers:shortlist_candidate', kwargs={'app_id': self.application.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'shortlisted')
    
    def test_reject_candidate(self):
        response = self.client.post(reverse('employers:reject_candidate', kwargs={'app_id': self.application.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'rejected')
    
    def test_invalid_status_transition(self):
        self.application.status = 'rejected'
        self.application.save()
        response = self.client.post(reverse('employers:shortlist_candidate', kwargs={'app_id': self.application.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AutomationTests(APITestCase):
    def setUp(self):
        self.employer_user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.employer = Employer.objects.get(user=self.employer_user)
        self.job = Job.objects.create(
            employer=self.employer, 
            title='Test', 
            description='Test', 
            location='Remote',
            auto_shortlist_enabled=True,
            auto_shortlist_threshold=80,
            auto_reject_threshold=30
        )
        self.client.force_authenticate(user=self.employer_user)
    
    def test_get_automation_settings(self):
        response = self.client.get(reverse('employers:automation_settings', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['auto_shortlist_enabled'])
    
    def test_update_automation_settings(self):
        data = {'auto_shortlist_threshold': 85, 'auto_reject_threshold': 25}
        response = self.client.post(reverse('employers:automation_settings', kwargs={'job_id': self.job.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.auto_shortlist_threshold, 85)
