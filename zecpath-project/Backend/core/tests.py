from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import CustomUser, Application, AuditLog
from candidates.models import Candidate
from employers.models import Employer, Job


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
    
    def test_signup_candidate(self):
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'role': 'candidate',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data['data'])
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())
    
    def test_signup_employer_inactive(self):
        data = {
            'email': 'employer@test.com',
            'password': 'TestPass123!',
            'role': 'employer',
            'first_name': 'Employer',
            'last_name': 'Test'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = CustomUser.objects.get(email='employer@test.com')
        self.assertFalse(user.is_active)
    
    def test_signup_duplicate_email(self):
        CustomUser.objects.create_user(email='test@example.com', password='pass', role='candidate')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'role': 'candidate',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        CustomUser.objects.create_user(email='test@example.com', password='TestPass123!', role='candidate')
        data = {'email': 'test@example.com', 'password': 'TestPass123!'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
    
    def test_login_invalid_credentials(self):
        data = {'email': 'wrong@example.com', 'password': 'wrong'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout(self):
        user = CustomUser.objects.create_user(email='test@example.com', password='pass', role='candidate')
        self.client.force_authenticate(user=user)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        response = self.client.post(self.logout_url, {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionTests(APITestCase):
    def setUp(self):
        self.candidate = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.employer = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.admin = CustomUser.objects.create_user(email='admin@test.com', password='pass', role='admin')
        Employer.objects.filter(user=self.employer).update(verification=True)
    
    def test_candidate_cannot_create_job(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.post(reverse('employers:job_create'), {'title': 'Test Job', 'description': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_employer_can_create_job(self):
        self.client.force_authenticate(user=self.employer)
        data = {
            'title': 'Software Engineer',
            'description': 'Test description',
            'location': 'Remote',
            'status': 'published'
        }
        response = self.client.post(reverse('employers:job_create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_unauthorized_access_blocked(self):
        response = self.client.get(reverse('candidates:candidate_profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_access_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobFlowTests(APITestCase):
    def setUp(self):
        self.candidate_user = CustomUser.objects.create_user(email='candidate@test.com', password='pass', role='candidate')
        self.employer_user = CustomUser.objects.create_user(email='employer@test.com', password='pass', role='employer', is_active=True)
        self.candidate = Candidate.objects.get(user=self.candidate_user)
        self.employer = Employer.objects.get(user=self.employer_user)
        self.employer.verification = True
        self.employer.save()
        
        self.job = Job.objects.create(
            employer=self.employer,
            title='Test Job',
            description='Test Description',
            location='Remote',
            status='published'
        )
    
    def test_candidate_apply_to_job(self):
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.post(reverse('job_apply', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Application.objects.filter(candidate=self.candidate, job=self.job).exists())
    
    def test_duplicate_application_blocked(self):
        Application.objects.create(candidate=self.candidate, job=self.job)
        self.client.force_authenticate(user=self.candidate_user)
        response = self.client.post(reverse('job_apply', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_employer_view_applications(self):
        Application.objects.create(candidate=self.candidate, job=self.job)
        self.client.force_authenticate(user=self.employer_user)
        response = self.client.get(reverse('employers:job_applications', kwargs={'job_id': self.job.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_employer_update_application_status(self):
        app = Application.objects.create(candidate=self.candidate, job=self.job)
        self.client.force_authenticate(user=self.employer_user)
        response = self.client.patch(
            reverse('application_status_update', kwargs={'app_id': app.id}),
            {'status': 'shortlisted'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, 'shortlisted')


class ModelTests(TestCase):
    def test_user_creation(self):
        user = CustomUser.objects.create_user(email='test@test.com', password='pass', role='candidate')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.check_password('pass'))
    
    def test_candidate_profile_auto_created(self):
        user = CustomUser.objects.create_user(email='test@test.com', password='pass', role='candidate')
        self.assertTrue(hasattr(user, 'candidate'))
    
    def test_employer_profile_auto_created(self):
        user = CustomUser.objects.create_user(email='test@test.com', password='pass', role='employer')
        self.assertTrue(hasattr(user, 'employer'))
    
    def test_application_unique_constraint(self):
        candidate_user = CustomUser.objects.create_user(email='c@test.com', password='pass', role='candidate')
        employer_user = CustomUser.objects.create_user(email='e@test.com', password='pass', role='employer')
        candidate = Candidate.objects.get(user=candidate_user)
        employer = Employer.objects.get(user=employer_user)
        job = Job.objects.create(employer=employer, title='Test', description='Test', location='Test')
        
        Application.objects.create(candidate=candidate, job=job)
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Application.objects.create(candidate=candidate, job=job)
