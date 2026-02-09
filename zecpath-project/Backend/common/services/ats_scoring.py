class ATSScoring:
    """ATS Scoring Engine for candidate-job matching"""
    
    # Weights for scoring categories
    WEIGHTS = {
        'skills': 0.40,      # 40%
        'experience': 0.30,  # 30%
        'education': 0.20,   # 20%
        'salary': 0.10       # 10%
    }
    
    @staticmethod
    def calculate_match_score(candidate, job):
        """Calculate overall match score (0-100) and breakdown"""
        skills_score = ATSScoring._score_skills(candidate, job)
        experience_score = ATSScoring._score_experience(candidate, job)
        education_score = ATSScoring._score_education(candidate, job)
        salary_score = ATSScoring._score_salary(candidate, job)
        
        # Calculate weighted total
        total_score = (
            skills_score * ATSScoring.WEIGHTS['skills'] +
            experience_score * ATSScoring.WEIGHTS['experience'] +
            education_score * ATSScoring.WEIGHTS['education'] +
            salary_score * ATSScoring.WEIGHTS['salary']
        )
        
        breakdown = {
            'skills_score': round(skills_score, 2),
            'experience_score': round(experience_score, 2),
            'education_score': round(education_score, 2),
            'salary_score': round(salary_score, 2),
            'skills_matched': [],
            'skills_missing': []
        }
        
        return round(total_score, 2), breakdown
    
    @staticmethod
    def _score_skills(candidate, job):
        """Score skills match (0-100)"""
        candidate_skills = candidate.skills if isinstance(candidate.skills, list) else []
        job_skills = job.skills if isinstance(job.skills, list) else []
        
        if not job_skills:
            return 100  # No requirements = full score
        
        if not candidate_skills:
            return 0
        
        # Normalize to lowercase for comparison
        candidate_skills_lower = [s.lower().strip() for s in candidate_skills]
        job_skills_lower = [s.lower().strip() for s in job_skills]
        
        matched = sum(1 for skill in job_skills_lower if skill in candidate_skills_lower)
        score = (matched / len(job_skills_lower)) * 100
        
        return min(100, score)
    
    @staticmethod
    def _score_experience(candidate, job):
        """Score experience match (0-100)"""
        candidate_exp = candidate.experience_years or 0
        
        # Extract required years from job.experience field
        job_exp = ATSScoring._extract_years_from_text(job.experience)
        
        if job_exp is None:
            return 100  # No requirement = full score
        
        if candidate_exp >= job_exp:
            return 100
        elif candidate_exp >= job_exp * 0.8:  # Within 80%
            return 80
        elif candidate_exp >= job_exp * 0.6:  # Within 60%
            return 60
        elif candidate_exp >= job_exp * 0.4:  # Within 40%
            return 40
        else:
            return 20
    
    @staticmethod
    def _score_education(candidate, job):
        """Score education relevance (0-100)"""
        # Basic scoring: has education = 100, no education = 50
        if candidate.education and candidate.education.strip():
            return 100
        return 50
    
    @staticmethod
    def _score_salary(candidate, job):
        """Score salary expectation match (0-100)"""
        if not candidate.expected_salary:
            return 100  # No expectation = full score
        
        if not job.salary_max:
            return 100  # No max = full score
        
        if candidate.expected_salary <= job.salary_max:
            return 100
        elif candidate.expected_salary <= job.salary_max * 1.1:  # Within 10%
            return 80
        elif candidate.expected_salary <= job.salary_max * 1.2:  # Within 20%
            return 60
        else:
            return 30
    
    @staticmethod
    def _extract_years_from_text(text):
        """Extract years from experience text"""
        if not text:
            return None
        
        import re
        match = re.search(r'(\d+)', str(text))
        return int(match.group(1)) if match else None
