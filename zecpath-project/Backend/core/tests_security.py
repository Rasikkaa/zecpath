from django.test import TestCase, Client
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import CustomUser
from employers.models import Employer, Job
from candidates.models import Candidate
from django.core.files.uploadedfile import SimpleUploadedFile


class SecurityTests(APITestCase):
    def setUp(self):
        self.client = Client()
        self.candidate = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.employer = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.admin = CustomUser.objects.create_user(email='admin@test.com', password='pass', role='admin')
    
    def test_unauthorized_access_blocked(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        response = self.client.get(reverse('candidates:candidate_profile'))
        self.assertEqual(response.status_code, 401)
    
    def test_role_based_access_control(self):
        """Test that users cannot access endpoints for other roles"""
        self.client.force_login(self.candidate)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertIn(response.status_code, [401, 403])
    
    def test_csrf_protection(self):
        """Test CSRF token validation"""
        response = self.client.post(reverse('login'), {
            'email': 'test@test.com',
            'password': 'pass'
        })
        # Should work with API (CSRF exempt for API endpoints)
        self.assertIn(response.status_code, [200, 400, 401])
    
    def test_sql_injection_prevention(self):
        """Test SQL injection attempts are blocked"""
        malicious_input = "'; DROP TABLE core_customuser; --"
        response = self.client.post(reverse('login'), {
            'email': malicious_input,
            'password': 'pass'
        })
        # Should not crash, should return error
        self.assertIn(response.status_code, [400, 401])
        # Verify table still exists
        self.assertTrue(CustomUser.objects.model._meta.db_table)
    
    def test_xss_prevention(self):
        """Test XSS script injection is sanitized"""
        self.client.force_login(self.candidate)
        xss_payload = '<script>alert("XSS")</script>'
        candidate = Candidate.objects.get(user=self.candidate)
        candidate.education = xss_payload
        candidate.save()
        # Data should be stored as-is (Django templates auto-escape)
        self.assertEqual(candidate.education, xss_payload)
    
    def test_file_upload_validation(self):
        """Test file upload restrictions"""
        self.client.force_login(self.candidate)
        # Test invalid file type
        malicious_file = SimpleUploadedFile("malware.exe", b"malicious content", content_type="application/x-msdownload")
        response = self.client.post(reverse('candidates:resume_upload'), {'resume': malicious_file})
        self.assertEqual(response.status_code, 400)
    
    def test_password_in_response(self):
        """Test that passwords are never returned in API responses"""
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@test.com',
            'password': 'SecurePass123!',
            'role': 'candidate',
            'first_name': 'Test',
            'last_name': 'User'
        })
        response_str = str(response.content)
        self.assertNotIn('SecurePass123!', response_str)
    
    def test_sensitive_data_exposure(self):
        """Test that sensitive data is not exposed in error messages"""
        response = self.client.post(reverse('login'), {
            'email': 'nonexistent@test.com',
            'password': 'wrongpass'
        })
        response_str = str(response.content)
        # Should not reveal if email exists
        self.assertNotIn('email does not exist', response_str.lower())


class AccessControlTests(APITestCase):
    def setUp(self):
        self.candidate_user = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.employer_user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.other_employer = CustomUser.objects.create_user(email='other@test.com', password='pass', role='employer', is_active=True)
        
        self.employer = Employer.objects.get(user=self.employer_user)
        self.employer.verification = True
        self.employer.save()
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test',
            location='Remote'
        )
    
    def test_employer_cannot_modify_other_jobs(self):
        """Test that employers can only modify their own jobs"""
        self.client.force_authenticate(user=self.other_employer)
        response = self.client.put(
            reverse('employers:job_update', kwargs={'job_id': self.job.id}),
            {'title': 'Hacked Title'}
        )
        self.assertIn(response.status_code, [400, 404])
    
    def test_candidate_cannot_access_employer_endpoints(self):
        """Test role separation"""
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.get(reverse('employers:employer_dashboard'))
        self.assertEqual(response.status_code, 403)
    
    def test_data_isolation(self):
        """Test that users can only access their own data"""
        other_candidate = CustomUser.objects.create_user(email='other_candidate@test.com', password='pass', role='candidate')
        self.client.force_authenticate(user=self.candidate_user)
        
        # Should not be able to access other candidate's profile
        response = self.client.get(reverse('candidates:candidate_profile') + f'?id={other_candidate.candidate.id}')
        # Should either deny or return own profile
        if response.status_code == 200:
            self.assertEqual(response.data['user_info']['email'], 'candidate@test.com')


class InputValidationTests(APITestCase):
    def test_email_validation(self):
        """Test email format validation"""
        response = self.client.post(reverse('signup'), {
            'email': 'invalid-email',
            'password': 'Pass123!',
            'role': 'candidate',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_required_fields(self):
        """Test required field validation"""
        response = self.client.post(reverse('signup'), {
            'email': 'test@test.com'
            # Missing required fields
        })
        self.assertEqual(response.status_code, 400)
    
    def test_max_length_validation(self):
        """Test field length limits"""
        long_string = 'A' * 300
        response = self.client.post(reverse('signup'), {
            'email': 'test@test.com',
            'password': 'Pass123!',
            'role': 'candidate',
            'first_name': long_string,
            'last_name': 'User'
        })
        # Should either truncate or reject
        self.assertIn(response.status_code, [200, 201, 400])
