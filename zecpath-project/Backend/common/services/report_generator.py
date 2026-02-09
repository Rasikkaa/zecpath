"""
Day 40 - AI Candidate Report Generator
"""
from core.models import Application
from core.ai_call_models import AICallQueue, AIInterviewSession
from django.utils import timezone


class CandidateReportGenerator:
    
    @staticmethod
    def generate_report(application_id):
        """Generate comprehensive candidate evaluation report"""
        try:
            application = Application.objects.select_related(
                'candidate__user', 'job__employer__user'
            ).get(id=application_id)
            
            # Aggregate all data
            ats_data = CandidateReportGenerator._get_ats_data(application)
            ai_data = CandidateReportGenerator._get_ai_interview_data(application)
            strengths, risks = CandidateReportGenerator._analyze_strengths_risks(application, ats_data, ai_data)
            recommendation = CandidateReportGenerator._generate_recommendation(ats_data, ai_data)
            
            report = {
                'report_id': f"RPT-{application.id}-{timezone.now().strftime('%Y%m%d')}",
                'generated_at': timezone.now().isoformat(),
                'candidate_info': {
                    'name': application.candidate.user.get_full_name(),
                    'email': application.candidate.user.email,
                    'experience_years': application.candidate.experience_years,
                    'expected_salary': application.candidate.expected_salary,
                    'skills': application.candidate.skills,
                },
                'job_info': {
                    'title': application.job.title,
                    'company': application.job.employer.company_name or 'N/A',
                    'applied_at': application.applied_at.isoformat(),
                },
                'ats_evaluation': ats_data,
                'ai_interview': ai_data,
                'analysis': {
                    'strengths': strengths,
                    'risks': risks,
                    'recommendation': recommendation,
                },
                'overall_rating': CandidateReportGenerator._calculate_overall_rating(ats_data, ai_data),
            }
            
            return report, None
            
        except Application.DoesNotExist:
            return None, 'Application not found'
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def _get_ats_data(application):
        """Extract ATS scoring data"""
        return {
            'match_score': application.match_score,
            'breakdown': application.match_breakdown,
            'status': application.status,
        }
    
    @staticmethod
    def _get_ai_interview_data(application):
        """Extract AI interview data"""
        try:
            call = AICallQueue.objects.filter(application=application).order_by('-created_at').first()
            if not call:
                return None
            
            session = getattr(call, 'session', None)
            if not session:
                return {
                    'status': call.status,
                    'scheduled_at': call.scheduled_at.isoformat() if call.scheduled_at else None,
                    'completed': False,
                }
            
            return {
                'status': call.status,
                'call_outcome': call.call_outcome,
                'sentiment_score': call.sentiment_score,
                'conversation_summary': call.conversation_summary,
                'overall_score': session.overall_score,
                'category_scores': session.category_scores,
                'total_questions': session.total_questions,
                'total_answers': session.total_answers,
                'call_duration': call.call_duration,
                'completed_at': call.completed_at.isoformat() if call.completed_at else None,
            }
        except Exception:
            return None
    
    @staticmethod
    def _analyze_strengths_risks(application, ats_data, ai_data):
        """Identify strengths and risks"""
        strengths = []
        risks = []
        
        # ATS-based analysis
        ats_score = ats_data.get('match_score') or 0
        if ats_score >= 80:
            strengths.append('Excellent ATS match score')
        elif ats_score < 50:
            risks.append('Low ATS match score')
        
        breakdown = ats_data.get('breakdown') or {}
        skills_score = breakdown.get('skills_score') or 0
        if skills_score >= 80:
            strengths.append('Strong technical skills match')
        elif skills_score < 50:
            risks.append('Skills gap identified')
        
        exp_score = breakdown.get('experience_score') or 0
        if exp_score >= 80:
            strengths.append('Relevant experience level')
        elif exp_score < 50:
            risks.append('Experience mismatch')
        
        # AI interview analysis
        if ai_data:
            overall_score = ai_data.get('overall_score') or 0
            if overall_score >= 80:
                strengths.append('Excellent interview performance')
            elif overall_score < 60:
                risks.append('Below average interview performance')
            
            sentiment = ai_data.get('sentiment_score') or 0
            if sentiment >= 0.7:
                strengths.append('Positive attitude and enthusiasm')
            elif sentiment < 0.4:
                risks.append('Low engagement or negative sentiment')
            
            if ai_data.get('call_outcome') == 'interested':
                strengths.append('Expressed strong interest in role')
            elif ai_data.get('call_outcome') == 'not_interested':
                risks.append('Candidate not interested')
            
            # Category-specific
            cat_scores = ai_data.get('category_scores') or {}
            for category, data in cat_scores.items():
                if isinstance(data, dict):
                    score = data.get('average_score') or 0
                    if score >= 85:
                        strengths.append(f'Strong {category} responses')
                    elif score < 60:
                        risks.append(f'Weak {category} responses')
        
        # Salary analysis
        candidate_salary = application.candidate.expected_salary
        job_max = application.job.salary_max
        if candidate_salary and job_max:
            if candidate_salary > job_max * 1.2:
                risks.append('Salary expectation significantly above budget')
            elif candidate_salary <= job_max:
                strengths.append('Salary expectation within budget')
        
        return strengths[:5], risks[:5]  # Limit to top 5 each
    
    @staticmethod
    def _generate_recommendation(ats_data, ai_data):
        """Generate hiring recommendation"""
        ats_score = ats_data.get('match_score') or 0
        ai_score = ai_data.get('overall_score') or 0 if ai_data else 0
        
        # Calculate weighted score
        if ai_data and ai_score > 0:
            combined_score = (ats_score * 0.4) + (ai_score * 0.6)
        else:
            combined_score = ats_score
        
        if combined_score >= 80:
            return {
                'action': 'Strong Hire',
                'priority': 'High',
                'next_steps': 'Schedule in-person interview immediately',
            }
        elif combined_score >= 70:
            return {
                'action': 'Hire',
                'priority': 'Medium',
                'next_steps': 'Proceed with technical assessment',
            }
        elif combined_score >= 60:
            return {
                'action': 'Consider',
                'priority': 'Low',
                'next_steps': 'Review with hiring manager',
            }
        else:
            return {
                'action': 'Reject',
                'priority': 'N/A',
                'next_steps': 'Send rejection email',
            }
    
    @staticmethod
    def _calculate_overall_rating(ats_data, ai_data):
        """Calculate overall candidate rating"""
        ats_score = ats_data.get('match_score') or 0
        ai_score = ai_data.get('overall_score') or 0 if ai_data else 0
        
        if ai_data and ai_score > 0:
            overall = (ats_score * 0.4) + (ai_score * 0.6)
        else:
            overall = ats_score
        
        if overall >= 85:
            rating = 'Excellent'
        elif overall >= 75:
            rating = 'Good'
        elif overall >= 65:
            rating = 'Average'
        else:
            rating = 'Below Average'
        
        return {
            'score': round(overall, 1),
            'rating': rating,
            'ats_weight': 40 if ai_data and ai_score > 0 else 100,
            'ai_weight': 60 if ai_data and ai_score > 0 else 0,
        }
