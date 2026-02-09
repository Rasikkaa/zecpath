# ZecPath - Complete Project Documentation

## Project Overview
ZecPath is a comprehensive Job Portal Platform with AI-powered interview capabilities, ATS (Applicant Tracking System), and automated candidate screening.

---

## Technologies Used

### Backend
- **Framework**: Django 6.0.1
- **API**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt 5.3.0)
- **Database**: PostgreSQL
- **Task Queue**: Celery 5.3.4
- **Message Broker**: Redis 5.0.1
- **AI/ML**: OpenAI API (GPT-3.5-turbo)
- **Voice Calls**: Twilio 8.10.0
- **File Processing**: PyPDF2, pdfplumber, python-docx
- **Testing**: pytest 7.4.3, pytest-django 4.7.0
- **Load Testing**: Locust 2.15.1

### Additional Libraries
- django-cors-headers 4.3.1
- python-dotenv 1.0.0
- Pillow 10.4.0
- requests 2.31.0

---

## Project Structure

```
ZecPath/
├── Backend/
│   ├── Backend/                    # Main project settings
│   │   ├── settings.py            # Django settings
│   │   ├── urls.py                # Root URL configuration
│   │   ├── celery.py              # Celery configuration
│   │   ├── wsgi.py                # WSGI application
│   │   └── asgi.py                # ASGI application
│   │
│   ├── core/                       # Core application
│   │   ├── models.py              # User, Application, AuditLog models
│   │   ├── views.py               # Main API views
│   │   ├── serializers.py         # DRF serializers
│   │   ├── permissions.py         # Custom permissions
│   │   ├── urls.py                # Core URL routing
│   │   ├── signals.py             # Django signals
│   │   ├── middleware.py          # Custom middleware
│   │   ├── exceptions.py          # Custom exception handlers
│   │   ├── ai_call_models.py      # AI interview models
│   │   ├── ai_call_views.py       # AI call API views
│   │   ├── question_models.py     # Question engine models
│   │   ├── question_views.py      # Question API views
│   │   ├── interview_models.py    # Interview scheduling models
│   │   ├── interview_views.py     # Interview API views
│   │   ├── reminder_models.py     # Reminder models
│   │   ├── answer_scoring_views.py # Answer evaluation APIs
│   │   ├── report_views.py        # Candidate report APIs
│   │   └── twilio_webhooks.py     # Twilio webhook handlers
│   │
│   ├── candidates/                 # Candidate application
│   │   ├── models.py              # Candidate, SavedJob models
│   │   ├── views.py               # Candidate API views
│   │   ├── serializers.py         # Candidate serializers
│   │   ├── services.py            # Business logic
│   │   ├── dashboard_views.py     # Dashboard APIs
│   │   └── urls.py                # Candidate URL routing
│   │
│   ├── employers/                  # Employer application
│   │   ├── models.py              # Employer, Job models
│   │   ├── views.py               # Employer API views
│   │   ├── serializers.py         # Employer serializers
│   │   ├── services.py            # Business logic
│   │   ├── automation_views.py    # ATS automation APIs
│   │   └── urls.py                # Employer URL routing
│   │
│   ├── common/                     # Shared utilities
│   │   ├── tasks.py               # Celery tasks
│   │   ├── tasks_ai_calls.py      # AI call tasks
│   │   ├── tasks_reminders.py     # Reminder tasks
│   │   ├── services/              # Business services
│   │   │   ├── email_service.py
│   │   │   ├── file_service.py
│   │   │   ├── resume_parser.py
│   │   │   ├── resume_analyzer.py
│   │   │   ├── ats_scoring.py
│   │   │   ├── automation_service.py
│   │   │   ├── ai_call_eligibility.py
│   │   │   ├── ai_conversation_service.py
│   │   │   ├── question_engine_service.py
│   │   │   ├── voice_call_service.py
│   │   │   ├── answer_evaluator.py
│   │   │   ├── interview_scorer.py
│   │   │   ├── interview_scheduler.py
│   │   │   ├── reminder_service.py
│   │   │   └── report_generator.py
│   │   ├── utils/                 # Utility functions
│   │   │   ├── pagination.py
│   │   │   ├── filters.py
│   │   │   ├── search.py
│   │   │   ├── cache.py
│   │   │   ├── file_validators.py
│   │   │   └── ats_rules.py
│   │   └── middleware/            # Custom middleware
│   │       ├── security.py
│   │       └── performance.py
│   │
│   ├── media/                      # Uploaded files
│   ├── static/                     # Static files
│   ├── logs/                       # Application logs
│   ├── manage.py                   # Django management
│   ├── requirements.txt            # Python dependencies
│   ├── pytest.ini                  # Pytest configuration
│   └── .env                        # Environment variables
│
└── postman/                        # API testing
    ├── ZecPath_API_Collection.json
    └── ZecPath_Environment.json
```

---

## Database Models

### Core Models
1. **CustomUser** - User authentication (Admin, Employer, Candidate)
2. **Application** - Job applications with ATS status
3. **ApplicationStatusHistory** - Application status tracking
4. **AuditLog** - Admin action logging
5. **EmailLog** - Email delivery tracking

### AI Interview Models
6. **AICallQueue** - AI interview call scheduling
7. **AIInterviewSession** - Interview session data
8. **AIConversationTurn** - Q&A turns with scoring
9. **AICallTranscript** - Call transcripts
10. **QuestionTemplate** - Interview question templates
11. **QuestionFlow** - Job-specific question flows
12. **InterviewState** - Dynamic interview state

### Interview Scheduling Models
13. **AvailabilitySlot** - User availability
14. **InterviewSchedule** - Interview appointments
15. **InterviewReminder** - Automated reminders

### Candidate Models
16. **Candidate** - Candidate profile
17. **SavedJob** - Saved job listings

### Employer Models
18. **Employer** - Employer profile
19. **Job** - Job postings with automation settings

---

## Complete API Endpoints

### Base URL
```
http://localhost:8000/api/
```

---

## 1. Authentication APIs

### 1.1 Home API
```
GET /
```
**Access**: Public
**Response**: API status message

### 1.2 Signup
```
POST /auth/signup/
```
**Access**: Public
**Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "candidate|employer|admin",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Response**: User data + JWT tokens

### 1.3 Login
```
POST /auth/login/
```
**Access**: Public
**Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response**: User data + JWT tokens

### 1.4 Logout
```
POST /auth/logout/
```
**Access**: Authenticated
**Body**:
```json
{
  "refresh": "refresh_token_here"
}
```

### 1.5 Refresh Token
```
POST /auth/refresh/
```
**Access**: Public
**Body**:
```json
{
  "refresh": "refresh_token_here"
}
```

---

## 2. Job Listing APIs (Public)

### 2.1 Get All Jobs
```
GET /jobs/
```
**Access**: Public
**Query Params**:
- `page` - Page number
- `page_size` - Items per page
- `skills` - Comma-separated skills
- `location` - Location filter
- `salary_min` - Minimum salary
- `salary_max` - Maximum salary
- `job_type` - full_time|part_time|contract|internship
- `is_featured` - true|false
- `search` - Search query

### 2.2 Featured Jobs
```
GET /jobs/featured/
```
**Access**: Public

### 2.3 Latest Jobs
```
GET /jobs/latest/
```
**Access**: Public
**Query Params**: `limit` (default: 10)

### 2.4 Apply to Job
```
POST /jobs/{job_id}/apply/
```
**Access**: Candidate only
**Body**: Optional resume file
**Response**: Application with ATS match score

---

## 3. Candidate APIs

### 3.1 Candidate Profile
```
GET /candidates/profile/
PUT /candidates/profile/
PATCH /candidates/profile/
DELETE /candidates/profile/
```
**Access**: Candidate or Admin
**Body** (PUT/PATCH):
```json
{
  "skills": ["Python", "Django"],
  "education": "Bachelor's in CS",
  "experience": "3 years",
  "expected_salary": 80000,
  "experience_years": 3
}
```

### 3.2 Resume Upload
```
POST /candidates/resume/upload/
```
**Access**: Candidate
**Body**: multipart/form-data with `resume` file

### 3.3 Resume Delete
```
DELETE /candidates/resume/delete/
```
**Access**: Candidate

### 3.4 Resume Download
```
GET /candidates/resume/download/
GET /candidates/resume/download/{candidate_id}/
```
**Access**: Candidate (own), Employer, Admin

### 3.5 Resume Parse
```
POST /candidates/resume/parse/
```
**Access**: Candidate
**Response**: Structured resume data with NLP analysis

### 3.6 Candidate Dashboard
```
GET /candidates/dashboard/
```
**Access**: Candidate
**Response**: Application statistics

### 3.7 Job Recommendations
```
GET /candidates/recommendations/
```
**Access**: Candidate
**Response**: AI-matched job recommendations

### 3.8 Saved Jobs
```
GET /candidates/saved-jobs/
POST /candidates/saved-jobs/{job_id}/
DELETE /candidates/saved-jobs/{job_id}/
```
**Access**: Candidate

### 3.9 Interview Status
```
GET /candidates/interviews/
```
**Access**: Candidate
**Response**: Scheduled interviews

### 3.10 Application Timeline
```
GET /candidates/applications/{app_id}/timeline/
```
**Access**: Candidate
**Response**: Status change history

---

## 4. Employer APIs

### 4.1 Employer Profile
```
GET /employers/profile/
PUT /employers/profile/
PATCH /employers/profile/
DELETE /employers/profile/
```
**Access**: Employer or Admin
**Body** (PUT/PATCH):
```json
{
  "company_name": "Tech Corp",
  "website": "https://techcorp.com",
  "company_description": "Leading tech company",
  "company_size": "50-100"
}
```

### 4.2 Employer Dashboard
```
GET /employers/dashboard/
```
**Access**: Employer
**Response**: Analytics and metrics

### 4.3 Employer Jobs
```
GET /employers/jobs/
```
**Access**: Employer
**Response**: All jobs posted by employer

### 4.4 Create Job
```
POST /employers/jobs/create/
```
**Access**: Employer (verified)
**Body**:
```json
{
  "title": "Software Engineer",
  "description": "Job description",
  "skills": ["Python", "Django"],
  "experience": "3-5 years",
  "salary_min": 60000,
  "salary_max": 100000,
  "location": "Remote",
  "job_type": "full_time",
  "status": "published"
}
```

### 4.5 Update Job
```
PUT /employers/jobs/{job_id}/update/
PATCH /employers/jobs/{job_id}/update/
DELETE /employers/jobs/{job_id}/update/
```
**Access**: Employer (owner)

### 4.6 Toggle Job Status
```
PATCH /employers/jobs/{job_id}/toggle-status/
```
**Access**: Employer
**Response**: Toggles between published/closed

### 4.7 Activate Job
```
POST /employers/jobs/{job_id}/activate/
```
**Access**: Employer

### 4.8 Deactivate Job
```
POST /employers/jobs/{job_id}/deactivate/
```
**Access**: Employer

### 4.9 Job Applications
```
GET /employers/jobs/{job_id}/applications/
```
**Access**: Employer or Admin
**Query Params**:
- `status` - Filter by application status
- `search` - Search candidates

### 4.10 Ranked Candidates
```
GET /employers/jobs/{job_id}/ranked-candidates/
```
**Access**: Employer or Admin
**Query Params**:
- `min_score` - Minimum ATS score
- `status` - Filter by status
**Response**: Applications sorted by match score

### 4.11 Shortlist Candidate
```
POST /employers/applications/{app_id}/shortlist/
```
**Access**: Employer or Admin

### 4.12 Reject Candidate
```
POST /employers/applications/{app_id}/reject/
```
**Access**: Employer or Admin

---

## 5. ATS Automation APIs

### 5.1 Get Automation Settings
```
GET /employers/jobs/{job_id}/automation/settings/
```
**Access**: Employer or Admin

### 5.2 Update Automation Settings
```
POST /employers/jobs/{job_id}/automation/settings/
```
**Access**: Employer or Admin
**Body**:
```json
{
  "auto_shortlist_enabled": true,
  "auto_shortlist_threshold": 80,
  "auto_reject_threshold": 30
}
```

### 5.3 Run Automation
```
POST /employers/jobs/{job_id}/automation/run/
```
**Access**: Employer or Admin
**Response**: Automation results

### 5.4 Preview Automation
```
GET /employers/jobs/{job_id}/automation/preview/
```
**Access**: Employer or Admin
**Response**: Preview of actions without executing

---

## 6. Application Management APIs

### 6.1 List Applications
```
GET /applications/
```
**Access**: Authenticated
**Query Params**:
- `status` - Filter by status
- `search` - Search query
**Response**: Applications based on user role

### 6.2 Application Detail
```
GET /applications/{app_id}/
```
**Access**: Candidate (own), Employer (job owner), Admin

### 6.3 Update Application Status
```
PATCH /applications/{app_id}/status/
```
**Access**: Employer or Admin
**Body**:
```json
{
  "status": "pending|shortlisted|interview_scheduled|reviewed|accepted|rejected|selected"
}
```

---

## 7. AI Interview Call APIs

### 7.1 AI Call Queue List
```
GET /ai-calls/
```
**Access**: Employer or Admin
**Query Params**: `status` - Filter by call status
**Response**: List of scheduled/completed AI calls

### 7.2 Trigger AI Call
```
POST /ai-calls/trigger/{application_id}/
```
**Access**: Employer or Admin
**Response**: Call scheduled confirmation

### 7.3 AI Call Statistics
```
GET /ai-calls/stats/
```
**Access**: Employer or Admin
**Response**: Call metrics and statistics

### 7.4 Conversation Detail
```
GET /ai-calls/{call_id}/conversation/
```
**Access**: Employer or Admin
**Response**: Full conversation transcript with scores

---

## 8. Question Engine APIs

### 8.1 Question Templates
```
GET /questions/templates/
POST /questions/templates/
```
**Access**: Employer or Admin
**Query Params**: `category` - Filter by category
**Body** (POST):
```json
{
  "category": "introduction|experience|skills|availability|salary",
  "question_text": "Tell me about yourself",
  "role": "Software Engineer",
  "order": 1
}
```

### 8.2 Job Question Flow
```
GET /questions/jobs/{job_id}/flow/
POST /questions/jobs/{job_id}/flow/
```
**Access**: Employer or Admin
**Body** (POST):
```json
{
  "template_ids": [1, 2, 3, 4]
}
```

### 8.3 Interview State
```
GET /questions/state/{session_id}/
```
**Access**: Employer or Admin
**Response**: Current interview state

---

## 9. Answer Scoring APIs

### 9.1 Submit Answer
```
POST /answers/submit/
```
**Access**: Employer or Admin
**Body**:
```json
{
  "turn_id": 1,
  "answer": "Answer text"
}
```
**Response**: Answer evaluation scores

### 9.2 Get Answer Score
```
GET /answers/{turn_id}/score/
```
**Access**: Employer or Admin
**Response**: Individual answer scores

### 9.3 Session Scores
```
GET /sessions/{session_id}/scores/
```
**Access**: Employer or Admin
**Response**: All scores for interview session

### 9.4 Aggregate Score
```
GET /sessions/{session_id}/aggregate-score/
POST /sessions/{session_id}/aggregate-score/
```
**Access**: Employer or Admin
**Response**: Overall interview score

---

## 10. Interview Scheduling APIs

### 10.1 Availability Slots
```
GET /availability/
POST /availability/
```
**Access**: Employer or Candidate
**Body** (POST):
```json
{
  "slots": [
    {
      "day_of_week": 1,
      "start_time": "09:00",
      "end_time": "17:00"
    }
  ]
}
```

### 10.2 Schedule Interview
```
POST /interviews/schedule/{application_id}/
```
**Access**: Employer or Admin
**Body**:
```json
{
  "interview_date": "2024-02-15T10:00:00Z",
  "auto_schedule": false
}
```

### 10.3 Available Slots
```
GET /interviews/{application_id}/available-slots/
```
**Access**: Employer or Admin
**Query Params**:
- `days` - Days ahead (default: 7)
- `max_slots` - Maximum slots (default: 10)

### 10.4 Confirm Interview
```
POST /interviews/{schedule_id}/confirm/
```
**Access**: Employer or Candidate

### 10.5 Decline Interview
```
POST /interviews/{schedule_id}/decline/
```
**Access**: Employer or Candidate

### 10.6 Reschedule Interview
```
POST /interviews/{schedule_id}/reschedule/
```
**Access**: Employer or Candidate
**Body**:
```json
{
  "new_date": "2024-02-16T14:00:00Z"
}
```

### 10.7 List Interviews
```
GET /interviews/
```
**Access**: Employer, Candidate, or Admin
**Query Params**: `status` - Filter by status

---

## 11. Candidate Report APIs

### 11.1 Generate Candidate Report
```
GET /reports/candidate/{application_id}/
```
**Access**: Employer or Admin
**Response**: Comprehensive candidate evaluation report

### 11.2 Bulk Reports
```
POST /reports/bulk/
```
**Access**: Employer or Admin
**Body**:
```json
{
  "application_ids": [1, 2, 3]
}
```

### 11.3 Job Reports
```
GET /reports/job/{job_id}/
```
**Access**: Employer or Admin
**Query Params**: `status` - Filter by status
**Response**: Reports for all candidates of a job

---

## 12. Admin Control Panel APIs

### 12.1 Admin Dashboard
```
GET /admin/dashboard/
```
**Access**: Admin
**Response**: Platform statistics

### 12.2 Pending Employers
```
GET /admin/employers/pending/
```
**Access**: Admin
**Response**: Unverified employers

### 12.3 Approve Employer
```
POST /admin/employers/{employer_id}/approve/
```
**Access**: Admin

### 12.4 Block/Unblock User
```
POST /admin/users/{user_id}/block/
```
**Access**: Admin
**Body**:
```json
{
  "action": "block|unblock"
}
```

### 12.5 Delete Job (Admin)
```
DELETE /admin/jobs/{job_id}/delete/
```
**Access**: Admin

### 12.6 Flag/Unflag Job
```
POST /admin/jobs/{job_id}/flag/
```
**Access**: Admin
**Body**:
```json
{
  "action": "flag|unflag"
}
```

### 12.7 Platform Analytics
```
GET /admin/analytics/
```
**Access**: Admin
**Query Params**: `days` - Time period (default: 30)
**Response**: Comprehensive platform analytics

### 12.8 Audit Logs
```
GET /admin/audit-logs/
```
**Access**: Admin
**Response**: Admin action history

### 12.9 Email Logs
```
GET /admin/email-logs/
```
**Access**: Admin
**Response**: Email delivery logs

### 12.10 Ranked Candidates (Admin)
```
GET /admin/jobs/{job_id}/ranked-candidates/
```
**Access**: Admin
**Response**: All candidates ranked by ATS score

---

## 13. Twilio Webhook APIs

### 13.1 Twilio Callback
```
POST /ai-calls/twilio-callback/
```
**Access**: Public (Twilio)
**Purpose**: Call initiation

### 13.2 Twilio Question
```
POST /ai-calls/twilio-question/{question_num}/
```
**Access**: Public (Twilio)
**Purpose**: Ask interview question

### 13.3 Twilio Response
```
POST /ai-calls/twilio-response/{question_num}/
```
**Access**: Public (Twilio)
**Purpose**: Process candidate response

### 13.4 Twilio Status Callback
```
POST /ai-calls/twilio-status/
```
**Access**: Public (Twilio)
**Purpose**: Call status updates

---

## Key Features

### 1. Role-Based Access Control (RBAC)
- **Admin**: Full platform control
- **Employer**: Job management, candidate screening
- **Candidate**: Job search, application tracking

### 2. ATS (Applicant Tracking System)
- Automated candidate scoring
- Skills matching algorithm
- Experience evaluation
- Salary compatibility check
- Auto-shortlist/reject based on thresholds

### 3. AI-Powered Interviews
- Automated voice calls via Twilio
- Dynamic question flow
- Real-time answer evaluation
- Sentiment analysis
- Conversation transcripts

### 4. Interview Scheduling
- Availability management
- Auto-scheduling algorithm
- Confirmation workflow
- Automated reminders (24h, 2h, 30min)
- Reschedule support

### 5. Resume Processing
- PDF/DOCX parsing
- NLP-based analysis
- Skill extraction
- Experience calculation
- Resume scoring

### 6. Email Automation
- Application notifications
- Status change alerts
- Interview reminders
- Rejection/acceptance emails

### 7. Performance Optimization
- Database indexing
- Query optimization
- Caching (Redis)
- Pagination
- Infinite scroll support

### 8. Security Features
- JWT authentication
- Password validation
- CSRF protection
- XSS prevention
- SQL injection protection
- Rate limiting
- Audit logging

---

## Environment Variables (.env)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=zecpath_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Redis
REDIS_URL=redis://localhost:6379/0

# AI/Voice APIs
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-3.5-turbo
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Application
BASE_URL=http://localhost:8000
AI_API_RATE_LIMIT=60
VOICE_API_RATE_LIMIT=10
```

---

## Running the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Run Celery Worker
```bash
celery -A Backend worker -l info
```

### 6. Run Celery Beat (Scheduler)
```bash
celery -A Backend beat -l info
```

### 7. Run Tests
```bash
pytest
# or
python manage.py test
```

---

## Celery Tasks

### Async Tasks
1. **send_email_task** - Send emails asynchronously
2. **parse_resume_task** - Parse resume files
3. **calculate_ats_score_task** - Calculate ATS match scores
4. **cleanup_old_logs** - Clean old email logs (periodic)

### AI Call Tasks
5. **schedule_ai_call** - Schedule AI interview call
6. **execute_ai_call** - Execute AI interview with dynamic questions
7. **process_pending_ai_calls** - Process queued calls (periodic)

### Reminder Tasks
8. **scan_and_send_reminders** - Scan and send interview reminders (every 5 min)
9. **send_reminder_task** - Send individual reminder
10. **create_reminders_for_new_interview** - Create reminders for new interview

---

## Testing

### Test Files
- `core/tests.py` - Core functionality tests
- `core/tests_security.py` - Security tests
- `candidates/tests.py` - Candidate tests
- `employers/tests.py` - Employer tests

### Run Specific Tests
```bash
python manage.py test core.tests
python manage.py test candidates.tests
python manage.py test employers.tests
python manage.py test core.tests_security
```

### Run All Tests
```bash
.\run_tests.bat
```

---

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success message",
  "data": { },
  "errors": {}
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "data": null,
  "errors": {
    "field": ["Error detail"]
  }
}
```

### Paginated Response
```json
{
  "count": 100,
  "next": "?page=2",
  "previous": null,
  "page_size": 20,
  "total_pages": 5,
  "current_page": 1,
  "results": []
}
```

---

## Application Status Flow

```
pending → shortlisted → interview_scheduled → reviewed → accepted/rejected → selected
```

### Valid Transitions
- pending → shortlisted, rejected
- shortlisted → interview_scheduled, rejected
- interview_scheduled → reviewed, rejected
- reviewed → accepted, rejected
- accepted → selected

---

## ATS Scoring Algorithm

### Components (100 points total)
1. **Skills Match** (40 points)
   - Exact skill matches
   - Partial matches
   - Skill level assessment

2. **Experience Match** (30 points)
   - Years of experience
   - Relevant experience
   - Industry experience

3. **Salary Compatibility** (20 points)
   - Expected vs offered salary
   - Negotiation range

4. **Education Match** (10 points)
   - Degree level
   - Field of study
   - Certifications

---

## AI Interview Scoring

### Answer Evaluation Metrics
1. **Relevance Score** (0-100)
   - Answer relevance to question
   - Keyword matching

2. **Completeness Score** (0-100)
   - Answer depth
   - Coverage of key points

3. **Confidence Score** (0-100)
   - Speech clarity
   - Response time

4. **Overall Answer Score** (0-100)
   - Weighted average of above

### Session Scoring
- Category-wise scores
- Overall interview score
- Sentiment analysis
- Recommendation (interested/not interested)

---

## Security Middleware

### 1. SecurityHeadersMiddleware
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

### 2. RateLimitMiddleware
- API rate limiting
- IP-based throttling

### 3. RoleSecurityMiddleware
- Role-based access logging
- Suspicious activity detection

---

## Performance Features

### 1. Database Optimization
- Composite indexes
- select_related() for foreign keys
- prefetch_related() for many-to-many
- Query count monitoring

### 2. Caching
- Response caching
- Cache invalidation
- Redis backend

### 3. Pagination
- Standard pagination
- Infinite scroll support
- Configurable page size

---

## Postman Collection

Import the collection from:
```
postman/ZecPath_API_Collection.json
postman/ZecPath_Environment.json
```

### Pre-configured Requests
- All authentication flows
- CRUD operations
- Security tests
- Error scenarios

---

## License
MIT License - See LICENSE file

---

## Support
For issues and questions, contact the development team.

---

**Last Updated**: February 2024
**Version**: 1.0.0
**Django Version**: 6.0.1
**Python Version**: 3.10+
