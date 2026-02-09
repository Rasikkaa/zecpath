from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import CustomUser
from .models import Candidate, SavedJob
from employers.models import Employer, Job
import os


class CandidateProfileTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.candidate = Candidate.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        response = self.client.get(reverse('candidates:candidate_profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_info']['email'], 'candidate@test.com')
    
    def test_update_profile(self):
        data = {
            'skills': ['Python', 'Django'],
            'experience_years': 3,
            'expected_salary': 80000
        }
        response = self.client.put(reverse('candidates:candidate_profile'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.experience_years, 3)


class ResumeTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.candidate = Candidate.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)
    
    def test_upload_resume_pdf(self):
        pdf_content = b'%PDF-1.4 fake pdf content'
        resume = SimpleUploadedFile("resume.pdf", pdf_content, content_type="application/pdf")
        response = self.client.post(reverse('candidates:resume_upload'), {'resume': resume}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.candidate.refresh_from_db()
        self.assertTrue(self.candidate.resume)
    
    def test_upload_invalid_file_type(self):
        invalid_file = SimpleUploadedFile("resume.txt", b"text content", content_type="text/plain")
        response = self.client.post(reverse('candidates:resume_upload'), {'resume': invalid_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_resume(self):
        pdf_content = b'%PDF-1.4 fake pdf'
        resume = SimpleUploadedFile("resume.pdf", pdf_content, content_type="application/pdf")
        self.client.post(reverse('candidates:resume_upload'), {'resume': resume}, format='multipart')
        
        response = self.client.delete(reverse('candidates:resume_delete'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.candidate.refresh_from_db()
        self.assertFalse(self.candidate.resume)


class SavedJobsTests(APITestCase):
    def setUp(self):
        self.candidate_user = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.employer_user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer')
        self.candidate = Candidate.objects.get(user=self.candidate_user)
        self.employer = Employer.objects.get(user=self.employer_user)
        self.job = Job.objects.create(employer=self.employer, title='Test Job', description='Test', location='Remote', status='published')
        self.client.force_authenticate(user=self.candidate_user)
    
    def test_save_job(self):
        response = self.client.post(reverse('candidates:save_job', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SavedJob.objects.filter(candidate=self.candidate, job=self.job).exists())
    
    def test_unsave_job(self):
        SavedJob.objects.create(candidate=self.candidate, job=self.job)
        response = self.client.delete(reverse('candidates:save_job', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SavedJob.objects.filter(candidate=self.candidate, job=self.job).exists())
    
    def test_get_saved_jobs(self):
        SavedJob.objects.create(candidate=self.candidate, job=self.job)
        response = self.client.get(reverse('candidates:saved_jobs_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
